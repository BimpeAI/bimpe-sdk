from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Call(BaseModel):
    """Placeholder; the calls endpoint returns 501 until the API ships it."""

    model_config = ConfigDict(extra="allow", frozen=True)

    id: str
