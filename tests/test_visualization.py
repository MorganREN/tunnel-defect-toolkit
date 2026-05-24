import numpy as np

from tdt.visualization.overlay import overlay_mask


def test_overlay_respects_configured_background_id():
    image = np.full((2, 2, 3), 100, dtype=np.uint8)
    mask = np.array([[7, 1], [7, 7]], dtype=np.uint8)

    output = overlay_mask(
        image,
        mask,
        color_map={1: (255, 0, 0), 7: (0, 0, 0)},
        alpha=1.0,
        background_id=7,
    )

    assert np.array_equal(output[0, 0], image[0, 0])
    assert np.array_equal(output[0, 1], np.array([255, 0, 0], dtype=np.uint8))
