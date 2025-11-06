"""API router for internal loss endpoints."""
from fastapi import APIRouter, Header, HTTPException, Query
import logging

from dao.internal_loss import InternalLossDAO
from models.internal_loss import (
    InternalLossList,
    InternalLossListItem,
    InternalLossDetails
)
from models.shared import TriggerResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/internal-loss",
    tags=["internal-loss"],
    responses={404: {"model": ErrorResponse}}
)

# Initialize DAO
dao = InternalLossDAO()

@router.get("", response_model=InternalLossList)
async def search_internal_losses(
    id: str = Query(..., description="Internal loss ID to search for"),
    limit: int = Query(1, description="Maximum number of results", ge=1, le=100)
):
    """Search internal losses by ID."""
    try:
        items = dao.search_by_id(id, limit)
        return InternalLossList(items=items, total=len(items))
    except Exception as e:
        logger.error(f"Error searching internal losses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=InternalLossList)
async def list_internal_losses(
    offset: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(100, description="Maximum number of items", ge=1, le=1000)
):
    """List all internal losses with pagination."""
    try:
        items, total = dao.list_all(offset, limit)
        return InternalLossList(items=items, total=total)
    except Exception as e:
        logger.error(f"Error listing internal losses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{event_id}/details", response_model=InternalLossDetails)
async def get_internal_loss_details(event_id: str):
    """Get full internal loss details including AI results."""
    try:
        details = dao.get_details(event_id)
        if not details:
            raise HTTPException(status_code=404, detail=f"Internal loss {event_id} not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting internal loss details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{event_id}/issue-taxonomy", response_model=TriggerResponse)
async def trigger_issue_taxonomy(
    event_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    session_id: str = Header(..., alias="X-Session-Id"),
):
    """Trigger AI taxonomy generation for an internal loss."""
    try:
        result = dao.trigger_issue_taxonomy(event_id, session_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI taxonomy: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{event_id}/root-cause", response_model=TriggerResponse)
async def trigger_root_cause(
    event_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    session_id: str = Header(..., alias="X-Session-Id"),
):
    """Trigger AI root cause analysis for an internal loss."""
    try:
        result = dao.trigger_root_cause(event_id, session_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI root causes: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{event_id}/enrichment", response_model=TriggerResponse)
async def trigger_enrichment(
    event_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    session_id: str = Header(..., alias="X-Session-Id"),
):
    """Trigger AI enrichment for an internal loss."""
    try:
        result = dao.trigger_enrichment(event_id, session_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI enrichment: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/statistics")
async def get_statistics():
    """Get internal loss dataset statistics."""
    try:
        return dao.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
