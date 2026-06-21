import os

from bimpeai import BimpeAI

workflow_id = os.environ.get("BIMPEAI_WORKFLOW_ID")
if not workflow_id:
    raise SystemExit("Set BIMPEAI_WORKFLOW_ID to an existing workflow id")

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
agent = client.agents.create(
    workflow_id=workflow_id,
    name="Support bot",
    description="Tier 1 support",
    idempotency_key="create-support-bot-v1",
)
print("created", agent.id)
