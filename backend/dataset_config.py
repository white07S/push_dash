"""Shared dataset configuration for backend services."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration describing a dataset's structure and behaviour."""

    csv_filename: str
    table: str
    key_field: str
    title_field: str
    theme_field: str
    subtheme_field: str
    description_field: str
    ai_functions: List[str]
    category_field: Optional[str] = None


DATASET_CONFIG: Dict[str, DatasetConfig] = {
    "issues": DatasetConfig(
        csv_filename="issues.csv",
        table="issues_raw",
        key_field="issue_id",
        title_field="issue_title",
        category_field="issues_type",
        theme_field="risk_theme",
        subtheme_field="risk_subtheme",
        description_field="issue_title",
        ai_functions=["issue_taxonomy", "root_cause", "enrichment"],
    ),
    "controls": DatasetConfig(
        csv_filename="controls.csv",
        table="controls_raw",
        key_field="control_id",
        title_field="control_title",
        category_field="key_control",
        theme_field="risk_theme",
        subtheme_field="risk_subtheme",
        description_field="control_title",
        ai_functions=["controls_taxonomy", "root_cause", "enrichment"],
    ),
    "external_loss": DatasetConfig(
        csv_filename="external_loss.csv",
        table="external_loss_raw",
        key_field="reference_id_code",
        title_field="description_of_event",
        category_field="parent_name",
        theme_field="risk_theme",
        subtheme_field="risk_subtheme",
        description_field="description_of_event",
        ai_functions=["issue_taxonomy", "root_cause", "enrichment"],
    ),
    "internal_loss": DatasetConfig(
        csv_filename="internal_loss.csv",
        table="internal_loss_raw",
        key_field="event_id",
        title_field="event_title",
        category_field="event_type",
        theme_field="risk_theme",
        subtheme_field="risk_subtheme",
        description_field="event_title",
        ai_functions=["issue_taxonomy", "root_cause", "enrichment"],
    ),
}


def get_dataset_config(dataset: str) -> DatasetConfig:
    """Fetch configuration for a dataset or raise ValueError."""
    try:
        return DATASET_CONFIG[dataset]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unknown dataset '{dataset}'") from exc

