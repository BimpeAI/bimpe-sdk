from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Generic, TypeVar

from ._models import PaginationMeta

T = TypeVar("T")


class Page(Generic[T]):
    def __init__(
        self,
        *,
        data: list[T],
        meta: PaginationMeta | None,
        request_id: str | None,
        fetcher: Callable[[int], Page[T]],
    ) -> None:
        self.data = data
        self.meta = meta
        self.request_id = request_id
        self._fetcher = fetcher

    @property
    def has_next_page(self) -> bool:
        return self.meta is not None and self.meta.has_next_page

    def get_next_page(self) -> Page[T] | None:
        if self.meta is None or not self.meta.has_next_page:
            return None
        return self._fetcher(self.meta.current_page + 1)

    def __iter__(self) -> Iterator[T]:
        page: Page[T] | None = self
        while page is not None:
            yield from page.data
            page = page.get_next_page()

    def pages(self) -> Iterator[Page[T]]:
        page: Page[T] | None = self
        while page is not None:
            yield page
            page = page.get_next_page()


class AsyncPage(Generic[T]):
    def __init__(
        self,
        *,
        data: list[T],
        meta: PaginationMeta | None,
        request_id: str | None,
        fetcher: Callable[[int], Awaitable[AsyncPage[T]]],
    ) -> None:
        self.data = data
        self.meta = meta
        self.request_id = request_id
        self._fetcher = fetcher

    @property
    def has_next_page(self) -> bool:
        return self.meta is not None and self.meta.has_next_page

    async def get_next_page(self) -> AsyncPage[T] | None:
        if self.meta is None or not self.meta.has_next_page:
            return None
        return await self._fetcher(self.meta.current_page + 1)

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[T]:
        page: AsyncPage[T] | None = self
        while page is not None:
            for item in page.data:
                yield item
            page = await page.get_next_page()

    async def pages(self) -> AsyncIterator[AsyncPage[T]]:
        page: AsyncPage[T] | None = self
        while page is not None:
            yield page
            page = await page.get_next_page()
