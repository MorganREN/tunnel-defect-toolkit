"""Static dashboard helpers."""

from __future__ import annotations

from pathlib import Path


def write_static_html(title: str, body: str, output_path: str | Path) -> None:
    """Write a minimal static HTML dashboard."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; }}
    table {{ border-collapse: collapse; margin: 16px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  {body}
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")
