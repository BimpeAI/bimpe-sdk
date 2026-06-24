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

/**
 * A provisioning request. Unlike an assigned `PhoneNumber`, it has no `e164`
 * until it is fulfilled, so every field other than `id` is optional. The index
 * signature keeps any field the server adds accessible.
 */
export interface PhoneNumberRequest {
  readonly id: string;
  readonly status?: string | null;
  readonly business_name?: string | null;
  readonly intended_use?: string | null;
  readonly region?: string | null;
  readonly agent_count?: number | null;
  readonly outbound_minutes?: number | null;
  readonly e164?: string | null;
  readonly agent_id?: string | null;
  readonly label?: string | null;
  readonly created_at?: string | null;
  readonly updated_at?: string | null;
  readonly [key: string]: unknown;
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
