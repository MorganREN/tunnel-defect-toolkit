import numpy as np

from tdt.analysis.morphology import describe_instances
from tdt.analysis.morphology_table import MORPHOLOGY_COLUMNS, _to_sorted_frame, resolve_worker_count


def test_describe_instances_returns_descriptors():
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[1:6, 3] = 1
    mask[2:5, 5:7] = 2

    descriptors = describe_instances(mask, class_ids={1, 2})

    assert len(descriptors) == 2
    assert {item.class_id for item in descriptors} == {1, 2}
    assert all(item.area_px > 0 for item in descriptors)
    assert all(item.skeleton_length_px > 0 for item in descriptors)


def test_connectivity_and_minimum_area_define_connected_regions():
    mask = np.zeros((5, 5), dtype=np.uint8)
    mask[1, 1] = 1
    mask[2, 2] = 1
    mask[4, 4] = 1

    four_connected = describe_instances(mask, {1}, connectivity=1)
    eight_connected = describe_instances(mask, {1}, connectivity=2)
    filtered = describe_instances(mask, {1}, connectivity=2, min_area_px=2)

    assert len(four_connected) == 3
    assert len(eight_connected) == 2
    assert len(filtered) == 1
    assert filtered[0].area_px == 2


def test_resolve_worker_count_accepts_auto_and_integer_strings():
    assert resolve_worker_count("1") == 1
    assert resolve_worker_count(2) == 2
    assert resolve_worker_count("auto") >= 1


def test_empty_morphology_table_retains_output_schema():
    assert list(_to_sorted_frame([]).columns) == MORPHOLOGY_COLUMNS
