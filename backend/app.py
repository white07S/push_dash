"""Main FastAPI application."""
import os
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import yaml

from db import get_db
from utils.csv_ingest import CSVIngester
from utils.batch_utils import BatchProcessor
from routers import (
    controls_router,
    external_loss_router,
    internal_loss_router,
    issues_router
)
from models.shared import HealthCheck, IngestionResult, BatchProcessingStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting up application...")

    # Initialize database
    db = get_db()
    logger.info("Database initialized")

    # Check if CSV ingestion is needed
    ingester = CSVIngester()
    stats = ingester.get_ingestion_stats()

    if all(count == 0 for count in stats.values()):
        logger.info("No data found, performing initial CSV ingestion...")
        results = ingester.ingest_all(batch_size=1000)
        for dataset, result in results.items():
            if 'error' not in result:
                logger.info(f"Ingested {dataset}: {result['successful']} successful, {result['failed']} failed")
            else:
                logger.error(f"Error ingesting {dataset}: {result['error']}")
    else:
        logger.info(f"Data already present: {stats}")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    db.close()

# Create FastAPI app
app = FastAPI(
    title="NFR Dashboard API",
    description="React + FastAPI dashboard for exploring NFR datasets",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('cors', {}).get('origins', ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.utcnow()

    # Extract headers
    session_id = request.headers.get("X-Session-Id", "unknown")
    user_id = request.headers.get("X-User-Id", "unknown")

    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Session: {session_id} | User: {user_id}"
    )

    # Process request
    try:
        response = await call_next(request)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Duration: {duration:.3f}s"
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        response.headers["X-Session-Id"] = session_id

        return response
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"Error: {request.method} {request.url.path} | "
            f"Error: {str(e)} | Duration: {duration:.3f}s"
        )
        raise

# Include routers
app.include_router(controls_router)
app.include_router(external_loss_router)
app.include_router(internal_loss_router)
app.include_router(issues_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "NFR Dashboard API",
        "version": "0.1.0",
        "endpoints": [
            "/api/controls",
            "/api/external-loss",
            "/api/internal-loss",
            "/api/issues"
        ]
    }

# Health check endpoint
@app.get("/healthz", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        db = get_db()
        ingester = CSVIngester()
        stats = ingester.get_ingestion_stats()

        return HealthCheck(
            status="healthy",
            database="connected",
            datasets=stats,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Admin endpoints for data management
@app.post("/admin/ingest", response_model=IngestionResult)
async def ingest_data(
    dataset: str,
    force: bool = False
):
    """Manually trigger CSV ingestion for a dataset."""
    try:
        ingester = CSVIngester()

        # Check if data already exists
        if not force:
            stats = ingester.get_ingestion_stats()
            if stats.get(dataset, 0) > 0:
                raise HTTPException(
                    status_code=409,
                    detail=f"Dataset {dataset} already has data. Use force=true to re-ingest."
                )

        result = ingester.ingest_dataset(dataset)
        return IngestionResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/batch-compute")
async def batch_compute_ai_functions(
    dataset: str,
    function_name: str,
    force_recompute: bool = False,
    max_items: Optional[int] = None
):
    """Batch compute AI functions for a dataset."""
    try:
        from services import mock_ai

        # Map function names to compute functions
        function_map = {
            'controls': {
                'ai_taxonomy': mock_ai.get_controls_ai_taxonomy,
                'ai_root_causes': mock_ai.get_controls_ai_root_causes,
                'ai_enrichment': mock_ai.get_controls_ai_enrichment,
                'similar_controls': mock_ai.get_controls_similar_controls
            },
            'external_loss': {
                'ai_taxonomy': mock_ai.get_external_loss_ai_taxonomy,
                'ai_root_causes': mock_ai.get_external_loss_ai_root_causes,
                'ai_enrichment': mock_ai.get_external_loss_ai_enrichment,
                'similar_external_loss': mock_ai.get_external_loss_similar_external_loss
            },
            'internal_loss': {
                'ai_taxonomy': mock_ai.get_internal_loss_ai_taxonomy,
                'ai_root_causes': mock_ai.get_internal_loss_ai_root_causes,
                'ai_enrichment': mock_ai.get_internal_loss_ai_enrichment,
                'similar_internal_loss': mock_ai.get_internal_loss_similar_internal_loss
            },
            'issues': {
                'ai_taxonomy': mock_ai.get_issues_ai_taxonomy,
                'ai_root_causes': mock_ai.get_issues_ai_root_causes,
                'ai_enrichment': mock_ai.get_issues_ai_enrichment,
                'similar_issues': mock_ai.get_issues_similar_issues
            }
        }

        if dataset not in function_map:
            raise HTTPException(status_code=400, detail=f"Invalid dataset: {dataset}")

        if function_name not in function_map[dataset]:
            raise HTTPException(status_code=400, detail=f"Invalid function: {function_name}")

        processor = BatchProcessor()
        compute_func = function_map[dataset][function_name]

        # Get IDs to process
        ids = None
        if max_items:
            db = get_db()
            key_fields = {
                'controls': 'control_id',
                'external_loss': 'ext_loss_id',
                'internal_loss': 'loss_id',
                'issues': 'issue_id'
            }
            key_field = key_fields[dataset]
            query = f"SELECT {key_field} FROM {dataset}_raw LIMIT ?"
            rows = db.fetchall(query, (max_items,))
            ids = [row[0] for row in rows]

        result = processor.batch_compute_ai_function(
            dataset=dataset,
            function_name=function_name,
            compute_func=compute_func,
            ids=ids,
            force_recompute=force_recompute
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch compute error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/batch-status/{dataset}")
async def get_batch_status(dataset: str):
    """Get batch processing status for a dataset."""
    try:
        processor = BatchProcessor()
        return processor.get_batch_status(dataset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "app:app",
        host=config.get('server', {}).get('host', "0.0.0.0"),
        port=config.get('server', {}).get('port', 8000),
        reload=config.get('server', {}).get('reload', True),
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )