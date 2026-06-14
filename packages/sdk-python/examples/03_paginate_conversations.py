import os
import sys

from bimpeai import BimpeAI

if len(sys.argv) < 2:
    raise SystemExit("usage: 03_paginate_conversations.py <agent_id>")

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
count = 0
for conversation in client.conversations.list(sys.argv[1], channel="whatsapp", limit=100):
    count += 1
    if count % 100 == 0:
        print("seen", count, conversation.id)
print("total whatsapp conversations:", count)
