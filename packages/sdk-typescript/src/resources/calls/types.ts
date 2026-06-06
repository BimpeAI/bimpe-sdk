// The Calls API is not yet implemented upstream; the server returns 501 and the
// SDK surfaces that as NotImplementedError. This shape is a placeholder that will
// be replaced with the real schema once the endpoint ships.
export interface Call {
  readonly id: string;
}
