from __future__ import annotations

import codecs
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SseEvent:
    data: str
    id: str | None = None
    event: str | None = None


class _Decoder:
    """Incrementally turn decoded SSE text into events (W3C event stream format)."""

    def __init__(self) -> None:
        self._buffer = ""
        self._id: str | None = None
        self._event: str | None = None
        self._data: list[str] = []

    def feed(self, chunk: str) -> list[SseEvent]:
        self._buffer += chunk
        out: list[SseEvent] = []
        while True:
            newline = self._buffer.find("\n")
            if newline == -1:
                break
            line = self._buffer[:newline]
            self._buffer = self._buffer[newline + 1 :]
            if line.endswith("\r"):
                line = line[:-1]
            event = self._line(line)
            if event is not None:
                out.append(event)
        return out

    def _line(self, line: str) -> SseEvent | None:
        if line == "":
            event = self._flush()
            self._id = None
            self._event = None
            self._data = []
            return event
        if line.startswith(":"):
            return None
        colon = line.find(":")
        if colon == -1:
            field, value = line, ""
        else:
            field = line[:colon]
            value = line[colon + 1 :]
            if value.startswith(" "):
                value = value[1:]
        if field == "event":
            self._event = value
        elif field == "data":
            self._data.append(value)
        elif field == "id":
            self._id = value
        return None

    def _flush(self) -> SseEvent | None:
        if not self._data:
            return None
        return SseEvent(data="\n".join(self._data), id=self._id, event=self._event)


def parse_sse(chunks: Iterator[bytes]) -> Iterator[SseEvent]:
    decoder = _Decoder()
    text = codecs.getincrementaldecoder("utf-8")()
    for chunk in chunks:
        yield from decoder.feed(text.decode(chunk))


async def aparse_sse(chunks: AsyncIterator[bytes]) -> AsyncIterator[SseEvent]:
    decoder = _Decoder()
    text = codecs.getincrementaldecoder("utf-8")()
    async for chunk in chunks:
        for event in decoder.feed(text.decode(chunk)):
            yield event
