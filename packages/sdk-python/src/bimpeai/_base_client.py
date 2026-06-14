from __future__ import annotations

import json
import platform
from typing import Any

import httpx

from ._exceptions import UserError, map_api_error
from ._models import ApiResponse, unwrap_envelope
from ._version import __version__

API_PATH_PREFIX = "/api/v1/console"
DEFAULT_BASE_URL = "https://api.bimpeai.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2


class BaseClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        if not api_key:
            raise UserError("api_key is required")
        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._default_headers = dict(default_headers or {})
        self._user_agent = _build_user_agent()

    def build_url(self, path: str) -> str:
        return f"{self._base_url}{API_PATH_PREFIX}{path}"

    def clean_params(self, query: dict[str, Any] | None) -> dict[str, str]:
        out: dict[str, str] = {}
        for key, value in (query or {}).items():
            if value is None:
                continue
            out[key] = "true" if value is True else "false" if value is False else str(value)
        return out

    def build_headers(
        self,
        *,
        has_body: bool,
        idempotency_key: str | None,
        request_id: str,
        extra: dict[str, str] | None,
    ) -> httpx.Headers:
        headers = httpx.Headers(self._default_headers)
        headers["Authorization"] = f"Bearer {self._api_key}"
        headers["Accept"] = "application/json"
        headers["User-Agent"] = self._user_agent
        headers["X-Request-Id"] = request_id
        if has_body:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        if extra:
            for key, value in extra.items():
                headers[key] = value
        return headers

    def parse_response(self, response: httpx.Response, request_id: str) -> ApiResponse[Any]:
        text = response.text
        parsed = _safe_json(text) if text else None
        if not response.is_success:
            raise map_api_error(response.status_code, parsed, response.headers)
        unwrapped = unwrap_envelope(parsed)
        return ApiResponse(
            data=unwrapped.data,
            meta=unwrapped.meta,
            request_id=response.headers.get("x-request-id") or request_id,
            status=response.status_code,
            headers=response.headers,
        )


def _build_user_agent() -> str:
    return f"bimpeai-python/{__version__} (Python/{platform.python_version()}; {platform.system()})"


def _safe_json(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return None
