"""CLI for exporting AI outputs into CSV."""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

from dataset_config import get_dataset_config
from db import get_db
from tqdm.asyncio import tqdm_asyncio


async def export_ai_data(
    dataset: str,
    ai_function: str,
    input_csv: Path,
    output_csv: Path,
) -> Tuple[int, int]:
    config = get_dataset_config(dataset)
    if ai_function not in config.ai_functions:
        valid = ", ".join(config.ai_functions)
        raise ValueError(f"Invalid ai_function '{ai_function}'. Valid options: {valid}")

    key_field = config.key_field
    db = get_db()
    table_name = f"{dataset}_{ai_function}"

    with input_csv.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows: List[Dict[str, str]] = list(reader)
        if reader.fieldnames is None:
            raise ValueError("Input CSV must have a header row.")
        fieldnames = list(reader.fieldnames)

    if ai_function not in fieldnames:
        fieldnames.append(ai_function)

    if not rows:
        with output_csv.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
        return 0, 0

    progress = tqdm_asyncio(
        total=len(rows),
        desc=f"Export {dataset}:{ai_function}",
        unit="row",
    )

    missing = 0
    try:
        with output_csv.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                identifier = (row.get(key_field) or "").strip()
                if identifier:
                    record = db.get_json(table_name, key_field, identifier)
                    if record:
                        row[ai_function] = json.dumps(record["payload"])
                    else:
                        row[ai_function] = ""
                        missing += 1
                else:
                    row[ai_function] = ""
                    missing += 1
                writer.writerow(row)
                progress.update(1)
                await asyncio.sleep(0)
    finally:
        progress.close()

    return len(rows), missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export cached AI outputs to CSV.")
    parser.add_argument("dataset", help="Dataset name (e.g. issues, controls).")
    parser.add_argument("ai_function", help="AI function name to export.")
    parser.add_argument("input_csv", type=Path, help="Input CSV file with dataset keys.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output CSV path (defaults to <input>_<ai_function>.csv).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_csv: Path = args.input_csv
    if not input_csv.exists():
        print(f"Input file '{input_csv}' not found.")
        return

    output_csv: Path
    if args.output:
        output_csv = args.output
    else:
        output_csv = input_csv.with_name(f"{input_csv.stem}_{args.ai_function}{input_csv.suffix}")

    try:
        total, missing = asyncio.run(
            export_ai_data(
                dataset=args.dataset,
                ai_function=args.ai_function,
                input_csv=input_csv,
                output_csv=output_csv,
            )
        )
    except ValueError as exc:
        print(str(exc))
        return
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return

    print(f"Wrote {total} rows to '{output_csv}'.")
    if missing:
        print(f"{missing} rows were missing data for '{args.ai_function}'.")


if __name__ == "__main__":
    main()
