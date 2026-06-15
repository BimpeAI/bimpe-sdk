// Stream new messages in a conversation in real time. Press Ctrl-C to stop.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });
const [agentId, conversationId] = process.argv.slice(2);
if (!agentId || !conversationId) {
  throw new Error('usage: 06-stream-messages.ts <agentId> <conversationId>');
}

const controller = new AbortController();
process.on('SIGINT', () => controller.abort());

for await (const message of client.conversations.messages.stream(agentId, conversationId, {
  signal: controller.signal,
})) {
  console.log(`[${message.role}] ${message.message ?? ''}`);
}
