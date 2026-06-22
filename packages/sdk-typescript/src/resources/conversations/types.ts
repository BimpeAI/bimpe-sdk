export type ConversationChannel =
  | 'whatsapp'
  | 'webchat'
  | 'telephony'
  | 'test_whatsapp'
  | 'test_webchat'
  | 'test_telephony';

export type MessageRole = 'user' | 'assistant';

export interface Conversation {
  readonly id: string;
  readonly channel_type: string;
  readonly channel_id: string | null;
  readonly channel_user_id: string | null;
  readonly channel_user_username: string | null;
  readonly is_test_channel: boolean;
  readonly is_ai_chat_paused: boolean;
  readonly needs_attention: boolean;
  readonly last_message_at: string | null;
  readonly last_seen: string | null;
  readonly last_message_preview: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface ConversationDetail extends Conversation {
  readonly full_name: string | null;
  readonly email: string | null;
  readonly phone_number: string | null;
  readonly profile_picture: string | null;
}

export interface ListConversationsQuery {
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
  channel?: ConversationChannel;
  is_test_channel?: boolean;
  is_ai_chat_paused?: boolean;
  needs_attention?: boolean;
}

export interface CreateConversationMessageBody {
  message: string;
  role?: MessageRole;
  conversation_id?: string;
  channel_type?: 'whatsapp' | 'webchat' | 'telephony';
  channel_user_id?: string;
  channel_username?: string;
  is_test_channel?: boolean;
}

export interface SetAiStatusBody {
  is_ai_chat_paused: boolean;
}

export interface ConversationAiStatus {
  readonly is_ai_chat_paused?: boolean;
}

export interface Message {
  readonly id: string;
  readonly role: string;
  readonly message: string | null;
  readonly message_type: string | null;
  readonly created_at: string;
  readonly attachments?: MessageAttachment[];
}

export interface MessageAttachment {
  type: string;
  url: string;
}

export interface SendMessageBody {
  message: string;
  role?: MessageRole;
}

export interface ListMessagesQuery {
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
}

export interface StreamTicket {
  readonly ticket: string;
  readonly expires_in: number;
}

export type StreamMessageRole = 'user' | 'assistant' | 'restaurant_user' | 'customer';

export interface StreamMessageEvent {
  readonly id: string;
  readonly conversation_id: string;
  readonly role: StreamMessageRole;
  readonly message: string | null;
  readonly message_type: string | null;
  readonly created_at: string;
}

export interface StreamHeartbeatEvent {
  readonly ts: number;
}

export interface StreamOptions {
  /** Abort to stop the stream. */
  signal?: AbortSignal;
  /** Replay messages created after this chat id or ISO-8601 timestamp. */
  after?: string;
  /** Re-open the stream after a drop, resuming from the last seen id. Default true. */
  reconnect?: boolean;
  /** Max consecutive reconnect attempts before giving up. Default 5. */
  maxRetries?: number;
}
