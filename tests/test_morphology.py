import numpy as np

from tdt.analysis.morphology import describe_instances
from tdt.analysis.morphology_table import resolve_worker_count


def test_describe_instances_returns_descriptors():
    mask = np.zeros((8, 8), dtype=np.uint8)
    mask[1:6, 3] = 1
    mask[2:5, 5:7] = 2

    descriptors = describe_instances(mask, class_ids={1, 2})

    assert len(descriptors) == 2
    assert {item.class_id for item in descriptors} == {1, 2}


def test_resolve_worker_count_accepts_auto_and_integer_strings():
    assert resolve_worker_count("1") == 1
    assert resolve_worker_count(2) == 2
    assert resolve_worker_count("auto") >= 1
