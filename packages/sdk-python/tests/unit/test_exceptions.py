import httpx

from bimpeai._exceptions import (
    APIError,
    APINotImplementedError,
    AuthenticationError,
    BadRequestError,
    BimpeAIError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
    map_api_error,
)


def h(d: dict[str, str] | None = None) -> httpx.Headers:
    return httpx.Headers(d or {})


def test_map_validation_error() -> None:
    err = map_api_error(400, {"message": ["name: required"], "code": "validation_error"}, h())
    assert isinstance(err, ValidationError)
    assert err.field_errors == [{"path": "name", "message": "required"}]


def test_map_bad_request() -> None:
    assert isinstance(map_api_error(400, {"message": "bad"}, h()), BadRequestError)


def test_map_status_classes() -> None:
    assert isinstance(map_api_error(401, {"message": "x"}, h()), AuthenticationError)
    assert isinstance(map_api_error(403, {"message": "x"}, h()), PermissionDeniedError)
    assert isinstance(map_api_error(404, {"message": "x"}, h()), NotFoundError)
    assert isinstance(map_api_error(409, {"message": "x"}, h()), ConflictError)
    assert isinstance(map_api_error(500, {"message": "x"}, h()), InternalServerError)
    assert isinstance(map_api_error(503, {"message": "x"}, h()), InternalServerError)
    assert isinstance(map_api_error(501, {"message": "x"}, h()), APINotImplementedError)
    assert type(map_api_error(418, {"message": "x"}, h())) is APIError


def test_rate_limit_metadata() -> None:
    err = map_api_error(
        429,
        {"message": "slow", "code": "too_many_requests"},
        h({"Retry-After": "7", "X-RateLimit-Limit": "60", "X-RateLimit-Remaining": "0"}),
    )
    assert isinstance(err, RateLimitError)
    assert err.retry_after == 7
    assert err.limit == 60
    assert err.remaining == 0
    assert err.code == "too_many_requests"


def test_request_id_prefers_header() -> None:
    err = map_api_error(500, {"message": "x", "request_id": "body"}, h({"X-Request-Id": "hdr"}))
    assert err.request_id == "hdr"
    assert isinstance(err, BimpeAIError)
