from tdt.preprocessing.tiling import plan_tiles


def test_plan_tiles_covers_image_edges():
    tiles = plan_tiles(width=10, height=10, tile_size=(6, 6), stride=(4, 4), source_id="x")

    assert tiles[0].box.x0 == 0
    assert tiles[-1].box.x1 == 10
    assert tiles[-1].box.y1 == 10
