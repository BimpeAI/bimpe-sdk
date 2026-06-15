import os

from bimpeai import BimpeAI, RateLimitError

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""), max_retries=0)
try:
    client.agents.list()
except RateLimitError as err:
    print(f"rate limited; retry in {err.retry_after}s, remaining {err.remaining}")
