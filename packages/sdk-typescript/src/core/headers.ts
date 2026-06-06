export type HeaderInput = Headers | Record<string, string> | undefined;

export function mergeHeaders(...sources: HeaderInput[]): Headers {
  const out = new Headers();
  for (const src of sources) {
    if (!src) continue;
    if (src instanceof Headers) {
      src.forEach((value, key) => out.set(key, value));
    } else {
      for (const [key, value] of Object.entries(src)) out.set(key, value);
    }
  }
  return out;
}
