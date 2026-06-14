from bimpeai._models import PaginationMeta
from bimpeai.pagination import AsyncPage, Page


def meta(current: int, has_next: bool) -> PaginationMeta:
    return PaginationMeta(
        total_count=5,
        page_count=3,
        current_page=current,
        limit=2,
        has_next_page=has_next,
        has_previous_page=current > 1,
    )


_PAGES = {1: [1, 2], 2: [3, 4], 3: [5]}


def fetch(page: int) -> Page[int]:
    return Page(data=_PAGES[page], meta=meta(page, page < 3), request_id=f"r{page}", fetcher=fetch)


def test_fields_and_next() -> None:
    page = fetch(1)
    assert page.data == [1, 2]
    assert page.request_id == "r1"
    assert page.has_next_page is True
    assert fetch(3).get_next_page() is None


def test_iterates_all_items() -> None:
    assert list(fetch(1)) == [1, 2, 3, 4, 5]


def test_pages_iteration() -> None:
    assert [p.data for p in fetch(1).pages()] == [[1, 2], [3, 4], [5]]


def test_early_break() -> None:
    seen: list[int] = []
    for item in fetch(1):
        seen.append(item)
        if item == 3:
            break
    assert seen == [1, 2, 3]


async def afetch(page: int) -> AsyncPage[int]:
    return AsyncPage(
        data=_PAGES[page], meta=meta(page, page < 3), request_id=f"r{page}", fetcher=afetch
    )


async def test_async_iteration() -> None:
    first = await afetch(1)
    assert [item async for item in first] == [1, 2, 3, 4, 5]
    assert await (await afetch(3)).get_next_page() is None
