"""DAO for controls dataset."""
from typing import Dict, Any, List, Optional
from dao.base import BaseDAO

class ControlsDAO(BaseDAO):
    """Data Access Object for controls dataset."""

    def __init__(self):
        """Initialize controls DAO."""
        super().__init__(dataset_name='controls', key_field='control_id')

    def search_by_id(self, control_id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search controls by control ID."""
        results = super().search_by_id(control_id, limit)
        # Rename 'id' to 'control_id' for consistency
        for item in results:
            item['control_id'] = item.pop('id')
        return results

    def get_details(self, control_id: str) -> Optional[Dict[str, Any]]:
        """Get full control details including AI results."""
        return super().get_details(control_id)

    def trigger_ai_taxonomy(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI taxonomy generation for a control."""
        return self.trigger_ai_function(
            control_id,
            'ai_taxonomy',
            description,
            refresh
        )

    def trigger_ai_root_causes(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI root cause analysis for a control."""
        return self.trigger_ai_function(
            control_id,
            'ai_root_causes',
            description,
            refresh
        )

    def trigger_ai_enrichment(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI enrichment for a control."""
        return self.trigger_ai_function(
            control_id,
            'ai_enrichment',
            description,
            refresh
        )

    def trigger_similar_controls(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger similar controls identification."""
        return self.trigger_ai_function(
            control_id,
            'similar_controls',
            description,
            refresh
        )

    def list_all(self, offset: int = 0, limit: int = 100):
        """List all controls with pagination."""
        items, total = super().list_all(offset, limit)
        # Rename 'id' to 'control_id' for consistency
        for item in items:
            item['control_id'] = item.pop('id')
        return items, total

    def search_by_taxonomy(self, taxonomy_token: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search controls by taxonomy token."""
        results = super().search_by_taxonomy(taxonomy_token, limit)
        # Rename 'id' to 'control_id' for consistency
        for item in results:
            item['control_id'] = item.pop('id')
        return results