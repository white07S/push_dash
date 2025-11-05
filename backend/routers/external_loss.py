"""API router for external loss endpoints."""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional
import logging

from dao.external_loss import ExternalLossDAO
from models.external_loss import (
    ExternalLossList,
    ExternalLossListItem,
    ExternalLossDetails,
    ExternalLossSearchRequest
)
from models.shared import TriggerResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/external-loss",
    tags=["external-loss"],
    responses={404: {"model": ErrorResponse}}
)

# Initialize DAO
dao = ExternalLossDAO()

@router.get("", response_model=ExternalLossList)
async def search_external_losses(
    id: str = Query(..., description="External loss ID to search for"),
    limit: int = Query(1, description="Maximum number of results", ge=1, le=100)
):
    """Search external losses by ID."""
    try:
        items = dao.search_by_id(id, limit)
        return ExternalLossList(items=items, total=len(items))
    except Exception as e:
        logger.error(f"Error searching external losses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=ExternalLossList)
async def list_external_losses(
    offset: int = Query(0, description="Number of items to skip", ge=0),
    limit: int = Query(100, description="Maximum number of items", ge=1, le=1000)
):
    """List all external losses with pagination."""
    try:
        items, total = dao.list_all(offset, limit)
        return ExternalLossList(items=items, total=total)
    except Exception as e:
        logger.error(f"Error listing external losses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{reference_id_code}/details", response_model=ExternalLossDetails)
async def get_external_loss_details(reference_id_code: str):
    """Get full external loss details including AI results."""
    try:
        details = dao.get_details(reference_id_code)
        if not details:
            raise HTTPException(status_code=404, detail=f"External loss {reference_id_code} not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting external loss details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{reference_id_code}/issue-taxonomy", response_model=TriggerResponse)
async def trigger_issue_taxonomy(
    reference_id_code: str,
    request: ExternalLossSearchRequest = Body(default=ExternalLossSearchRequest()),
    refresh: bool = Query(False, description="Force recompute even if cached")
):
    """Trigger AI taxonomy generation for an external loss."""
    try:
        result = dao.trigger_issue_taxonomy(
            reference_id_code,
            request.description,
            refresh
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI taxonomy: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{reference_id_code}/root-cause", response_model=TriggerResponse)
async def trigger_root_cause(
    reference_id_code: str,
    request: ExternalLossSearchRequest = Body(default=ExternalLossSearchRequest()),
    refresh: bool = Query(False, description="Force recompute even if cached")
):
    """Trigger AI root cause analysis for an external loss."""
    try:
        result = dao.trigger_root_cause(
            reference_id_code,
            request.description,
            refresh
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI root causes: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.post("/{reference_id_code}/enrichment", response_model=TriggerResponse)
async def trigger_enrichment(
    reference_id_code: str,
    request: ExternalLossSearchRequest = Body(default=ExternalLossSearchRequest()),
    refresh: bool = Query(False, description="Force recompute even if cached")
):
    """Trigger AI enrichment for an external loss."""
    try:
        result = dao.trigger_enrichment(
            reference_id_code,
            request.description,
            refresh
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering AI enrichment: {e}")
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/statistics")
async def get_statistics():
    """Get external loss dataset statistics."""
    try:
        return dao.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
