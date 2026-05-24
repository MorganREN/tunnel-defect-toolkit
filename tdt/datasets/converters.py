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

    path = Path(labelme_json)
    data = _read_labelme_document(path)
    height = int(data["imageHeight"])
    width = int(data["imageWidth"])
    mask_image = Image.new("L", (width, height), color=int(background_id))
    draw = ImageDraw.Draw(mask_image)

    for class_id, points in _mapped_polygons(data, class_to_id, path):
        draw.polygon(points, fill=int(class_id))

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
    if not Path(annotation_dir).exists():
        raise FileNotFoundError(f"Annotation directory does not exist: {annotation_dir}")
    if not annotations:
        raise ValueError(f"No LabelMe JSON files found in: {annotation_dir}")
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
    if not Path(annotation_dir).exists():
        raise FileNotFoundError(f"Annotation directory does not exist: {annotation_dir}")
    if not annotations:
        raise ValueError(f"No LabelMe JSON files found in: {annotation_dir}")
    tolerant_mapping = build_label_mapping(class_to_id)
    categories: list[dict[str, int | str]] = [
        {"id": int(class_id), "name": str(label), "supercategory": "defect"}
        for label, class_id in sorted(class_to_id.items(), key=lambda item: item[1])
        if int(class_id) != background_id
    ]
    seen_category_ids: set[int] = set()
    deduped_categories = []
    for category in categories:
        category_id = int(category["id"])
        if category_id in seen_category_ids:
            continue
        seen_category_ids.add(category_id)
        deduped_categories.append(category)

    coco: dict[str, Any] = {"images": [], "annotations": [], "categories": deduped_categories}
    annotation_id = 1
    for image_id, path in enumerate(annotations, start=1):
        data = _read_labelme_document(path)
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
        for category_id, points in _mapped_polygons(data, tolerant_mapping, path):
            if int(category_id) == background_id:
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

    path = Path(labelme_json)
    data = _read_labelme_document(path)
    height = int(data["imageHeight"])
    width = int(data["imageWidth"])
    mask_image = Image.new("L", (width, height), color=int(background_id))
    draw = ImageDraw.Draw(mask_image)

    for class_id, points in _mapped_polygons(data, class_to_id, path):
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


def _read_labelme_document(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid LabelMe JSON: {path}") from error
    if not isinstance(data, dict):
        raise ValueError(f"LabelMe document must be a JSON object: {path}")
    try:
        width = int(data["imageWidth"])
        height = int(data["imageHeight"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"LabelMe document lacks valid imageWidth/imageHeight: {path}") from error
    if width <= 0 or height <= 0:
        raise ValueError(f"LabelMe image dimensions must be positive: {path}")
    if not isinstance(data.get("shapes", []), list):
        raise ValueError(f"LabelMe shapes must be a list: {path}")
    return data


def _mapped_polygons(
    data: dict[str, Any],
    class_to_id: dict[str, int],
    path: Path,
) -> list[tuple[int, list[tuple[float, float]]]]:
    polygons: list[tuple[int, list[tuple[float, float]]]] = []
    for index, shape in enumerate(data.get("shapes", [])):
        if not isinstance(shape, dict):
            raise ValueError(f"LabelMe shape {index} must be an object: {path}")
        shape_type = shape.get("shape_type", "polygon")
        if shape_type not in (None, "polygon"):
            raise ValueError(f"Only LabelMe polygon shapes are supported in V1: {path} shape {index}")
        label = str(shape.get("label", ""))
        class_id = class_to_id.get(label, class_to_id.get(_normalize_label(label)))
        if class_id is None:
            raise ValueError(f"Unknown LabelMe label '{label}' in {path} shape {index}.")
        raw_points = shape.get("points", [])
        if not isinstance(raw_points, list) or len(raw_points) < 3:
            raise ValueError(f"LabelMe polygon has fewer than three points: {path} shape {index}")
        try:
            points = [(float(point[0]), float(point[1])) for point in raw_points]
        except (IndexError, TypeError, ValueError) as error:
            raise ValueError(f"LabelMe polygon has invalid points: {path} shape {index}") from error
        polygons.append((int(class_id), points))
    return polygons
