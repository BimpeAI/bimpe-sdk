export type ConversationChannel =
  | 'whatsapp'
  | 'webchat'
  | 'telephony'
  | 'test_whatsapp'
  | 'test_webchat'
  | 'test_telephony';

export type CreateOrSendChannelType = 'whatsapp' | 'webchat' | 'telephony';

export interface ConversationListItem {
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

export interface Conversation extends ConversationListItem {
  readonly full_name: string | null;
  readonly email: string | null;
  readonly phone_number: string | null;
  readonly profile_picture: string | null;
}

export interface ListConversationsQuery {
  page?: number;
  limit?: number;
  search?: string;
  channel?: ConversationChannel;
  is_test_channel?: boolean;
  is_ai_chat_paused?: boolean;
  needs_attention?: boolean;
}

export interface MessageAttachment {
  readonly type: string;
  readonly url: string;
}

export interface Message {
  readonly id: string;
  readonly role: string;
  readonly message: string | null;
  readonly message_type: string | null;
  readonly created_at: string;
  readonly attachments?: readonly MessageAttachment[];
}

export type MessageRole = 'user' | 'assistant';

export interface SendMessageBody {
  message: string;
  role?: MessageRole;
}

export interface SendToConversationBody {
  message: string;
  role?: MessageRole;
}

export interface CreateOrSendExistingBody extends SendToConversationBody {
  conversation_id: string;
}

export interface CreateOrSendByChannelBody extends SendToConversationBody {
  channel_type: CreateOrSendChannelType;
  channel_user_id: string;
  channel_username?: string;
  is_test_channel?: boolean;
}

export type CreateOrSendMessageBody = CreateOrSendExistingBody | CreateOrSendByChannelBody;

export interface CreateOrSendMessageResponse extends Message {
  readonly conversation_id: string;
}

export interface UpdateAiStatusBody {
  is_ai_chat_paused: boolean;
}

export interface UpdateAiStatusResponse {
  readonly is_ai_chat_paused: boolean;
}

export interface ListMessagesQuery {
  page?: number;
  limit?: number;
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
