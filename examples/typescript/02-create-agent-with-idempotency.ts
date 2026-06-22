// Create an agent with an idempotency key. Re-running this script with the same
// key returns the original agent rather than creating a duplicate.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });
const workflowId = process.argv[2];
if (!workflowId) throw new Error('usage: 02-create-agent-with-idempotency.ts <workflowId>');

const agent = await client.agents.create(
  { workflow_id: workflowId, name: 'Support bot', description: 'Tier 1 support' },
  { idempotencyKey: 'create-support-bot-v1' },
);
console.log(`created ${agent.id}`);
