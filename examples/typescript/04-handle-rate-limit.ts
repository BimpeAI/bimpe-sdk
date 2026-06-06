// Catch a RateLimitError and inspect the rate-limit headers.
import { BimpeAI, RateLimitError } from '@bimpeai/sdk';

const client = new BimpeAI({ apiKey: process.env.BIMPEAI_API_KEY ?? '', maxRetries: 0 });

try {
  await client.agents.list();
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(
      `rate limited. retry in ${error.retryAfter}s, limit ${error.limit}, remaining ${error.remaining}`,
    );
  } else {
    throw error;
  }
}
