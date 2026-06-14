from typing import Any

import httpx
import pytest

from bimpeai._exceptions import APINotImplementedError
from bimpeai._request import RequestSpec
from bimpeai.resources.calls import Calls


class FakeRaise:
    def __init__(self) -> None:
        self.specs: list[RequestSpec] = []

    def request(self, spec: RequestSpec) -> Any:
        self.specs.append(spec)
        raise APINotImplementedError(
            "coming soon",
            status=501,
            code="not_implemented",
            request_id=None,
            headers=httpx.Headers(),
            body={},
        )


def test_calls_list_surfaces_not_implemented() -> None:
    client = FakeRaise()
    with pytest.raises(APINotImplementedError):
        Calls(client).list()
    assert client.specs[-1] == RequestSpec(method="GET", path="/calls")
