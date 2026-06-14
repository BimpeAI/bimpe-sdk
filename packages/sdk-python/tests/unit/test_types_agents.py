from bimpeai.types.agents import Agent, AgentDetail, KnowledgeBase


def test_agent_parses_and_tolerates_extra() -> None:
    agent = Agent.model_validate(
        {
            "id": "a_1",
            "name": "Bot",
            "status": "active",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "future_field": 1,
        }
    )
    assert agent.id == "a_1"
    assert agent.name == "Bot"


def test_agent_detail_has_nested_lists() -> None:
    detail = AgentDetail.model_validate(
        {
            "id": "a_1",
            "name": "Bot",
            "status": "active",
            "created_at": "t",
            "updated_at": "t",
            "integration": [],
            "channel": [],
            "conversation_flow": [],
            "actions": [],
            "knowledge_bases": [{"id": "k_1", "type": "text", "name": "FAQ", "description": None}],
        }
    )
    assert isinstance(detail.knowledge_bases[0], KnowledgeBase)
    assert detail.knowledge_bases[0].type == "text"
