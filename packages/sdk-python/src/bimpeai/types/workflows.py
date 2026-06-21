from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict
from typing_extensions import NotRequired, TypedDict

from .rules import Rule, RuleInput

WorkflowVisibility = Literal["private", "public"]
WorkflowScope = Literal["accessible", "owned", "public"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class WorkflowGuide(_Model):
    youtubeUrl: str | None = None
    steps: list[str] = []


class WorkflowFaqItem(_Model):
    question: str
    answer: str


class Workflow(_Model):
    id: str
    name: str
    description: str | None = None
    category: str | None = None
    visibility: WorkflowVisibility
    is_owner: bool
    created_at: str
    updated_at: str
    system_prompt: str | None = None
    rules: list[Rule] = []
    flows: list[dict[str, Any]] = []
    tags: list[str] = []
    integrations: list[str] = []
    channels: list[str] = []
    actions: list[str] = []
    guide: WorkflowGuide | None = None
    faq: list[WorkflowFaqItem] = []
    setup_steps: list[Any] = []
    setup_time: int | None = None
    video_url: str | None = None


WorkflowSummary = Workflow


class CreateWorkflowBody(TypedDict):
    name: str
    system_prompt: str
    description: NotRequired[str]
    category: NotRequired[str]
    rules: NotRequired[list[RuleInput]]
    flows: NotRequired[list[dict[str, Any]]]
    tags: NotRequired[list[str]]
    integrations: NotRequired[list[str]]
    channels: NotRequired[list[str]]
    actions: NotRequired[list[str]]
    guide: NotRequired[dict[str, Any]]
    faq: NotRequired[list[dict[str, str]]]
    setup_steps: NotRequired[list[Any]]
    setup_time: NotRequired[int]
    video_url: NotRequired[str]


class UpdateWorkflowBody(TypedDict, total=False):
    name: str
    system_prompt: str
    description: str
    category: str
    rules: list[RuleInput]
    flows: list[dict[str, Any]]
    tags: list[str]
    integrations: list[str]
    channels: list[str]
    actions: list[str]
    guide: dict[str, Any]
    faq: list[dict[str, str]]
    setup_steps: list[Any]
    setup_time: int
    video_url: str


class CloneWorkflowBody(TypedDict):
    source_workflow_id: str
