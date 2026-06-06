// List the first page of agents in your team.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });

const page = await client.agents.list({ limit: 50, sort: '-created_at' });
for (const agent of page.data) console.log(agent.id, agent.name);
console.log(`total: ${page.meta?.total_count}`);
