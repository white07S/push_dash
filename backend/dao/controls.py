"""DAO for controls dataset."""
from typing import Dict, Any, Optional
from dao.base import BaseDAO


class ControlsDAO(BaseDAO):
    """Data Access Object for controls dataset."""

    def __init__(self):
        super().__init__(dataset_name="controls")

    def get_details(self, control_id: str) -> Optional[Dict[str, Any]]:
        return super().get_details(control_id)

    async def trigger_controls_taxonomy(
        self,
        control_id: str,
        session_id: str,
        user_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return await self.trigger_ai_function(
            control_id,
            "controls_taxonomy",
            session_id,
            user_id,
            refresh,
        )

    async def trigger_root_cause(
        self,
        control_id: str,
        session_id: str,
        user_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return await self.trigger_ai_function(
            control_id,
            "root_cause",
            session_id,
            user_id,
            refresh,
        )

    async def trigger_enrichment(
        self,
        control_id: str,
        session_id: str,
        user_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return await self.trigger_ai_function(
            control_id,
            "enrichment",
            session_id,
            user_id,
            refresh,
        )
