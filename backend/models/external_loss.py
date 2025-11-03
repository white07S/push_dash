"""Pydantic models for external loss dataset."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ExternalLossListItem(BaseModel):
    """External loss list item for search results."""
    ext_loss_id: str = Field(..., description="External loss ID")
    description: str = Field(..., description="Loss description")
    nfr_taxonomy: str = Field(..., description="NFR taxonomy (pipe-delimited)")
    ai_taxonomy_present: bool = Field(False, description="Whether AI taxonomy has been computed")

class ExternalLossRawData(BaseModel):
    """Raw external loss data."""
    ext_loss_id: str
    description: str
    nfr_taxonomy: str
    raw_data: Optional[Dict[str, Any]] = None

class ExternalLossAIResults(BaseModel):
    """AI results for an external loss."""
    taxonomy: Optional[Dict[str, Any]] = None
    root_causes: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None
    similar_external_loss: Optional[Dict[str, Any]] = None

class ExternalLossDetails(BaseModel):
    """Detailed external loss information."""
    raw: ExternalLossRawData
    ai: ExternalLossAIResults

class ExternalLossSearchRequest(BaseModel):
    """Request model for external loss search."""
    description: Optional[str] = Field(None, description="Optional description for AI functions")

class ExternalLossList(BaseModel):
    """List of external losses."""
    items: List[ExternalLossListItem]
    total: Optional[int] = None