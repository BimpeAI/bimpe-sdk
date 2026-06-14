import os

from bimpeai import BimpeAI

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
page = client.agents.list(limit=50, sort="-created_at")
for agent in page:
    print(agent.id, agent.name)
