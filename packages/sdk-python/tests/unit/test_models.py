import httpx
import pytest

from bimpeai._models import PaginationMeta, unwrap_envelope


def test_unwrap_single() -> None:
    result = unwrap_envelope({"message": "ok", "data": {"id": "a_1"}})
    assert result.data == {"id": "a_1"}
    assert result.meta is None


def test_unwrap_paginated() -> None:
    result = unwrap_envelope(
        {
            "message": "ok",
            "data": [{"id": "a_1"}],
            "meta": {
                "total_count": 1,
                "page_count": 1,
                "current_page": 1,
                "limit": 20,
                "has_next_page": False,
                "has_previous_page": False,
            },
        }
    )
    assert result.data == [{"id": "a_1"}]
    assert isinstance(result.meta, PaginationMeta)
    assert result.meta.total_count == 1


def test_unwrap_null_data() -> None:
    result = unwrap_envelope({"message": "deleted", "data": None})
    assert result.data is None
    assert result.meta is None


def test_unwrap_rejects_non_envelope() -> None:
    with pytest.raises(TypeError):
        unwrap_envelope({"id": "x"})


def test_pagination_meta_tolerates_extra_fields() -> None:
    meta = PaginationMeta.model_validate(
        {
            "total_count": 1,
            "page_count": 1,
            "current_page": 1,
            "limit": 20,
            "has_next_page": False,
            "has_previous_page": False,
            "future_field": 7,
        }
    )
    assert meta.limit == 20
    assert httpx is not None  # import kept for parity with transport tests
