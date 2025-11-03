"""Pydantic models for controls dataset."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ControlsListItem(BaseModel):
    """Controls list item for search results."""
    control_id: str = Field(..., description="Control ID")
    description: str = Field(..., description="Control description")
    nfr_taxonomy: str = Field(..., description="NFR taxonomy (pipe-delimited)")
    ai_taxonomy_present: bool = Field(False, description="Whether AI taxonomy has been computed")

class ControlsRawData(BaseModel):
    """Raw controls data."""
    control_id: str
    description: str
    nfr_taxonomy: str
    raw_data: Optional[Dict[str, Any]] = None

class ControlsAIResults(BaseModel):
    """AI results for a control."""
    taxonomy: Optional[Dict[str, Any]] = None
    root_causes: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None
    similar_controls: Optional[Dict[str, Any]] = None

class ControlsDetails(BaseModel):
    """Detailed control information."""
    raw: ControlsRawData
    ai: ControlsAIResults

class ControlsSearchRequest(BaseModel):
    """Request model for controls search."""
    description: Optional[str] = Field(None, description="Optional description for AI functions")

class ControlsList(BaseModel):
    """List of controls."""
    items: List[ControlsListItem]
    total: Optional[int] = None