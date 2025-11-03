"""DAO for internal loss dataset."""
from typing import Dict, Any, List, Optional
from dao.base import BaseDAO

class InternalLossDAO(BaseDAO):
    """Data Access Object for internal loss dataset."""

    def __init__(self):
        """Initialize internal loss DAO."""
        super().__init__(dataset_name='internal_loss', key_field='loss_id')

    def search_by_id(self, loss_id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search internal losses by ID."""
        results = super().search_by_id(loss_id, limit)
        # Rename 'id' to 'loss_id' for consistency
        for item in results:
            item['loss_id'] = item.pop('id')
        return results

    def get_details(self, loss_id: str) -> Optional[Dict[str, Any]]:
        """Get full internal loss details including AI results."""
        return super().get_details(loss_id)

    def trigger_ai_taxonomy(
        self,
        loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI taxonomy generation for an internal loss."""
        return self.trigger_ai_function(
            loss_id,
            'ai_taxonomy',
            description,
            refresh
        )

    def trigger_ai_root_causes(
        self,
        loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI root cause analysis for an internal loss."""
        return self.trigger_ai_function(
            loss_id,
            'ai_root_causes',
            description,
            refresh
        )

    def trigger_ai_enrichment(
        self,
        loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI enrichment for an internal loss."""
        return self.trigger_ai_function(
            loss_id,
            'ai_enrichment',
            description,
            refresh
        )

    def trigger_similar_internal_loss(
        self,
        loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger similar internal losses identification."""
        return self.trigger_ai_function(
            loss_id,
            'similar_internal_loss',
            description,
            refresh
        )

    def list_all(self, offset: int = 0, limit: int = 100):
        """List all internal losses with pagination."""
        items, total = super().list_all(offset, limit)
        # Rename 'id' to 'loss_id' for consistency
        for item in items:
            item['loss_id'] = item.pop('id')
        return items, total

    def search_by_taxonomy(self, taxonomy_token: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search internal losses by taxonomy token."""
        results = super().search_by_taxonomy(taxonomy_token, limit)
        # Rename 'id' to 'loss_id' for consistency
        for item in results:
            item['loss_id'] = item.pop('id')
        return results