"""Routers package for backend API."""
from .controls import router as controls_router
from .external_loss import router as external_loss_router
from .internal_loss import router as internal_loss_router
from .issues import router as issues_router

__all__ = [
    'controls_router',
    'external_loss_router',
    'internal_loss_router',
    'issues_router'
]