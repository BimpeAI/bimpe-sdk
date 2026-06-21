// The Calls API is not yet implemented upstream; endpoints return a not_implemented envelope.
// Body shapes will be finalized when the API ships.

export interface Call {
  readonly id: string;
}

export type MakeCallBody = Record<string, unknown>;

export type QueueCallBody = Record<string, unknown>;

export interface CallsNotImplementedResponse {
  readonly message: string;
  readonly data: unknown;
  readonly code: 'not_implemented';
}
