"""
Orchestrator Events and Logging (spec section 23).
"""
from typing import Any
from datetime import datetime, timezone
from pydantic import BaseModel


class AgentEvent(BaseModel):
    agent_name: str
    stage: str
    message: str
    status: str = "running"  # running, completed, warning, error
    timestamp: str = ""
    details: dict[str, Any] = {}

    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.now(timezone.utc).isoformat()
        super().__init__(**data)
