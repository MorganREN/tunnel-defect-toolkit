"""Connected-component morphology descriptors for semantic masks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from skimage.measure import label, regionprops
from skimage.morphology import medial_axis, skeletonize


@dataclass(frozen=True)
class MorphologyDescriptor:
    """Shape descriptors for one connected foreground region in pixel space."""

    class_id: int
    instance_id: int
    area_px: int
    perimeter_px: float
    compactness: float
    elongation: float
    eccentricity: float
    solidity: float
    bbox_width_px: int
    bbox_height_px: int
    skeleton_length_px: int
    mean_width_px: float
    orientation: float


def describe_instances(
    mask: np.ndarray,
    class_ids: list[int] | set[int],
    *,
    connectivity: int = 2,
    min_area_px: int = 1,
) -> list[MorphologyDescriptor]:
    """Compute descriptors for semantic-mask connected regions.

    V1 reports pixel-space quantities only. Regions of the same class that
    touch under the selected connectivity are treated as one connected region.
    """

    if connectivity not in (1, 2):
        raise ValueError("connectivity must be 1 (edge-connected) or 2 (edge-and-corner-connected).")
    if min_area_px < 1:
        raise ValueError("min_area_px must be at least 1.")

    descriptors: list[MorphologyDescriptor] = []
    for class_id in sorted(class_ids):
        binary = np.asarray(mask) == class_id
        labeled = label(binary, connectivity=connectivity)
        instance_index = 0
        for region in regionprops(labeled):
            if region.area < min_area_px:
                continue
            instance_index += 1
            # Region-local processing preserves descriptors while avoiding a
            # full-resolution skeletonization for each sparse component.
            component = region.image
            perimeter_px = float(region.perimeter)
            compactness = _compactness(area_px=float(region.area), perimeter_px=perimeter_px)
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
                    area_px=int(region.area),
                    perimeter_px=perimeter_px,
                    compactness=compactness,
                    elongation=elongation,
                    eccentricity=float(region.eccentricity),
                    solidity=float(region.solidity),
                    bbox_width_px=int(max_col - min_col),
                    bbox_height_px=int(max_row - min_row),
                    skeleton_length_px=int(np.count_nonzero(skeleton)),
                    mean_width_px=float(np.mean(widths)) if widths.size else 0.0,
                    orientation=float(region.orientation),
                )
            )
    return descriptors


def _compactness(area_px: float, perimeter_px: float) -> float:
    if perimeter_px <= 0:
        return 0.0
    return float(4.0 * np.pi * area_px / (perimeter_px * perimeter_px))


def _elongation(major_axis: float, minor_axis: float) -> float:
    if minor_axis <= 1e-8:
        return float("inf") if major_axis > 0 else 0.0
    return float(major_axis / minor_axis)
