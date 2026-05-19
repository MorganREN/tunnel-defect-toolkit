"""Reporting data schemas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportArtifact:
    """A generated report artifact."""

    name: str
    path: str
    kind: str
