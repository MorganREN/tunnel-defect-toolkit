"""HTML reporting helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from tdt.visualization.dashboards import write_static_html


def dataframe_to_html_table(frame: pd.DataFrame) -> str:
    """Render a DataFrame as an HTML table."""

    return frame.to_html(index=False, escape=True, border=0)


def write_report(title: str, sections: dict[str, str], output_path: str | Path) -> None:
    """Write an HTML report from named sections."""

    body = "\n".join(f"<h2>{name}</h2>\n{content}" for name, content in sections.items())
    write_static_html(title, body, output_path)
