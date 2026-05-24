"""Verify that built distributions contain only the declared V1 package surface."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

ALLOWED_PACKAGE_DIRECTORIES = {
    "analysis",
    "cli",
    "datasets",
    "preprocessing",
    "reporting",
    "utils",
    "visualization",
}
ALLOWED_PREPROCESSING_FILES = {"__init__.py", "tile_dataset.py", "tiling.py"}
ALLOWED_REPORTING_FILES = {"__init__.py", "dataset_report.py", "html.py", "schemas.py"}


def _check_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    directories = {
        name.split("/")[1]
        for name in names
        if name.startswith("tdt/") and name.count("/") >= 2
    }
    assert directories <= ALLOWED_PACKAGE_DIRECTORIES, directories - ALLOWED_PACKAGE_DIRECTORIES
    assert _directory_files(names, "tdt/preprocessing/") <= ALLOWED_PREPROCESSING_FILES
    assert _directory_files(names, "tdt/reporting/") <= ALLOWED_REPORTING_FILES
    assert not any(name.startswith(("configs/", "docs/", "examples/")) for name in names)


def _check_sdist(path: Path) -> None:
    with tarfile.open(path) as archive:
        names = archive.getnames()
    normalized = [name.split("/", 1)[1] for name in names if "/" in name]
    directories = {
        name.split("/")[1]
        for name in normalized
        if name.startswith("tdt/") and name.count("/") >= 2
    }
    assert directories <= ALLOWED_PACKAGE_DIRECTORIES, directories - ALLOWED_PACKAGE_DIRECTORIES
    assert _directory_files(normalized, "tdt/preprocessing/") <= ALLOWED_PREPROCESSING_FILES
    assert _directory_files(normalized, "tdt/reporting/") <= ALLOWED_REPORTING_FILES
    required = {
        "configs/labelme_template.yaml",
        "docs/v1_scope.md",
    }
    assert required <= set(normalized), required - set(normalized)
    assert not any(
        name.startswith(("examples/example_data/", "configs/example_data.yaml"))
        for name in normalized
    )


def _directory_files(names: list[str], prefix: str) -> set[str]:
    return {
        name[len(prefix) :]
        for name in names
        if name.startswith(prefix) and "/" not in name[len(prefix) :]
    }


def main(paths: list[str]) -> int:
    for value in paths:
        path = Path(value)
        if path.suffix == ".whl":
            _check_wheel(path)
        elif path.name.endswith(".tar.gz"):
            _check_sdist(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
