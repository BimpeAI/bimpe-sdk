from collections.abc import AsyncIterator, Iterator

from bimpeai._sse import SseEvent, aparse_sse, parse_sse


def _bytes(chunks: list[str]) -> Iterator[bytes]:
    for chunk in chunks:
        yield chunk.encode()


async def _abytes(chunks: list[str]) -> AsyncIterator[bytes]:
    for chunk in chunks:
        yield chunk.encode()


def collect(chunks: list[str]) -> list[SseEvent]:
    return list(parse_sse(_bytes(chunks)))


def test_single_event() -> None:
    assert collect(['id: m_1\nevent: message\ndata: {"a":1}\n\n']) == [
        SseEvent(data='{"a":1}', id="m_1", event="message")
    ]


def test_multiline_data() -> None:
    assert collect(["data: a\ndata: b\n\n"])[0].data == "a\nb"


def test_comments_ignored_and_dataless_dropped() -> None:
    assert collect([": ping\n\n", "event: heartbeat\n\n", "data: x\n\n"]) == [SseEvent(data="x")]


def test_crlf_and_chunk_split() -> None:
    assert collect(["event: message\r\nda", "ta: hi\r\n", "\r\n"]) == [
        SseEvent(data="hi", event="message")
    ]


async def test_async_parse() -> None:
    events = [event async for event in aparse_sse(_abytes(["data: hi\n\n"]))]
    assert events == [SseEvent(data="hi")]
