export interface PhoneNumber {
  readonly id: string;
  readonly agent_id: string | null;
  readonly label: string | null;
  readonly e164: string;
}

export interface PhoneNumberDetail extends PhoneNumber {
  readonly created_at: string;
  readonly updated_at: string;
  readonly inbound_enabled: boolean;
}

export type PhoneNumberRegion = 'us' | 'uk' | 'eu' | 'ng';

export interface CreatePhoneNumberRequestBody {
  business_name: string;
  intended_use: string;
  region: PhoneNumberRegion;
  agent_count: number;
  outbound_minutes: number;
  submitted_by_agent_id?: string;
}

export interface UpdatePhoneNumberBody {
  agent_id?: string | null;
  label?: string;
}
