"""Morphology descriptors for tunnel defect masks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from skimage.measure import label, regionprops
from skimage.morphology import medial_axis, skeletonize


@dataclass(frozen=True)
class MorphologyDescriptor:
    """Shape descriptors for one connected defect instance."""

    class_id: int
    instance_id: int
    area: int
    perimeter: float
    compactness: float
    elongation: float
    eccentricity: float
    solidity: float
    bbox_width: int
    bbox_height: int
    skeleton_length: int
    mean_width: float
    orientation: float


def describe_instances(mask: np.ndarray, class_ids: list[int] | set[int]) -> list[MorphologyDescriptor]:
    """Compute morphology descriptors for connected components in a semantic mask."""

    descriptors: list[MorphologyDescriptor] = []
    for class_id in sorted(class_ids):
        binary = np.asarray(mask) == class_id
        labeled = label(binary, connectivity=2)
        for instance_index, region in enumerate(regionprops(labeled), start=1):
            if region.area <= 0:
                continue
            component = labeled == region.label
            perimeter = float(region.perimeter)
            compactness = _compactness(area=float(region.area), perimeter=perimeter)
            if hasattr(region, "axis_major_length"):
                major_axis = region.axis_major_length
                minor_axis = region.axis_minor_length
            else:
                major_axis = region.major_axis_length
                minor_axis = region.minor_axis_length
            elongation = _elongation(major_axis, minor_axis)
            skeleton = skeletonize(component)
            _, distance = medial_axis(component, return_distance=True)
            widths = 2.0 * distance[skeleton]
            min_row, min_col, max_row, max_col = region.bbox
            descriptors.append(
                MorphologyDescriptor(
                    class_id=int(class_id),
                    instance_id=instance_index,
                    area=int(region.area),
                    perimeter=perimeter,
                    compactness=compactness,
                    elongation=elongation,
                    eccentricity=float(region.eccentricity),
                    solidity=float(region.solidity),
                    bbox_width=int(max_col - min_col),
                    bbox_height=int(max_row - min_row),
                    skeleton_length=int(np.count_nonzero(skeleton)),
                    mean_width=float(np.mean(widths)) if widths.size else 0.0,
                    orientation=float(region.orientation),
                )
            )
    return descriptors


def _compactness(area: float, perimeter: float) -> float:
    if perimeter <= 0:
        return 0.0
    return float(4.0 * np.pi * area / (perimeter * perimeter))


def _elongation(major_axis: float, minor_axis: float) -> float:
    if minor_axis <= 1e-8:
        return float("inf") if major_axis > 0 else 0.0
    return float(major_axis / minor_axis)
