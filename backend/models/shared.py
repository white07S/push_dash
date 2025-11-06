"""Shared Pydantic models for API responses."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class AIFunctionResult(BaseModel):
    """AI function result response."""
    payload: Any = Field(..., description="AI function result payload")
    created_at: str = Field(..., description="ISO-8601 timestamp")

class TriggerResponse(BaseModel):
    """Response for AI function trigger endpoints."""
    status: str = Field(..., description="Status (ok/error)")
    source: str = Field(..., description="Source (cache/computed)")
    payload: Any = Field(..., description="Result payload")
    created_at: str = Field(..., description="ISO-8601 timestamp")

class TriggerRequest(BaseModel):
    """Request payload for AI function trigger endpoints."""
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Error code")

class BatchProcessingStatus(BaseModel):
    """Batch processing status response."""
    status: str = Field(..., description="Processing status")
    total: int = Field(..., description="Total items to process")
    processed: int = Field(..., description="Items processed")
    successful: int = Field(..., description="Successfully processed")
    failed: int = Field(..., description="Failed items")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    elapsed_time: Optional[str] = Field(None, description="Processing time")
    rate: Optional[str] = Field(None, description="Processing rate")

class IngestionResult(BaseModel):
    """CSV ingestion result."""
    dataset: str = Field(..., description="Dataset name")
    successful: int = Field(..., description="Successfully ingested rows")
    failed: int = Field(..., description="Failed rows")
    total: int = Field(..., description="Total rows processed")
    errors: List[str] = Field(default_factory=list, description="Error messages")

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    database: str = Field(..., description="Database status")
    datasets: Dict[str, int] = Field(..., description="Record counts per dataset")
    timestamp: str = Field(..., description="Check timestamp")
