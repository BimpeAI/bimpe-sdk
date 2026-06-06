export type ConversationChannel =
  | 'whatsapp'
  | 'messenger'
  | 'instagram'
  | 'webchat'
  | 'test_whatsapp'
  | 'test_messenger'
  | 'test_instagram';

export interface Conversation {
  readonly id: string;
  readonly channel_type: string;
  readonly channel_id: string | null;
  readonly is_test_channel: boolean;
  readonly full_name: string | null;
  readonly email: string | null;
  readonly phone_number: string | null;
  readonly channel_username: string | null;
  readonly is_ai_chat_paused: boolean;
  readonly last_message_at: string | null;
  readonly last_message_preview: string | null;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface ListConversationsQuery {
  page?: number;
  limit?: number;
  search?: string;
  channel?: ConversationChannel;
}

export interface Message {
  readonly id: string;
  readonly role: string;
  readonly message: string | null;
  readonly message_type: string | null;
  readonly created_at: string;
}

export interface MessageAttachment {
  type: string;
  url: string;
}

export interface SendMessageBody {
  message: string;
  attachments?: MessageAttachment[];
}

export interface ListMessagesQuery {
  page?: number;
  limit?: number;
}
