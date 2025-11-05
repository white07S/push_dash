"""Pydantic models for controls dataset."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ControlsListItem(BaseModel):
    """Controls list item for search results."""

    control_id: str = Field(..., description="Control ID")
    control_title: Optional[str] = Field(None, description="Control title")
    key_control: Optional[str] = Field(None, description="Key control indicator")
    risk_theme: Optional[str] = Field(None, description="Risk theme")
    risk_subtheme: Optional[str] = Field(None, description="Risk subtheme")
    ai_status: Dict[str, bool] = Field(default_factory=dict, description="AI computation flags")
    record: Dict[str, Any] = Field(default_factory=dict, description="Complete CSV row")


class ControlsRawData(BaseModel):
    """Raw controls data."""

    control_id: str
    control_title: Optional[str] = None
    key_control: Optional[str] = None
    risk_theme: Optional[str] = None
    risk_subtheme: Optional[str] = None
    record: Dict[str, Any] = Field(default_factory=dict)


class ControlsAIResults(BaseModel):
    """AI results for a control."""

    controls_taxonomy: Optional[Dict[str, Any]] = None
    root_cause: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None


class ControlsDetails(BaseModel):
    """Detailed control information."""

    raw: ControlsRawData
    ai: ControlsAIResults



class ControlsList(BaseModel):
    """List of controls."""

    items: List[ControlsListItem]
    total: Optional[int] = None
