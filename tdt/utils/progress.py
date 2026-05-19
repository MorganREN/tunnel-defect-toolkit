"""Progress bar helpers."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")

DESC_WIDTH = 24
BAR_WIDTH = 26
NCOLS = 92
BAR_FORMAT = (
    "{desc} {percentage:3.0f}% |{bar:" + str(BAR_WIDTH) + "}| "
    "{n_fmt:>5}/{total_fmt:<5} [{elapsed}<{remaining}]"
)


def progress(
    iterable: Iterable[T],
    *,
    total: int | None = None,
    desc: str | None = None,
    enabled: bool = True,
) -> Iterator[T]:
    """Wrap an iterable in a progress bar when enabled.

    The implementation uses tqdm when available. If tqdm is unavailable, it
    falls back to the original iterable rather than making tqdm a hard runtime
    failure point.
    """

    if not enabled:
        yield from iterable
        return

    try:
        from tqdm import tqdm
    except Exception:
        yield from iterable
        return

    yield from tqdm(
        iterable,
        total=total,
        desc=_format_desc(desc),
        unit="it",
        ascii=" #",
        dynamic_ncols=False,
        ncols=NCOLS,
        bar_format=BAR_FORMAT,
        mininterval=0.2,
        smoothing=0.05,
    )


def _format_desc(desc: str | None) -> str:
    label = desc or "Progress"
    if len(label) > DESC_WIDTH:
        label = label[: DESC_WIDTH - 1] + "."
    return f"{label:<{DESC_WIDTH}}"
