export type CallStatus =
  | 'queued'
  | 'ringing'
  | 'answered'
  | 'ended'
  | 'busy'
  | 'failed'
  | 'cancelled';

export interface Call {
  readonly id: string;
  readonly source: string | null;
  readonly destination: string;
  readonly status: CallStatus;
  readonly direction: string;
  readonly created_on: string;
  readonly duration_seconds: number | null;
  readonly is_test_call: boolean;
  readonly error_reason: string | null;
  readonly end_reason: string | null;
  readonly ringing_at: string | null;
  readonly ended_at: string | null;
}

export interface CallMessageAttachment {
  type: string;
  url: string;
}

export interface CallMessage {
  readonly id: string;
  readonly role: string;
  readonly message?: string | null;
  readonly message_type?: string | null;
  readonly created_at: string;
  readonly attachments?: readonly CallMessageAttachment[];
}

export interface CallDetail extends Call {
  readonly started_at: string | null;
  readonly answered_at: string | null;
  readonly conversation_logs: readonly CallMessage[];
}

export interface ListCallsQuery {
  page?: number;
  limit?: number;
  search?: string;
  sort?: string;
  is_test_call?: boolean;
  status?: CallStatus;
}

export interface MakeCallBody {
  destination: string;
  is_test_call: boolean;
}

export type MakeCallStatus = 'initiated' | 'busy' | 'failed';

export interface MakeCallResult {
  readonly status: MakeCallStatus;
  readonly call_id?: string;
  readonly detail?: string;
}
