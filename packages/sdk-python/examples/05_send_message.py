import os
import sys

from bimpeai import BimpeAI

if len(sys.argv) < 4:
    raise SystemExit("usage: 05_send_message.py <agent_id> <conversation_id> <message>")

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
sent = client.conversations.messages.send(sys.argv[1], sys.argv[2], message=" ".join(sys.argv[3:]))
print("sent", sent.id)
