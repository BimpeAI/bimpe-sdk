// Walk every WhatsApp conversation on an agent. Pages are fetched on demand.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });
const agentId = process.argv[2];
if (!agentId) throw new Error('usage: 03-paginate-conversations.ts <agentId>');

let count = 0;
for await (const conversation of client.conversations.list(agentId, {
  channel: 'whatsapp',
  limit: 100,
})) {
  count += 1;
  if (count % 100 === 0) console.log(`seen ${count}`, conversation.id);
}
console.log(`total whatsapp conversations: ${count}`);
