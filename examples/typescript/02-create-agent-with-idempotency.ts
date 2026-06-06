// Create an agent with an idempotency key. Re-running this script with the same
// key returns the original agent rather than creating a duplicate.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });

const agent = await client.agents.create(
  { name: 'Support bot', description: 'Tier 1 support' },
  { idempotencyKey: 'create-support-bot-v1' },
);
console.log(`created ${agent.id}`);
