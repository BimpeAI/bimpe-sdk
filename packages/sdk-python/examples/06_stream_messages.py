import os
import sys

from bimpeai import BimpeAI

if len(sys.argv) < 3:
    raise SystemExit("usage: 06_stream_messages.py <agent_id> <conversation_id>")

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
for message in client.conversations.messages.stream(sys.argv[1], sys.argv[2]):
    print(f"[{message.role}] {message.message or ''}")
