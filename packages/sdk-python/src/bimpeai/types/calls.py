from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class Call(BaseModel):
    """Placeholder; the calls endpoint returns not_implemented until the API ships it."""

    model_config = ConfigDict(extra="allow", frozen=True)

    id: str


MakeCallBody = dict[str, Any]
QueueCallBody = dict[str, Any]
