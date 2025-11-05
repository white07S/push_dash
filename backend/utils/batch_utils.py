"""Batch utilities for bulk processing of AI functions and data operations."""
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from db import get_db
from dataset_config import get_dataset_config

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handle batch processing for AI functions and bulk operations."""

    def __init__(self, max_workers: int = 4, batch_size: int = 100):
        """Initialize batch processor."""
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.db = get_db()

    def batch_compute_ai_function(
        self,
        dataset: str,
        function_name: str,
        compute_func: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        ids: Optional[List[str]] = None,
        force_recompute: bool = False,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Batch compute an AI function for multiple IDs."""
        config = get_dataset_config(dataset)
        key_field = config.key_field
        table_name = config.table

        # Get IDs to process
        if ids is None:
            query = f"SELECT {key_field}, raw_data, title, category, risk_theme, risk_subtheme FROM {table_name}"
            rows = self.db.fetchall(query)
            ids_to_process = []
            for row in rows:
                raw_record = json.loads(row[1]) if row[1] else {
                    key_field: row[0],
                    "title": row[2],
                    "category": row[3],
                    "risk_theme": row[4],
                    "risk_subtheme": row[5],
                }
                ids_to_process.append((row[0], raw_record))
        else:
            ids_to_process = []
            for id_val in ids:
                query = f"SELECT raw_data, title, category, risk_theme, risk_subtheme FROM {table_name} WHERE {key_field} = ?"
                result = self.db.fetchone(query, (id_val,))
                if result:
                    raw_data_json, title, category, risk_theme, risk_subtheme = result
                    raw_record = json.loads(raw_data_json) if raw_data_json else {
                        key_field: id_val,
                        "title": title,
                        "category": category,
                        "risk_theme": risk_theme,
                        "risk_subtheme": risk_subtheme,
                    }
                    ids_to_process.append((id_val, raw_record))

        # Filter out already computed if not forcing recompute
        if not force_recompute:
            filtered_ids: List[Tuple[str, Dict[str, Any]]] = []
            ai_table = f"{dataset}_{function_name}"
            for id_val, record in ids_to_process:
                query = f"SELECT 1 FROM {ai_table} WHERE {key_field} = ?"
                result = self.db.fetchone(query, (id_val,))
                if not result:
                    filtered_ids.append((id_val, record))
            ids_to_process = filtered_ids

        if not ids_to_process:
            return {
                "status": "success",
                "message": "No items to process",
                "processed": 0,
                "successful": 0,
                "failed": 0,
            }

        # Process in batches
        results: Dict[str, Any] = {
            "status": "processing",
            "total": len(ids_to_process),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i in range(0, len(ids_to_process), self.batch_size):
                batch = ids_to_process[i : i + self.batch_size]
                future = executor.submit(
                    self._process_batch,
                    dataset,
                    function_name,
                    compute_func,
                    batch,
                    key_field,
                )
                futures.append(future)

            for future in as_completed(futures):
                try:
                    batch_result = future.result()
                    results["processed"] += batch_result["processed"]
                    results["successful"] += batch_result["successful"]
                    results["failed"] += batch_result["failed"]
                    results["errors"].extend(batch_result.get("errors", [])[:10])

                    if progress_callback:
                        progress_callback(results)
                except Exception as exc:  # pragma: no cover - logging side-effect
                    logger.error("Batch processing error: %s", exc)
                    results["errors"].append(str(exc))

        elapsed_time = time.time() - start_time
        results["status"] = "completed"
        results["elapsed_time"] = f"{elapsed_time:.2f}s"
        results["rate"] = (
            f"{results['processed'] / elapsed_time:.1f} items/sec"
            if elapsed_time > 0
            else "N/A"
        )

        return results

    def _process_batch(
        self,
        dataset: str,
        function_name: str,
        compute_func: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        batch: List[Tuple[str, Dict[str, Any]]],
        key_field: str,
    ) -> Dict[str, Any]:
        """Process a single batch of items."""
        batch_results: Dict[str, Any] = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

        ai_table = f"{dataset}_{function_name}"

        for id_val, raw_record in batch:
            try:
                result = compute_func(id_val, raw_record)
                query = f"""
                    INSERT OR REPLACE INTO {ai_table}
                    ({key_field}, payload, created_at)
                    VALUES (?, ?, ?)
                """
                self.db.execute(
                    query,
                    (id_val, json.dumps(result), datetime.utcnow().isoformat() + "Z"),
                )
                batch_results["successful"] += 1
            except Exception as exc:  # pragma: no cover - logging side-effect
                logger.error("Error processing %s: %s", id_val, exc)
                batch_results["failed"] += 1
                batch_results["errors"].append(f"{id_val}: {exc}")
            finally:
                batch_results["processed"] += 1

        return batch_results

    def batch_delete(
        self,
        dataset: str,
        ids: List[str],
        cascade: bool = True
    ) -> Dict[str, Any]:
        """Batch delete items from a dataset."""
        config = get_dataset_config(dataset)
        key_field = config.key_field

        results = {
            "deleted": 0,
            "failed": 0,
            "errors": [],
        }

        tables_to_clean = [config.table]

        if cascade:
            tables_to_clean.extend(f"{dataset}_{func}" for func in config.ai_functions)

        for id_val in ids:
            try:
                for table in tables_to_clean:
                    query = f"DELETE FROM {table} WHERE {key_field} = ?"
                    self.db.execute(query, (id_val,))
                results["deleted"] += 1
            except Exception as exc:  # pragma: no cover - logging side-effect
                logger.error("Error deleting %s: %s", id_val, exc)
                results["failed"] += 1
                results["errors"].append(f"{id_val}: {exc}")

        return results

    def batch_export(
        self,
        dataset: str,
        output_format: str = "json",
        include_ai_results: bool = True,
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Batch export dataset with optional AI results."""
        config = get_dataset_config(dataset)
        key_field = config.key_field
        table_name = config.table

        if ids:
            placeholders = ",".join("?" for _ in ids)
            query = f"""
                SELECT {key_field}, title, category, risk_theme, risk_subtheme, raw_data
                FROM {table_name}
                WHERE {key_field} IN ({placeholders})
            """
            rows = self.db.fetchall(query, tuple(ids))
        else:
            query = f"""
                SELECT {key_field}, title, category, risk_theme, risk_subtheme, raw_data
                FROM {table_name}
            """
            rows = self.db.fetchall(query)

        export_data: List[Dict[str, Any]] = []

        for row in rows:
            item: Dict[str, Any] = {
                key_field: row[0],
                "title": row[1],
                "category": row[2],
                "risk_theme": row[3],
                "risk_subtheme": row[4],
                "raw_data": json.loads(row[5]) if row[5] else {},
            }

            if include_ai_results:
                item["ai_results"] = {}
                for func in config.ai_functions:
                    table = f"{dataset}_{func}"
                    ai_query = f"""
                        SELECT payload, created_at
                        FROM {table}
                        WHERE {key_field} = ?
                    """
                    ai_result = self.db.fetchone(ai_query, (row[0],))
                    if ai_result:
                        item["ai_results"][func] = {
                            "payload": json.loads(ai_result[0]),
                            "created_at": ai_result[1],
                        }

            export_data.append(item)

        results: Dict[str, Any] = {
            "status": "success",
            "dataset": dataset,
            "count": len(export_data),
            "format": output_format,
            "data": export_data,
        }

        if output_format == "csv":
            import pandas as pd  # Local import to avoid dependency at import time

            df = pd.DataFrame(export_data)

            if include_ai_results and "ai_results" in df.columns:
                for func in config.ai_functions:
                    df[f"{func}_present"] = df["ai_results"].apply(
                        lambda x, fn=func: fn in x if isinstance(x, dict) else False
                    )
                df = df.drop("ai_results", axis=1)

            if "raw_data" in df.columns:
                df = df.drop("raw_data", axis=1)

            results["data"] = df.to_dict("records")

        return results

    def get_batch_status(self, dataset: str) -> Dict[str, Any]:
        """Get batch processing status for a dataset."""
        config = get_dataset_config(dataset)
        key_field = config.key_field

        total_query = f"SELECT COUNT(*) FROM {config.table}"
        total_row = self.db.fetchone(total_query)
        total = total_row[0] if total_row else 0

        ai_status: Dict[str, Dict[str, Any]] = {}
        for func in config.ai_functions:
            table_name = f"{dataset}_{func}"
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            try:
                count = self.db.fetchone(count_query)[0]
            except Exception:  # pragma: no cover - defensive
                count = 0

            ai_status[func] = {
                "computed": count,
                "pending": max(total - count, 0),
                "percentage": f"{(count / total * 100):.1f}%" if total > 0 else "0%",
            }

        return {
            "dataset": dataset,
            "key_field": key_field,
            "total_items": total,
            "ai_functions": ai_status,
        }
