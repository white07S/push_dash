"""DAO for external loss dataset."""
from typing import Dict, Any, List, Optional
from dao.base import BaseDAO

class ExternalLossDAO(BaseDAO):
    """Data Access Object for external loss dataset."""

    def __init__(self):
        """Initialize external loss DAO."""
        super().__init__(dataset_name='external_loss', key_field='ext_loss_id')

    def search_by_id(self, ext_loss_id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search external losses by ID."""
        results = super().search_by_id(ext_loss_id, limit)
        # Rename 'id' to 'ext_loss_id' for consistency
        for item in results:
            item['ext_loss_id'] = item.pop('id')
        return results

    def get_details(self, ext_loss_id: str) -> Optional[Dict[str, Any]]:
        """Get full external loss details including AI results."""
        return super().get_details(ext_loss_id)

    def trigger_ai_taxonomy(
        self,
        ext_loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI taxonomy generation for an external loss."""
        return self.trigger_ai_function(
            ext_loss_id,
            'ai_taxonomy',
            description,
            refresh
        )

    def trigger_ai_root_causes(
        self,
        ext_loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI root cause analysis for an external loss."""
        return self.trigger_ai_function(
            ext_loss_id,
            'ai_root_causes',
            description,
            refresh
        )

    def trigger_ai_enrichment(
        self,
        ext_loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI enrichment for an external loss."""
        return self.trigger_ai_function(
            ext_loss_id,
            'ai_enrichment',
            description,
            refresh
        )

    def trigger_similar_external_loss(
        self,
        ext_loss_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger similar external losses identification."""
        return self.trigger_ai_function(
            ext_loss_id,
            'similar_external_loss',
            description,
            refresh
        )

    def list_all(self, offset: int = 0, limit: int = 100):
        """List all external losses with pagination."""
        items, total = super().list_all(offset, limit)
        # Rename 'id' to 'ext_loss_id' for consistency
        for item in items:
            item['ext_loss_id'] = item.pop('id')
        return items, total

    def search_by_taxonomy(self, taxonomy_token: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search external losses by taxonomy token."""
        results = super().search_by_taxonomy(taxonomy_token, limit)
        # Rename 'id' to 'ext_loss_id' for consistency
        for item in results:
            item['ext_loss_id'] = item.pop('id')
        return results