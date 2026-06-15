from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import httpx

from ._base_client import BaseClient, safe_json
from ._exceptions import (
    APIConnectionError,
    APITimeoutError,
    BimpeAIError,
    RateLimitError,
    map_api_error,
)
from ._idempotency import resolve_idempotency_key
from ._models import ApiResponse
from ._request import RequestSpec, StreamSpec
from ._request_id import generate_request_id
from ._retries import compute_backoff, should_retry
from .resources.agents import Agents
from .resources.calls import Calls
from .resources.conversations import Conversations
from .resources.workflows import Workflows

_WRITE_METHODS = frozenset({"POST", "PATCH", "PUT", "DELETE"})


class BimpeAI(BaseClient):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        default_headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
        )
        self._http = http_client if http_client is not None else httpx.Client()
        self._owns_http = http_client is None
        self.agents = Agents(self)
        self.workflows = Workflows(self)
        self.conversations = Conversations(self)
        self.calls = Calls(self)

    def request(self, spec: RequestSpec) -> ApiResponse[Any]:
        url = self.build_url(spec.path)
        params = self.clean_params(spec.query)
        options = spec.options
        max_retries = self._max_retries if options.max_retries is None else options.max_retries
        timeout = self._timeout if options.timeout is None else options.timeout
        idempotency_key = (
            resolve_idempotency_key(options.idempotency_key, max_retries)
            if spec.method in _WRITE_METHODS
            else None
        )
        request_id = _resolve_request_id(options.headers)

        attempt = 0
        while True:
            try:
                return self._send(spec, url, params, idempotency_key, request_id, timeout)
            except BimpeAIError as error:
                if not should_retry(error, attempt, max_retries):
                    raise
                retry_after = error.retry_after if isinstance(error, RateLimitError) else None
                time.sleep(compute_backoff(attempt, retry_after_s=retry_after))
                attempt += 1

    def _send(
        self,
        spec: RequestSpec,
        url: str,
        params: dict[str, str],
        idempotency_key: str | None,
        request_id: str,
        timeout: float,
    ) -> ApiResponse[Any]:
        headers = self.build_headers(
            has_body=spec.body is not None,
            idempotency_key=idempotency_key,
            request_id=request_id,
            extra=spec.options.headers,
        )
        try:
            response = self._http.request(
                spec.method,
                url,
                params=params or None,
                json=spec.body if spec.body is not None else None,
                headers=headers,
                timeout=timeout,
            )
        except httpx.TimeoutException as exc:
            raise APITimeoutError(cause=exc) from exc
        except httpx.RequestError as exc:
            raise APIConnectionError("network error", cause=exc) from exc
        return self.parse_response(response, request_id)

    @contextmanager
    def stream(self, spec: StreamSpec) -> Generator[httpx.Response, None, None]:
        url = self.build_url(spec.path)
        params = self.clean_params(spec.query)
        headers = httpx.Headers(self._default_headers)
        headers["Accept"] = "text/event-stream"
        headers["User-Agent"] = self._user_agent
        if spec.headers:
            for key, value in spec.headers.items():
                headers[key] = value
        try:
            with self._http.stream(
                "GET", url, params=params or None, headers=headers, timeout=spec.timeout
            ) as response:
                if not response.is_success:
                    body = response.read()
                    raise map_api_error(
                        response.status_code, safe_json(body.decode() or ""), response.headers
                    )
                yield response
        except httpx.TimeoutException as exc:
            raise APITimeoutError(cause=exc) from exc
        except httpx.RequestError as exc:
            raise APIConnectionError("stream aborted", cause=exc) from exc

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> BimpeAI:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _resolve_request_id(extra: dict[str, str] | None) -> str:
    if extra:
        for key, value in extra.items():
            if key.lower() == "x-request-id":
                return value
    return generate_request_id()
