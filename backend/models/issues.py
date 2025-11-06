"""Pydantic models for issues dataset."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IssuesListItem(BaseModel):
    """Issues list item for search results."""

    issue_id: str = Field(..., description="Issue ID")
    issue_title: Optional[str] = Field(None, description="Issue title")
    issues_type: Optional[str] = Field(None, description="Issue type")
    risk_theme: Optional[str] = Field(None, description="Risk theme")
    risk_subtheme: Optional[str] = Field(None, description="Risk subtheme")
    ai_status: Dict[str, bool] = Field(default_factory=dict, description="AI computation flags")
    record: Dict[str, Any] = Field(default_factory=dict, description="Complete CSV row")


class IssuesRawData(BaseModel):
    """Raw issues data."""

    issue_id: str
    issue_title: Optional[str] = None
    issues_type: Optional[str] = None
    risk_theme: Optional[str] = None
    risk_subtheme: Optional[str] = None
    record: Dict[str, Any] = Field(default_factory=dict)


class IssuesAIResults(BaseModel):
    """AI results for an issue."""

    issue_taxonomy: Optional[Any] = None
    root_cause: Optional[Any] = None
    enrichment: Optional[Any] = None


class IssuesDetails(BaseModel):
    """Detailed issue information."""

    raw: IssuesRawData
    ai: IssuesAIResults



class IssuesList(BaseModel):
    """List of issues."""

    items: List[IssuesListItem]
    total: Optional[int] = None
