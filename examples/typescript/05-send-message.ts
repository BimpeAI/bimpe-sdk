// Send a message into a conversation.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });
const [agentId, conversationId, ...rest] = process.argv.slice(2);
if (!agentId || !conversationId || rest.length === 0) {
  throw new Error('usage: 05-send-message.ts <agentId> <conversationId> <message>');
}

const sent = await client.conversations.messages.send(agentId, conversationId, {
  message: rest.join(' '),
});
console.log(`sent message ${sent.id}`);
