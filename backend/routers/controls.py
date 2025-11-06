"""API router for controls endpoints."""
from fastapi import APIRouter, Header, HTTPException, Query
import logging

from dao.controls import ControlsDAO
from models.controls import (
    ControlsList,
    ControlsListItem,
    ControlsDetails
)
from models.shared import TriggerResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/controls",
    tags=["controls"],
    responses={404: {"model": ErrorResponse}}
)

# Initialize DAO
dao = ControlsDAO()

@router.get("", response_model=ControlsList)
async def search_controls(
    id: str = Query(..., description="Control ID to search for"),
    limit: int = Query(1, description="Maximum number of results", ge=1, le=100)
):
    """Search controls by ID."""
    try:
        items = dao.search_by_id(id, limit)
        return ControlsList(items=items, total=len(items))
    except Exception as e:
        logger.error(f"Error searching controls: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=ControlsList)
async def list_controls(
    offset: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(100, description="Maximum number of items", ge=1, le=1000)
):
    """List all controls with pagination."""
    try:
        items, total = dao.list_all(offset, limit)
        return ControlsList(items=items, total=total)
    except Exception as e:
        logger.error(f"Error listing controls: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{control_id}/details", response_model=ControlsDetails)
async def get_control_details(control_id: str):
    """Get full control details including AI results."""
    try:
        details = dao.get_details(control_id)
        if not details:
            raise HTTPException(status_code=404, detail=f"Control {control_id} not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting control details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{control_id}/controls-taxonomy", response_model=TriggerResponse)
async def trigger_controls_taxonomy(
    control_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    session_id: str = Header(..., alias="X-Session-Id"),
    user_id: str = Header(..., alias="X-User-Id"),
):
    """Trigger AI taxonomy generation for a control."""
    try:
        result = await dao.trigger_controls_taxonomy(control_id, session_id, user_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI taxonomy: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{control_id}/root-cause", response_model=TriggerResponse)
async def trigger_root_cause(
    control_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    session_id: str = Header(..., alias="X-Session-Id"),
    user_id: str = Header(..., alias="X-User-Id"),
):
    """Trigger AI root cause analysis for a control."""
    try:
        result = await dao.trigger_root_cause(control_id, session_id, user_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI root causes: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{control_id}/enrichment", response_model=TriggerResponse)
async def trigger_enrichment(
    control_id: str,
    refresh: bool = Query(False, description="Force recompute even if cached"),
    session_id: str = Header(..., alias="X-Session-Id"),
    user_id: str = Header(..., alias="X-User-Id"),
):
    """Trigger AI enrichment for a control."""
    try:
        result = await dao.trigger_enrichment(control_id, session_id, user_id, refresh)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI enrichment: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/statistics")
async def get_statistics():
    """Get controls dataset statistics."""
    try:
        return dao.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
