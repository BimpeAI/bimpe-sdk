import asyncio
import os

from bimpeai import AsyncBimpeAI


async def main() -> None:
    async with AsyncBimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", "")) as client:
        page = await client.agents.list(limit=50)
        async for agent in page:
            print(agent.id, agent.name)


asyncio.run(main())
