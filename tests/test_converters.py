import json
from pathlib import Path

import numpy as np
import pytest

from tdt.datasets.converters import convert_labelme_directory, labelme_to_mask_tolerant


def _write_labelme(path: Path, *, label: str = "crack") -> Path:
    path.write_text(
        json.dumps(
            {
                "imageWidth": 8,
                "imageHeight": 8,
                "shapes": [
                    {
                        "label": label,
                        "shape_type": "polygon",
                        "points": [[1, 1], [5, 1], [5, 5], [1, 5]],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_labelme_conversion_writes_semantic_mask(tmp_path: Path):
    annotations = tmp_path / "annotations"
    annotations.mkdir()
    _write_labelme(annotations / "sample.json", label="Crack")

    outputs = convert_labelme_directory(
        annotations,
        tmp_path / "masks",
        {"crack": 1},
        show_progress=False,
    )

    assert len(outputs) == 1
    mask = labelme_to_mask_tolerant(annotations / "sample.json", {"crack": 1})
    assert int(np.max(mask)) == 1


def test_labelme_conversion_rejects_unmapped_labels(tmp_path: Path):
    annotation = _write_labelme(tmp_path / "sample.json", label="not_declared")

    with pytest.raises(ValueError, match="Unknown LabelMe label"):
        labelme_to_mask_tolerant(annotation, {"crack": 1})


def test_labelme_conversion_rejects_malformed_json(tmp_path: Path):
    annotation = tmp_path / "broken.json"
    annotation.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid LabelMe JSON"):
        labelme_to_mask_tolerant(annotation, {"crack": 1})
