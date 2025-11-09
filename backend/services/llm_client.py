"""Simple mock LLM client used for testing bulk execution flows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class MockLLMClient:
    """A placeholder LLM client that captures contextual metadata."""

    session_id: str
    user_id: str
    extras: Dict[str, Any] | None = None


def create_mock_llm_client(session_id: str, user_id: str) -> MockLLMClient:
    """Factory that returns a reusable mock LLM client instance."""
    return MockLLMClient(session_id=session_id, user_id=user_id)
