"""Pydantic models for internal loss dataset."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class InternalLossListItem(BaseModel):
    """Internal loss list item for search results."""
    loss_id: str = Field(..., description="Internal loss ID")
    description: str = Field(..., description="Loss description")
    nfr_taxonomy: str = Field(..., description="NFR taxonomy (pipe-delimited)")
    ai_taxonomy_present: bool = Field(False, description="Whether AI taxonomy has been computed")

class InternalLossRawData(BaseModel):
    """Raw internal loss data."""
    loss_id: str
    description: str
    nfr_taxonomy: str
    raw_data: Optional[Dict[str, Any]] = None

class InternalLossAIResults(BaseModel):
    """AI results for an internal loss."""
    taxonomy: Optional[Dict[str, Any]] = None
    root_causes: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None
    similar_internal_loss: Optional[Dict[str, Any]] = None

class InternalLossDetails(BaseModel):
    """Detailed internal loss information."""
    raw: InternalLossRawData
    ai: InternalLossAIResults

class InternalLossSearchRequest(BaseModel):
    """Request model for internal loss search."""
    description: Optional[str] = Field(None, description="Optional description for AI functions")

class InternalLossList(BaseModel):
    """List of internal losses."""
    items: List[InternalLossListItem]
    total: Optional[int] = None