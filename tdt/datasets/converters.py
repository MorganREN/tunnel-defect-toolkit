"""Annotation conversion utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from tdt.utils.progress import progress


def labelme_to_mask(
    labelme_json: str | Path,
    class_to_id: dict[str, int],
    output_path: str | Path | None = None,
    background_id: int = 0,
) -> np.ndarray:
    """Convert one LabelMe polygon annotation to a semantic mask.

    Parameters
    ----------
    labelme_json:
        Path to a LabelMe JSON file.
    class_to_id:
        Mapping from LabelMe label names to integer class ids.
    output_path:
        Optional output image path. If provided, the mask is saved as an 8-bit
        grayscale image.
    background_id:
        Class id used for unlabeled pixels.
    """

    with Path(labelme_json).open("r", encoding="utf-8") as stream:
        data = json.load(stream)

    height = int(data["imageHeight"])
    width = int(data["imageWidth"])
    mask_image = Image.new("L", (width, height), color=int(background_id))
    draw = ImageDraw.Draw(mask_image)

    for shape in data.get("shapes", []):
        label = shape.get("label")
        if label not in class_to_id:
            continue
        points = [tuple(point) for point in shape.get("points", [])]
        if len(points) >= 3:
            draw.polygon(points, fill=int(class_to_id[label]))

    mask = np.asarray(mask_image, dtype=np.uint8)
    if output_path is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        mask_image.save(output_path)
    return mask


def build_label_mapping(class_items: dict[str, int] | list[tuple[str, int]]) -> dict[str, int]:
    """Build a tolerant LabelMe label mapping.

    Keys are matched both exactly and after normalization, where punctuation,
    whitespace, and underscores are removed and case is ignored.
    """

    items = class_items.items() if isinstance(class_items, dict) else class_items
    mapping: dict[str, int] = {}
    for label, class_id in items:
        mapping[label] = int(class_id)
        mapping[_normalize_label(label)] = int(class_id)
    return mapping


def convert_labelme_directory(
    annotation_dir: str | Path,
    output_dir: str | Path,
    class_to_id: dict[str, int],
    background_id: int = 0,
    show_progress: bool = True,
) -> list[Path]:
    """Convert all LabelMe JSON files in a directory to semantic masks."""

    annotations = sorted(Path(annotation_dir).glob("*.json"))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tolerant_mapping = build_label_mapping(class_to_id)
    outputs: list[Path] = []
    for annotation in progress(
        annotations,
        total=len(annotations),
        desc="Converting LabelMe",
        enabled=show_progress,
    ):
        mask = labelme_to_mask_tolerant(
            annotation,
            class_to_id=tolerant_mapping,
            background_id=background_id,
        )
        output_path = out / f"{annotation.stem}.png"
        Image.fromarray(mask.astype(np.uint8)).save(output_path)
        outputs.append(output_path)
    return outputs


def labelme_directory_to_coco(
    annotation_dir: str | Path,
    output_path: str | Path,
    class_to_id: dict[str, int],
    background_id: int = 0,
) -> Path:
    """Convert a directory of LabelMe JSON files to a COCO-style JSON file."""

    annotations = sorted(Path(annotation_dir).glob("*.json"))
    tolerant_mapping = build_label_mapping(class_to_id)
    categories = [
        {"id": int(class_id), "name": str(label), "supercategory": "defect"}
        for label, class_id in sorted(class_to_id.items(), key=lambda item: item[1])
        if int(class_id) != background_id
    ]
    seen_category_ids: set[int] = set()
    deduped_categories = []
    for category in categories:
        if category["id"] in seen_category_ids:
            continue
        seen_category_ids.add(category["id"])
        deduped_categories.append(category)

    coco: dict[str, Any] = {"images": [], "annotations": [], "categories": deduped_categories}
    annotation_id = 1
    for image_id, path in enumerate(annotations, start=1):
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        width = int(data["imageWidth"])
        height = int(data["imageHeight"])
        coco["images"].append(
            {
                "id": image_id,
                "file_name": data.get("imagePath") or f"{path.stem}.png",
                "width": width,
                "height": height,
            }
        )
        for shape in data.get("shapes", []):
            label = str(shape.get("label", ""))
            category_id = tolerant_mapping.get(label, tolerant_mapping.get(_normalize_label(label)))
            if category_id is None or int(category_id) == background_id:
                continue
            points = [(float(x), float(y)) for x, y in shape.get("points", [])]
            if len(points) < 3:
                continue
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            segmentation = [coord for point in points for coord in point]
            area = _polygon_area(points)
            coco["annotations"].append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": int(category_id),
                    "segmentation": [segmentation],
                    "area": area,
                    "bbox": [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)],
                    "iscrowd": 0,
                }
            )
            annotation_id += 1

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(coco, indent=2), encoding="utf-8")
    return output


def labelme_to_mask_tolerant(
    labelme_json: str | Path,
    class_to_id: dict[str, int],
    background_id: int = 0,
) -> np.ndarray:
    """Convert one LabelMe file using exact and normalized label matching."""

    with Path(labelme_json).open("r", encoding="utf-8") as stream:
        data = json.load(stream)

    height = int(data["imageHeight"])
    width = int(data["imageWidth"])
    mask_image = Image.new("L", (width, height), color=int(background_id))
    draw = ImageDraw.Draw(mask_image)

    for shape in data.get("shapes", []):
        label = str(shape.get("label", ""))
        class_id = class_to_id.get(label, class_to_id.get(_normalize_label(label)))
        if class_id is None:
            continue
        points = [tuple(point) for point in shape.get("points", [])]
        if len(points) >= 3:
            draw.polygon(points, fill=int(class_id))
    return np.asarray(mask_image, dtype=np.uint8)


def _normalize_label(label: str) -> str:
    return "".join(char.lower() for char in label if char.isalnum())


def _polygon_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        area += point[0] * next_point[1] - next_point[0] * point[1]
    return abs(area) / 2.0
