"""Bulk AI function execution CLI."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Iterable, List, Sequence, Set

from dataset_config import get_dataset_config
from db import get_db
from services.resolver import get_resolver
from tqdm.asyncio import tqdm_asyncio

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path(__file__).resolve().parent / "_cache"


def chunked(values: Sequence[str], size: int) -> Iterable[List[str]]:
    """Yield fixed-size chunks from a sequence."""
    if size <= 0:
        raise ValueError("batch size must be positive")
    for start in range(0, len(values), size):
        yield list(values[start : start + size])


class CacheManager:
    """Persist processed IDs so interrupted runs can resume."""

    def __init__(self, cache_path: Path, dataset: str, ai_function: str, refresh: bool):
        self.cache_path = cache_path
        self.dataset = dataset
        self.ai_function = ai_function
        self.refresh = refresh
        self.processed: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if not self.cache_path.exists():
            return
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to read cache %s: %s", self.cache_path, exc)
            return
        if (
            data.get("dataset") == self.dataset
            and data.get("ai_function") == self.ai_function
            and data.get("refresh") == self.refresh
        ):
            self.processed = set(data.get("processed_ids", []))
        else:
            logger.info("Ignoring cache %s due to configuration mismatch", self.cache_path)

    def mark(self, identifier: str) -> None:
        self.processed.add(identifier)

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dataset": self.dataset,
            "ai_function": self.ai_function,
            "refresh": self.refresh,
            "processed_ids": sorted(self.processed),
        }
        temp_path = self.cache_path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_path.replace(self.cache_path)

    def clear(self) -> None:
        if self.cache_path.exists():
            self.cache_path.unlink()


async def _process_single(
    resolver,
    dataset: str,
    ai_function: str,
    identifier: str,
    session_id: str,
    refresh: bool,
) -> bool:
    try:
        resolver.resolve(
            dataset=dataset,
            func=ai_function,
            id=identifier,
            session_id=session_id,
            refresh=refresh,
        )
    except Exception as exc:  # pragma: no cover - logging side-effect
        logger.error("Failed to process %s/%s for %s: %s", dataset, ai_function, identifier, exc)
        return False
    await asyncio.sleep(0)  # allow scheduling for future async workloads
    return True


async def run_bulk_process(
    dataset: str,
    ai_function: str,
    batch_size: int,
    session_id: str,
    refresh: bool,
    cache_dir: Path,
) -> None:
    config = get_dataset_config(dataset)
    if ai_function not in config.ai_functions:
        valid = ", ".join(config.ai_functions)
        raise ValueError(f"Invalid ai_function '{ai_function}'. Valid options: {valid}")

    db = get_db()
    resolver = get_resolver()

    key_field = config.key_field
    id_rows = db.fetchall(f"SELECT {key_field} FROM {config.table} ORDER BY {key_field}")
    all_ids = [row[0] for row in id_rows]

    if not all_ids:
        print(f"No records found for dataset '{dataset}'.")
        return

    cache_path = cache_dir / f"{dataset}_{ai_function}.json"
    cache = CacheManager(cache_path, dataset, ai_function, refresh)

    if refresh:
        candidate_ids = list(all_ids)
    else:
        table_name = f"{dataset}_{ai_function}"
        existing_rows = db.fetchall(f"SELECT {key_field} FROM {table_name}")
        computed_ids = {row[0] for row in existing_rows}
        candidate_ids = [identifier for identifier in all_ids if identifier not in computed_ids]

    pending_ids = [identifier for identifier in candidate_ids if identifier not in cache.processed]
    already_done = len(all_ids) - len(candidate_ids)
    resumed = sum(1 for identifier in candidate_ids if identifier in cache.processed)
    initial_progress = already_done + resumed

    if not pending_ids:
        if cache.processed:
            cache.clear()
        print(f"Nothing to process for dataset '{dataset}' and function '{ai_function}'.")
        return

    progress = tqdm_asyncio(
        total=len(all_ids),
        initial=initial_progress,
        desc=f"{dataset}:{ai_function}",
        unit="record",
    )

    failures: List[str] = []
    try:
        for batch in chunked(pending_ids, batch_size):
            for identifier in batch:
                success = await _process_single(
                    resolver,
                    dataset,
                    ai_function,
                    identifier,
                    session_id,
                    refresh,
                )
                if success:
                    cache.mark(identifier)
                else:
                    failures.append(identifier)
                progress.update(1)
            cache.save()
    except BaseException:
        cache.save()
        raise
    finally:
        progress.close()

    if failures:
        print(f"Completed with {len(failures)} failures. See logs for details.")
    else:
        cache.clear()
        print("Bulk processing completed successfully.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI function across a dataset.")
    parser.add_argument("dataset", help="Dataset name (e.g. issues, controls).")
    parser.add_argument("ai_function", help="AI function to execute (see dataset configuration).")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=25,
        help="Number of records to process per batch.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Recompute even if cached data exists.",
    )
    parser.add_argument(
        "--session-id",
        default="bulk-cli-session",
        help="Session identifier to forward to mock AI functions.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help="Directory for progress cache files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(
            run_bulk_process(
                dataset=args.dataset,
                ai_function=args.ai_function,
                batch_size=args.batch_size,
                session_id=args.session_id,
                refresh=args.refresh,
                cache_dir=args.cache_dir,
            )
        )
    except ValueError as exc:
        print(str(exc))
    except KeyboardInterrupt:
        print("\nInterrupted by user.")


if __name__ == "__main__":
    main()
