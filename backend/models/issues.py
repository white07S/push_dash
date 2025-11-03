"""Pydantic models for issues dataset."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class IssuesListItem(BaseModel):
    """Issues list item for search results."""
    issue_id: str = Field(..., description="Issue ID")
    description: str = Field(..., description="Issue description")
    nfr_taxonomy: str = Field(..., description="NFR taxonomy (pipe-delimited)")
    ai_taxonomy_present: bool = Field(False, description="Whether AI taxonomy has been computed")

class IssuesRawData(BaseModel):
    """Raw issues data."""
    issue_id: str
    description: str
    nfr_taxonomy: str
    raw_data: Optional[Dict[str, Any]] = None

class IssuesAIResults(BaseModel):
    """AI results for an issue."""
    taxonomy: Optional[Dict[str, Any]] = None
    root_causes: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None
    similar_issues: Optional[Dict[str, Any]] = None

class IssuesDetails(BaseModel):
    """Detailed issue information."""
    raw: IssuesRawData
    ai: IssuesAIResults

class IssuesSearchRequest(BaseModel):
    """Request model for issues search."""
    description: Optional[str] = Field(None, description="Optional description for AI functions")

class IssuesList(BaseModel):
    """List of issues."""
    items: List[IssuesListItem]
    total: Optional[int] = None