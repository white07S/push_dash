"""Batch utilities for bulk processing of AI functions and data operations."""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from db import get_db

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Handle batch processing for AI functions and bulk operations."""

    def __init__(self, max_workers: int = 4, batch_size: int = 100):
        """Initialize batch processor.

        Args:
            max_workers: Maximum number of concurrent workers
            batch_size: Number of items to process in each batch
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.db = get_db()

    def batch_compute_ai_function(
        self,
        dataset: str,
        function_name: str,
        compute_func: Callable,
        ids: Optional[List[str]] = None,
        force_recompute: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Batch compute AI function for multiple IDs.

        Args:
            dataset: Dataset name (controls, external_loss, internal_loss, issues)
            function_name: AI function name (ai_taxonomy, ai_root_causes, etc.)
            compute_func: Function to compute AI result for a single ID
            ids: List of IDs to process (if None, process all)
            force_recompute: Force recomputation even if cached
            progress_callback: Callback function to report progress

        Returns:
            Dictionary with processing results
        """
        # Get dataset configuration
        key_fields = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

        if dataset not in key_fields:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = key_fields[dataset]

        # Get IDs to process
        if ids is None:
            # Get all IDs from raw table
            query = f"SELECT {key_field}, description FROM {dataset}_raw"
            rows = self.db.fetchall(query)
            ids_to_process = [(row[0], row[1]) for row in rows]
        else:
            # Get descriptions for provided IDs
            ids_to_process = []
            for id_val in ids:
                query = f"SELECT description FROM {dataset}_raw WHERE {key_field} = ?"
                result = self.db.fetchone(query, (id_val,))
                if result:
                    ids_to_process.append((id_val, result[0]))

        # Filter out already computed if not forcing recompute
        if not force_recompute:
            filtered_ids = []
            table_name = f"{dataset}_{function_name}"
            for id_val, desc in ids_to_process:
                query = f"SELECT 1 FROM {table_name} WHERE {key_field} = ?"
                result = self.db.fetchone(query, (id_val,))
                if not result:
                    filtered_ids.append((id_val, desc))
            ids_to_process = filtered_ids

        if not ids_to_process:
            return {
                'status': 'success',
                'message': 'No items to process',
                'processed': 0,
                'successful': 0,
                'failed': 0
            }

        # Process in batches
        results = {
            'status': 'processing',
            'total': len(ids_to_process),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks in batches
            futures = []
            for i in range(0, len(ids_to_process), self.batch_size):
                batch = ids_to_process[i:i + self.batch_size]
                future = executor.submit(
                    self._process_batch,
                    dataset,
                    function_name,
                    compute_func,
                    batch,
                    key_field
                )
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    batch_result = future.result()
                    results['processed'] += batch_result['processed']
                    results['successful'] += batch_result['successful']
                    results['failed'] += batch_result['failed']
                    results['errors'].extend(batch_result.get('errors', [])[:10])

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(results)

                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
                    results['errors'].append(str(e))

        # Final results
        elapsed_time = time.time() - start_time
        results['status'] = 'completed'
        results['elapsed_time'] = f"{elapsed_time:.2f}s"
        results['rate'] = f"{results['processed'] / elapsed_time:.1f} items/sec" if elapsed_time > 0 else "N/A"

        return results

    def _process_batch(
        self,
        dataset: str,
        function_name: str,
        compute_func: Callable,
        batch: List[Tuple[str, str]],
        key_field: str
    ) -> Dict[str, Any]:
        """Process a single batch of items."""
        batch_results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        table_name = f"{dataset}_{function_name}"

        for id_val, description in batch:
            try:
                # Compute AI function result
                result = compute_func(id_val, description)

                # Store result in database
                query = f'''
                    INSERT OR REPLACE INTO {table_name}
                    ({key_field}, payload, created_at)
                    VALUES (?, ?, ?)
                '''

                self.db.execute(
                    query,
                    (id_val, json.dumps(result), datetime.utcnow().isoformat() + 'Z')
                )

                batch_results['successful'] += 1

            except Exception as e:
                logger.error(f"Error processing {id_val}: {e}")
                batch_results['failed'] += 1
                batch_results['errors'].append(f"{id_val}: {str(e)}")

            batch_results['processed'] += 1

        # Commit batch
        # APSW is in autocommit mode by default, no commit needed

        return batch_results

    def batch_update_taxonomy(
        self,
        dataset: str,
        taxonomy_updates: Dict[str, str],
        validate: bool = True
    ) -> Dict[str, Any]:
        """Batch update NFR taxonomy for multiple items.

        Args:
            dataset: Dataset name
            taxonomy_updates: Dictionary mapping ID to new taxonomy value
            validate: Whether to validate taxonomy values

        Returns:
            Update results
        """
        key_fields = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

        if dataset not in key_fields:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = key_fields[dataset]
        table_name = f"{dataset}_raw"
        taxonomy_table = f"{dataset}_taxonomy_map"

        results = {
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        for id_val, taxonomy_str in taxonomy_updates.items():
            try:
                # Normalize taxonomy
                from utils.taxonomy import normalize_taxonomy
                normalized = normalize_taxonomy(taxonomy_str)

                # Update raw table
                query = f'''
                    UPDATE {table_name}
                    SET nfr_taxonomy = ?
                    WHERE {key_field} = ?
                '''
                self.db.execute(query, (normalized, id_val))

                # Update taxonomy map table
                # First delete existing mappings
                delete_query = f"DELETE FROM {taxonomy_table} WHERE {key_field} = ?"
                self.db.execute(delete_query, (id_val,))

                # Insert new mappings
                if normalized:
                    tokens = normalized.split('|')
                    insert_data = [(id_val, token) for token in tokens if token]
                    insert_query = f'''
                        INSERT INTO {taxonomy_table} ({key_field}, taxonomy_token)
                        VALUES (?, ?)
                    '''
                    self.db.executemany(insert_query, insert_data)

                results['updated'] += 1

            except Exception as e:
                logger.error(f"Error updating taxonomy for {id_val}: {e}")
                results['failed'] += 1
                results['errors'].append(f"{id_val}: {str(e)}")

        # APSW is in autocommit mode by default, no commit needed
        return results

    def batch_delete(
        self,
        dataset: str,
        ids: List[str],
        cascade: bool = True
    ) -> Dict[str, Any]:
        """Batch delete items from dataset.

        Args:
            dataset: Dataset name
            ids: List of IDs to delete
            cascade: Whether to delete related AI function results

        Returns:
            Deletion results
        """
        key_fields = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

        if dataset not in key_fields:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = key_fields[dataset]

        results = {
            'deleted': 0,
            'failed': 0,
            'errors': []
        }

        tables_to_clean = [f"{dataset}_raw"]

        if cascade:
            # Add AI function tables
            ai_functions = ['ai_taxonomy', 'ai_root_causes', 'ai_enrichment']
            if dataset == 'controls':
                ai_functions.append('similar_controls')
            else:
                ai_functions.append(f'similar_{dataset}')

            for func in ai_functions:
                tables_to_clean.append(f"{dataset}_{func}")

            # Add taxonomy map table
            tables_to_clean.append(f"{dataset}_taxonomy_map")

        for id_val in ids:
            try:
                for table in tables_to_clean:
                    query = f"DELETE FROM {table} WHERE {key_field} = ?"
                    self.db.execute(query, (id_val,))

                results['deleted'] += 1

            except Exception as e:
                logger.error(f"Error deleting {id_val}: {e}")
                results['failed'] += 1
                results['errors'].append(f"{id_val}: {str(e)}")

        # APSW is in autocommit mode by default, no commit needed
        return results

    def batch_export(
        self,
        dataset: str,
        output_format: str = 'json',
        include_ai_results: bool = True,
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Batch export dataset with optional AI results.

        Args:
            dataset: Dataset name
            output_format: Export format (json, csv)
            include_ai_results: Whether to include AI function results
            ids: Specific IDs to export (None for all)

        Returns:
            Export results with data
        """
        key_fields = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

        if dataset not in key_fields:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = key_fields[dataset]

        # Build query
        if ids:
            placeholders = ','.join(['?' for _ in ids])
            query = f'''
                SELECT {key_field}, description, nfr_taxonomy, raw_data
                FROM {dataset}_raw
                WHERE {key_field} IN ({placeholders})
            '''
            rows = self.db.fetchall(query, tuple(ids))
        else:
            query = f'''
                SELECT {key_field}, description, nfr_taxonomy, raw_data
                FROM {dataset}_raw
            '''
            rows = self.db.fetchall(query)

        export_data = []

        for row in rows:
            item = {
                key_field: row[0],
                'description': row[1],
                'nfr_taxonomy': row[2],
                'raw_data': json.loads(row[3]) if row[3] else {}
            }

            if include_ai_results:
                # Add AI function results
                ai_functions = ['ai_taxonomy', 'ai_root_causes', 'ai_enrichment']
                if dataset == 'controls':
                    ai_functions.append('similar_controls')
                else:
                    ai_functions.append(f'similar_{dataset}')

                item['ai_results'] = {}

                for func in ai_functions:
                    table_name = f"{dataset}_{func}"
                    ai_query = f'''
                        SELECT payload, created_at
                        FROM {table_name}
                        WHERE {key_field} = ?
                    '''
                    ai_result = self.db.fetchone(ai_query, (row[0],))

                    if ai_result:
                        item['ai_results'][func] = {
                            'payload': json.loads(ai_result[0]),
                            'created_at': ai_result[1]
                        }

            export_data.append(item)

        results = {
            'status': 'success',
            'dataset': dataset,
            'count': len(export_data),
            'format': output_format,
            'data': export_data
        }

        if output_format == 'csv':
            # Convert to CSV format (flatten structure)
            import pandas as pd
            df = pd.DataFrame(export_data)

            # Flatten nested structures for CSV
            if include_ai_results and 'ai_results' in df.columns:
                # Add AI result columns
                for func in ['ai_taxonomy', 'ai_root_causes', 'ai_enrichment']:
                    df[f'{func}_present'] = df['ai_results'].apply(
                        lambda x: func in x if x else False
                    )
                df = df.drop('ai_results', axis=1)

            if 'raw_data' in df.columns:
                df = df.drop('raw_data', axis=1)

            results['data'] = df.to_dict('records')

        return results

    def get_batch_status(self, dataset: str) -> Dict[str, Any]:
        """Get batch processing status for a dataset.

        Args:
            dataset: Dataset name

        Returns:
            Status information
        """
        key_fields = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

        if dataset not in key_fields:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = key_fields[dataset]

        # Get total count
        total_query = f"SELECT COUNT(*) FROM {dataset}_raw"
        total = self.db.fetchone(total_query)[0]

        # Get AI function counts
        ai_functions = ['ai_taxonomy', 'ai_root_causes', 'ai_enrichment']
        if dataset == 'controls':
            ai_functions.append('similar_controls')
        else:
            ai_functions.append(f'similar_{dataset}')

        ai_status = {}
        for func in ai_functions:
            table_name = f"{dataset}_{func}"
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            try:
                count = self.db.fetchone(count_query)[0]
                ai_status[func] = {
                    'computed': count,
                    'pending': total - count,
                    'percentage': f"{(count / total * 100):.1f}%" if total > 0 else "0%"
                }
            except:
                ai_status[func] = {
                    'computed': 0,
                    'pending': total,
                    'percentage': "0%"
                }

        return {
            'dataset': dataset,
            'total_items': total,
            'ai_functions': ai_status
        }