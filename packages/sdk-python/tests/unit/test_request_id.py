import re

from bimpeai._request_id import generate_request_id

UUID_V4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def test_generate_request_id_is_uuid4() -> None:
    assert UUID_V4.match(generate_request_id())


def test_generate_request_id_is_unique() -> None:
    assert len({generate_request_id() for _ in range(1000)}) == 1000
