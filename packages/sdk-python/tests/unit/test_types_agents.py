from bimpeai.types.agents import Agent, AgentDetail, KnowledgeBaseSummary


def test_agent_parses_and_tolerates_extra() -> None:
    agent = Agent.model_validate(
        {
            "id": "a_1",
            "name": "Bot",
            "description": "A support bot",
            "persona": "friendly",
            "status": "live",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "future_field": 1,
        }
    )
    assert agent.id == "a_1"
    assert agent.name == "Bot"
    assert agent.description == "A support bot"
    assert agent.persona == "friendly"


def test_agent_detail_has_nested_lists() -> None:
    detail = AgentDetail.model_validate(
        {
            "id": "a_1",
            "name": "Bot",
            "description": "A support bot",
            "created_at": "t",
            "updated_at": "t",
            "integrations": [
                {
                    "id": "i_1",
                    "type": "slack",
                    "name": "Slack",
                    "status": "ok",
                    "is_connected": True,
                }
            ],
            "channels": [
                {
                    "id": "c_1",
                    "type": "whatsapp",
                    "name": "WhatsApp",
                    "status": "ok",
                    "is_connected": True,
                }
            ],
            "knowledge_bases": [{"id": "k_1", "type": "text", "name": "FAQ", "description": None}],
        }
    )
    assert isinstance(detail.knowledge_bases[0], KnowledgeBaseSummary)
    assert detail.knowledge_bases[0].type == "text"
    assert detail.integrations[0].type == "slack"
    assert detail.channels[0].type == "whatsapp"
