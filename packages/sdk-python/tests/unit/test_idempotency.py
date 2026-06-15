import re

from bimpeai._idempotency import resolve_idempotency_key

UUID_V4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def test_supplied_key_wins() -> None:
    assert resolve_idempotency_key("op-1", 2) == "op-1"
    assert resolve_idempotency_key("op-2", 0) == "op-2"


def test_generates_when_retries_on() -> None:
    key = resolve_idempotency_key(None, 2)
    assert key is not None and UUID_V4.match(key)


def test_none_when_retries_off() -> None:
    assert resolve_idempotency_key(None, 0) is None
