"""API router for issues endpoints."""
from fastapi import APIRouter, HTTPException, Query
import logging

from dao.issues import IssuesDAO
from models.issues import (
    IssuesList,
    IssuesListItem,
    IssuesDetails
)
from models.shared import TriggerRequest, TriggerResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/issues",
    tags=["issues"],
    responses={404: {"model": ErrorResponse}}
)

# Initialize DAO
dao = IssuesDAO()

@router.get("", response_model=IssuesList)
async def search_issues(
    id: str = Query(..., description="Issue ID to search for"),
    limit: int = Query(1, description="Maximum number of results", ge=1, le=100)
):
    """Search issues by ID."""
    try:
        items = dao.search_by_id(id, limit)
        return IssuesList(items=items, total=len(items))
    except Exception as e:
        logger.error(f"Error searching issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=IssuesList)
async def list_issues(
    offset: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(100, description="Maximum number of items", ge=1, le=1000)
):
    """List all issues with pagination."""
    try:
        items, total = dao.list_all(offset, limit)
        return IssuesList(items=items, total=total)
    except Exception as e:
        logger.error(f"Error listing issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{issue_id}/details", response_model=IssuesDetails)
async def get_issue_details(issue_id: str):
    """Get full issue details including AI results."""
    try:
        details = dao.get_details(issue_id)
        if not details:
            raise HTTPException(status_code=404, detail=f"Issue {issue_id} not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting issue details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{issue_id}/issue-taxonomy", response_model=TriggerResponse)
async def trigger_issue_taxonomy(
    issue_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    payload: TriggerRequest,
):
    """Trigger AI taxonomy generation for an issue."""
    try:
        result = await dao.trigger_issue_taxonomy(issue_id, payload.session_id, payload.user_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering issue taxonomy: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{issue_id}/root-cause", response_model=TriggerResponse)
async def trigger_root_cause(
    issue_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    payload: TriggerRequest,
):
    """Trigger AI root cause analysis for an issue."""
    try:
        result = await dao.trigger_root_cause(issue_id, payload.session_id, payload.user_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI root causes: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{issue_id}/enrichment", response_model=TriggerResponse)
async def trigger_enrichment(
    issue_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    payload: TriggerRequest,
):
    """Trigger AI enrichment for an issue."""
    try:
        result = await dao.trigger_enrichment(issue_id, payload.session_id, payload.user_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI enrichment: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/statistics")
async def get_statistics():
    """Get issues dataset statistics."""
    try:
        return dao.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
