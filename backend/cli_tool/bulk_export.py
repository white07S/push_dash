"""CLI for exporting AI outputs into CSV."""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dataset_config import get_dataset_config
from db import get_db
from tqdm.asyncio import tqdm_asyncio


def _hydrate_record(config, row: Tuple[Any, ...]) -> Tuple[str, Dict[str, Any]]:
    """Convert a dataset row into a serializable record dictionary."""
    (
        identifier,
        title,
        category,
        risk_theme,
        risk_subtheme,
        raw_data_json,
    ) = row

    record_data: Dict[str, Any] = {}
    if raw_data_json:
        try:
            parsed = json.loads(raw_data_json)
            if isinstance(parsed, dict):
                record_data.update(parsed)
            else:
                record_data["raw_data"] = parsed
        except json.JSONDecodeError:
            record_data["raw_data"] = raw_data_json

    # Ensure core fields are always present
    record_data.setdefault(config.key_field, identifier)
    record_data.setdefault(config.title_field, title or "")
    if config.category_field:
        record_data.setdefault(config.category_field, category or "")
    record_data.setdefault(config.theme_field, risk_theme or "")
    if config.subtheme_field:
        record_data.setdefault(config.subtheme_field, risk_subtheme or "")

    # Preserve generic aliases for convenience
    record_data.setdefault("title", title or "")
    record_data.setdefault("category", category or "")
    record_data.setdefault("risk_theme", risk_theme or "")
    record_data.setdefault("risk_subtheme", risk_subtheme or "")

    return identifier, record_data


def _serialize_for_csv(value: Any) -> str:
    """Convert complex values into CSV-friendly strings."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


async def export_ai_data(
    dataset: str,
    ai_function: str,
    output_csv: Path | None = None,
) -> Tuple[Path, int, int]:
    config = get_dataset_config(dataset)
    if ai_function not in config.ai_functions:
        valid = ", ".join(config.ai_functions)
        raise ValueError(f"Invalid ai_function '{ai_function}'. Valid options: {valid}")

    db = get_db()
    results_table = f"{dataset}_{ai_function}"

    dataset_rows = db.fetchall(
        f"""
        SELECT {config.key_field}, title, category, risk_theme, risk_subtheme, raw_data
        FROM {config.table}
        ORDER BY {config.key_field}
        """
    )

    if output_csv is None:
        output_csv = Path(f"{dataset}_{ai_function}_export.csv")
    output_csv = output_csv.expanduser().resolve()
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if not dataset_rows:
        base_fields = [config.key_field]
        for field in (
            config.title_field,
            config.category_field,
            config.theme_field,
            config.subtheme_field,
        ):
            if field and field not in base_fields:
                base_fields.append(field)
        writer_fields = base_fields + [ai_function]
        with output_csv.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=writer_fields)
            writer.writeheader()
        return output_csv, 0, 0

    field_order: List[str] = []
    seen_fields: set[str] = set()

    def register_field(field: str) -> None:
        if field not in seen_fields:
            seen_fields.add(field)
            field_order.append(field)

    # Ensure deterministic ordering for high-signal fields first
    register_field(config.key_field)
    for field in (
        config.title_field,
        config.category_field,
        config.theme_field,
        config.subtheme_field,
        "title",
        "category",
        "risk_theme",
        "risk_subtheme",
    ):
        if field:
            register_field(field)

    records: List[Tuple[str, Dict[str, Any]]] = []
    for row in dataset_rows:
        identifier, record = _hydrate_record(config, row)
        records.append((identifier, record))
        for key in record.keys():
            register_field(key)

    writer_fields = list(field_order)
    if ai_function not in seen_fields:
        writer_fields.append(ai_function)

    progress = tqdm_asyncio(
        total=len(records),
        desc=f"Export {dataset}:{ai_function}",
        unit="row",
    )

    missing = 0
    try:
        with output_csv.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=writer_fields)
            writer.writeheader()

            for identifier, record in records:
                row_payload: Dict[str, str] = {}
                for field in writer_fields:
                    if field == ai_function:
                        continue
                    row_payload[field] = _serialize_for_csv(record.get(field))

                computed = db.get_json(results_table, config.key_field, identifier)
                if computed:
                    row_payload[ai_function] = json.dumps(computed["payload"], ensure_ascii=False)
                else:
                    row_payload[ai_function] = ""
                    missing += 1

                writer.writerow(row_payload)
                progress.update(1)
                await asyncio.sleep(0)
    finally:
        progress.close()

    return output_csv, len(records), missing


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export cached AI outputs to CSV.")
    parser.add_argument("dataset", help="Dataset name (e.g. issues, controls).")
    parser.add_argument("ai_function", help="AI function name to export.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output CSV path (defaults to ./<dataset>_<ai_function>_export.csv).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        output_csv, total, missing = asyncio.run(
            export_ai_data(
                dataset=args.dataset,
                ai_function=args.ai_function,
                output_csv=args.output,
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
