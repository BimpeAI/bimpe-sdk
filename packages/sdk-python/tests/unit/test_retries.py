import httpx

from bimpeai._exceptions import APIConnectionError, APITimeoutError, map_api_error
from bimpeai._retries import DEFAULT_BASE_S, DEFAULT_MAX_BACKOFF_S, compute_backoff, should_retry


def err(status: int) -> object:
    return map_api_error(status, {"message": "x"}, httpx.Headers())


def test_retries_connection_and_timeout() -> None:
    assert should_retry(APIConnectionError(), 0, 2)
    assert should_retry(APITimeoutError(), 0, 2)


def test_retries_408_429_5xx_except_501() -> None:
    assert should_retry(err(408), 0, 2)
    assert should_retry(err(429), 0, 2)
    assert should_retry(err(500), 0, 2)
    assert should_retry(err(503), 0, 2)
    assert not should_retry(err(501), 0, 2)


def test_does_not_retry_409_or_other_4xx() -> None:
    assert not should_retry(err(409), 0, 2)
    assert not should_retry(err(400), 0, 2)
    assert not should_retry(err(404), 0, 2)


def test_stops_at_max() -> None:
    assert should_retry(err(500), 1, 2)
    assert not should_retry(err(500), 2, 2)


def test_non_bimpe_error_not_retried() -> None:
    assert not should_retry(ValueError("x"), 0, 2)


def test_backoff_growth_and_cap() -> None:
    assert compute_backoff(0) > 0
    assert compute_backoff(20) <= DEFAULT_MAX_BACKOFF_S
    assert compute_backoff(0, retry_after_s=3.0) == 3.0
    assert compute_backoff(0, retry_after_s=99.0) == DEFAULT_MAX_BACKOFF_S
    assert DEFAULT_BASE_S == 0.5
