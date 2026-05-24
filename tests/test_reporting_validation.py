import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from PIL import Image

from tdt.cli.main import main
from tdt.datasets.registry import load_config
from tdt.datasets.validation import validate_dataset
from tdt.reporting.dataset_report import generate_dataset_report


def _write_configured_dataset(tmp_path: Path, *, mismatched: bool = False, unknown: bool = False):
    images = tmp_path / "images"
    masks = tmp_path / "masks"
    images.mkdir()
    masks.mkdir()
    Image.fromarray(np.zeros((8, 8, 3), dtype=np.uint8)).save(images / "sample.png")
    mask_shape = (7, 8) if mismatched else (8, 8)
    mask = np.zeros(mask_shape, dtype=np.uint8)
    mask[1:4, 1:4] = 9 if unknown else 1
    Image.fromarray(mask).save(masks / "sample.png")
    path = tmp_path / "dataset.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "name": "small",
                "paths": {"images": str(images), "masks": str(masks)},
                "annotation": {"format": "mask", "background_id": 0},
                "analysis": {
                    "ignore_index": 255,
                    "morphology": {"connectivity": 2, "min_area_px": 2},
                },
                "classes": [
                    {"id": 0, "name": "background", "color": [0, 0, 0]},
                    {"id": 1, "name": "crack", "color": [255, 0, 0]},
                ],
            }
        ),
        encoding="utf-8",
    )
    return load_config(path)


def test_dataset_report_records_morphology_policy_and_pixel_schema(tmp_path: Path):
    config = _write_configured_dataset(tmp_path)
    out = tmp_path / "report"

    report = generate_dataset_report(config, out, with_morphology=True, show_progress=False)

    metadata = json.loads((out / "analysis_metadata.json").read_text(encoding="utf-8"))
    descriptors = pd.read_csv(out / "morphology_descriptors.csv")
    assert report.exists()
    assert metadata["morphology_policy"]["units"] == "pixels"
    assert metadata["morphology_policy"]["min_area_px"] == 2
    assert {"area_px", "perimeter_px", "mean_width_px"} <= set(descriptors.columns)


def test_validation_reports_mismatched_size_and_unknown_id(tmp_path: Path):
    config = _write_configured_dataset(tmp_path, mismatched=True, unknown=True)

    issues = validate_dataset(config)

    assert any("size mismatch" in issue for issue in issues)
    assert any("Unknown class id" in issue for issue in issues)


def test_cli_rejects_invalid_dataset_before_analysis(tmp_path: Path, capsys):
    _write_configured_dataset(tmp_path, unknown=True)

    status = main(["analyze", str(tmp_path / "dataset.yaml"), "--out", str(tmp_path / "out")])

    captured = capsys.readouterr()
    assert status == 1
    assert "Dataset validation failed" in captured.err


def test_repository_example_analysis_smoke(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    if not (root / "configs" / "example_data.yaml").exists():
        pytest.skip("Licensed repository example assets are not included in distribution archives.")

    status = main(
        [
            "analyze",
            str(root / "configs" / "example_data.yaml"),
            "--out",
            str(tmp_path / "example_report"),
            "--no-progress",
        ]
    )

    assert status == 0
    assert (tmp_path / "example_report" / "analysis_metadata.json").exists()
