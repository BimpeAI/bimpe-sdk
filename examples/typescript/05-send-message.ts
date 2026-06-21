// Send a message into a conversation, or open a thread by channel address.
import { BimpeAI } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '' });
const [agentId, conversationId, ...rest] = process.argv.slice(2);
if (!agentId || rest.length === 0) {
  throw new Error(
    'usage: 05-send-message.ts <agentId> [conversationId] <message> — omit conversationId to send by channel env vars',
  );
}

const message =
  conversationId && rest.length > 0 ? rest.join(' ') : [conversationId, ...rest].join(' ');

if (conversationId && rest.length > 0) {
  const sent = await client.conversations.messages.send(agentId, conversationId, { message });
  console.log(`sent message ${sent.id}`);
} else {
  const channelType = process.env.BIMPEAI_CHANNEL_TYPE as
    | 'whatsapp'
    | 'webchat'
    | 'telephony'
    | undefined;
  const channelUserId = process.env.BIMPEAI_CHANNEL_USER_ID;
  if (!channelType || !channelUserId) {
    throw new Error('Set BIMPEAI_CHANNEL_TYPE and BIMPEAI_CHANNEL_USER_ID for unified send');
  }
  const sent = await client.conversations.createOrSendMessage(agentId, {
    message,
    channel_type: channelType,
    channel_user_id: channelUserId,
    is_test_channel: process.env.BIMPEAI_IS_TEST_CHANNEL === 'true',
  });
  console.log(`sent message ${sent.id} on conversation ${sent.conversation_id}`);
}
