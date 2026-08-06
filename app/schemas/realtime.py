from typing import Any

from pydantic import BaseModel, Field


class RealtimeEnvelope(BaseModel):
    type: str
    match_id: str
    sequence: int = Field(ge=0)
    payload: dict[str, Any]

