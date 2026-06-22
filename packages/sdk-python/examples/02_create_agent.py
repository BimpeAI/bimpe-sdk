import os

from bimpeai import BimpeAI

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
agent = client.agents.create(
    workflow_id="wf_support",
    name="Support bot",
    description="Tier 1 support",
    persona="professional",
    idempotency_key="create-support-bot-v1",
)
print("created", agent.id)
