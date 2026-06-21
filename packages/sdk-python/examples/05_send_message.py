import os
import sys
from typing import cast

from bimpeai import BimpeAI
from bimpeai.types.conversations import CreateOrSendByChannelBody

if len(sys.argv) < 3:
    raise SystemExit(
        "usage: 05_send_message.py <agent_id> [conversation_id] <message> — "
        "omit conversation_id to send via BIMPEAI_CHANNEL_TYPE + BIMPEAI_CHANNEL_USER_ID"
    )

client = BimpeAI(api_key=os.environ.get("BIMPEAI_API_KEY", ""))
agent_id = sys.argv[1]

if len(sys.argv) >= 4:
    conversation_id = sys.argv[2]
    message = " ".join(sys.argv[3:])
    sent = client.conversations.messages.send(agent_id, conversation_id, message=message)
    print("sent", sent.id)
else:
    message = " ".join(sys.argv[2:])
    channel_type = os.environ.get("BIMPEAI_CHANNEL_TYPE")
    channel_user_id = os.environ.get("BIMPEAI_CHANNEL_USER_ID")
    if not channel_type or not channel_user_id:
        raise SystemExit("Set BIMPEAI_CHANNEL_TYPE and BIMPEAI_CHANNEL_USER_ID for unified send")
    sent = client.conversations.create_or_send(
        agent_id,
        cast(
            CreateOrSendByChannelBody,
            {
                "message": message,
                "channel_type": channel_type,
                "channel_user_id": channel_user_id,
                "is_test_channel": os.environ.get("BIMPEAI_IS_TEST_CHANNEL") == "true",
            },
        ),
    )
    print("sent", sent.id, "conversation", sent.conversation_id)
