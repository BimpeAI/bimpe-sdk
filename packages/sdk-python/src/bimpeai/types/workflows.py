from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

from .agents import Rule, RuleInput

WorkflowVisibility = Literal["private", "public"]
WorkflowScope = Literal["owned", "public"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class WorkflowSummary(_Model):
    id: str
    name: str
    description: str | None = None
    category: str | None = None
    visibility: WorkflowVisibility
    is_owner: bool
    created_at: str
    updated_at: str


class Workflow(WorkflowSummary):
    system_prompt: str | None = None
    rules: list[Rule] = []
    flows: list[dict[str, Any]] = []
    tags: list[str] = []
    prompt_config: dict[str, Any] = {}


class CreateWorkflowBody(TypedDict):
    name: str
    description: NotRequired[str]
    category: NotRequired[str]
    system_prompt: NotRequired[str]
    rules: NotRequired[list[RuleInput]]
    flows: NotRequired[list[dict[str, Any]]]
    tags: NotRequired[list[str]]
    prompt_config: NotRequired[dict[str, Any]]


class UpdateWorkflowBody(TypedDict, total=False):
    name: str
    description: str
    category: str
    system_prompt: str
    rules: list[RuleInput]
    flows: list[dict[str, Any]]
    tags: list[str]
    prompt_config: dict[str, Any]
