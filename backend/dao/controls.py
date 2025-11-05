"""DAO for controls dataset."""
from typing import Dict, Any, Optional
from dao.base import BaseDAO


class ControlsDAO(BaseDAO):
    """Data Access Object for controls dataset."""

    def __init__(self):
        super().__init__(dataset_name="controls")

    def get_details(self, control_id: str) -> Optional[Dict[str, Any]]:
        return super().get_details(control_id)

    def trigger_controls_taxonomy(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            control_id,
            "controls_taxonomy",
            description,
            refresh,
        )

    def trigger_root_cause(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            control_id,
            "root_cause",
            description,
            refresh,
        )

    def trigger_enrichment(
        self,
        control_id: str,
        description: Optional[str] = None,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            control_id,
            "enrichment",
            description,
            refresh,
        )
