"""Pydantic models for internal loss dataset."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InternalLossListItem(BaseModel):
    """Internal loss list item for search results."""

    event_id: str = Field(..., description="Internal loss event ID")
    event_title: Optional[str] = Field(None, description="Event title")
    event_type: Optional[str] = Field(None, description="Event type")
    risk_theme: Optional[str] = Field(None, description="Risk theme")
    risk_subtheme: Optional[str] = Field(None, description="Risk subtheme")
    ai_status: Dict[str, bool] = Field(default_factory=dict, description="AI computation flags")
    record: Dict[str, Any] = Field(default_factory=dict, description="Complete CSV row")


class InternalLossRawData(BaseModel):
    """Raw internal loss data."""

    event_id: str
    event_title: Optional[str] = None
    event_type: Optional[str] = None
    risk_theme: Optional[str] = None
    risk_subtheme: Optional[str] = None
    record: Dict[str, Any] = Field(default_factory=dict)


class InternalLossAIResults(BaseModel):
    """AI results for an internal loss."""

    issue_taxonomy: Optional[Any] = None
    root_cause: Optional[Any] = None
    enrichment: Optional[Any] = None


class InternalLossDetails(BaseModel):
    """Detailed internal loss information."""

    raw: InternalLossRawData
    ai: InternalLossAIResults



class InternalLossList(BaseModel):
    """List of internal losses."""

    items: List[InternalLossListItem]
    total: Optional[int] = None
