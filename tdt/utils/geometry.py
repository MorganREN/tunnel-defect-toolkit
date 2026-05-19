"""Geometry helpers for masks and tiles."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    """Integer image box in xyxy format."""

    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0
