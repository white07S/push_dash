"""Pydantic models for external loss dataset."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExternalLossListItem(BaseModel):
    """External loss list item for search results."""

    reference_id_code: str = Field(..., description="External loss reference ID")
    parent_name: Optional[str] = Field(None, description="Parent organization name")
    description_of_event: Optional[str] = Field(None, description="Event description")
    risk_theme: Optional[str] = Field(None, description="Risk theme")
    risk_subtheme: Optional[str] = Field(None, description="Risk subtheme")
    ai_status: Dict[str, bool] = Field(default_factory=dict, description="AI computation flags")
    record: Dict[str, Any] = Field(default_factory=dict, description="Complete CSV row")


class ExternalLossRawData(BaseModel):
    """Raw external loss data."""

    reference_id_code: str
    parent_name: Optional[str] = None
    description_of_event: Optional[str] = None
    risk_theme: Optional[str] = None
    risk_subtheme: Optional[str] = None
    record: Dict[str, Any] = Field(default_factory=dict)


class ExternalLossAIResults(BaseModel):
    """AI results for an external loss."""

    issue_taxonomy: Optional[Dict[str, Any]] = None
    root_cause: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None


class ExternalLossDetails(BaseModel):
    """Detailed external loss information."""

    raw: ExternalLossRawData
    ai: ExternalLossAIResults



class ExternalLossList(BaseModel):
    """List of external losses."""

    items: List[ExternalLossListItem]
    total: Optional[int] = None
