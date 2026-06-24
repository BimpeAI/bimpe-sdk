from __future__ import annotations

from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, field_validator
from typing_extensions import NotRequired, TypedDict

from .agents import Rule, RuleInput

WorkflowVisibility = Literal["private", "public"]
WorkflowScope = Literal["owned", "public", "accessible"]


class _Model(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)


class FlowStep(_Model):
    type: str
    content: str | None = None
    action: str | None = None
    followup: str | None = None


class FlowTriggerKeyword(_Model):
    keyword: str
    weight: Literal["high", "medium", "low"] | None = None


class Flow(_Model):
    name: str
    description: str | None = None
    category: str | None = None
    priority: int | None = None
    is_active: bool | None = None
    trigger_keywords: list[FlowTriggerKeyword] | None = None
    conversation_steps: list[FlowStep] | None = None


class WorkflowGuide(_Model):
    youtube_url: str | None = None
    steps: list[str] = []


class WorkflowFaq(_Model):
    question: str
    answer: str


class Workflow(_Model):
    id: str
    name: str
    description: str | None = None
    category: str | None = None
    visibility: WorkflowVisibility
    is_owner: bool
    system_prompt: str | None = None
    rules: list[Rule] = []
    flows: list[Flow] = []
    tags: list[str] | None = None
    integrations: list[str] | None = None
    channels: list[str] | None = None
    actions: list[str] | None = None
    guide: WorkflowGuide | None = None
    faq: list[WorkflowFaq] | None = None
    setup_steps: list[Any] = []
    setup_time: int | None = None
    video_url: str | None = None
    created_at: str
    updated_at: str

    @field_validator("flows", "rules", "faq", mode="before")
    @classmethod
    def _drop_non_object_items(cls, value: Any) -> Any:
        # The server occasionally emits empty-list placeholders inside these
        # collections; drop anything that is not an object so a malformed entry
        # can never fail validation of the whole workflow.
        if not isinstance(value, list):
            return value
        return [item for item in cast("list[Any]", value) if isinstance(item, dict)]


WorkflowDetail = Workflow
WorkflowSummary = Workflow


class FlowStepInput(TypedDict):
    type: str
    content: NotRequired[str]
    action: NotRequired[str]
    followup: NotRequired[str]


class FlowTriggerKeywordInput(TypedDict):
    keyword: str
    weight: NotRequired[Literal["high", "medium", "low"]]


class FlowInput(TypedDict):
    name: str
    description: NotRequired[str | None]
    category: NotRequired[str | None]
    priority: NotRequired[int]
    is_active: NotRequired[bool]
    trigger_keywords: NotRequired[list[FlowTriggerKeywordInput]]
    conversation_steps: NotRequired[list[FlowStepInput]]


class WorkflowGuideInput(TypedDict):
    steps: list[str]
    youtube_url: NotRequired[str]


class WorkflowFaqInput(TypedDict):
    question: str
    answer: str


class CreateWorkflowBody(TypedDict):
    name: str
    system_prompt: str
    description: NotRequired[str]
    category: NotRequired[str]
    rules: NotRequired[list[RuleInput]]
    flows: NotRequired[list[FlowInput]]
    tags: NotRequired[list[str]]
    integrations: NotRequired[list[str]]
    channels: NotRequired[list[str]]
    actions: NotRequired[list[str]]
    guide: NotRequired[WorkflowGuideInput]
    faq: NotRequired[list[WorkflowFaqInput]]
    setup_steps: NotRequired[list[Any]]
    setup_time: NotRequired[int]
    video_url: NotRequired[str]


class UpdateWorkflowBody(TypedDict, total=False):
    name: str
    system_prompt: str
    description: str
    category: str
    rules: list[RuleInput]
    flows: list[FlowInput]
    tags: list[str]
    integrations: list[str]
    channels: list[str]
    actions: list[str]
    guide: WorkflowGuideInput
    faq: list[WorkflowFaqInput]
    setup_steps: list[Any]
    setup_time: int
    video_url: str


class CloneWorkflowBody(TypedDict):
    source_workflow_id: str


# Resolve the forward reference on agents.AgentCreateResponse.workflow. Done here,
# after WorkflowDetail is defined, so the single runtime import edge stays
# workflows -> agents and no import cycle forms.
from .agents import AgentCreateResponse  # noqa: E402

AgentCreateResponse.model_rebuild(_types_namespace={"WorkflowDetail": WorkflowDetail})
