import uuid


def generate_request_id() -> str:
    return str(uuid.uuid4())
