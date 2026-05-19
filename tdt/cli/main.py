"""Command-line interface for tunnel-defect-toolkit."""

from __future__ import annotations

import argparse
from pathlib import Path

from tdt.datasets.converters import convert_labelme_directory, labelme_directory_to_coco
from tdt.datasets.manifest import collect_dataset_items, write_manifest
from tdt.datasets.registry import load_config
from tdt.datasets.split import split_dataset
from tdt.datasets.validation import validate_dataset
from tdt.preprocessing.tile_dataset import tile_dataset
from tdt.reporting.dataset_report import generate_dataset_report
from tdt.visualization.morphology_plots import save_morphology_plots
from tdt.visualization.overlay_batch import export_mask_overlays


def main(argv: list[str] | None = None) -> int:
    """Run the tdt command-line interface."""

    parser = argparse.ArgumentParser(prog="tdt")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a dataset config.")
    validate.add_argument("config", type=Path)

    manifest = subparsers.add_parser("manifest", help="Write a source image/mask manifest.")
    manifest.add_argument("config", type=Path)
    manifest.add_argument("--out", type=Path, required=True)
    manifest.add_argument("--allow-missing-masks", action="store_true")

    analyze = subparsers.add_parser("analyze", help="Generate a dataset analysis report.")
    analyze.add_argument("config", type=Path)
    analyze.add_argument("--out", type=Path, required=True)
    analyze.add_argument(
        "--with-morphology",
        action="store_true",
        help="Include full instance-level morphology descriptors. Slower on large masks.",
    )
    analyze.add_argument("--no-progress", action="store_true", help="Disable progress bars.")
    analyze.add_argument(
        "--workers",
        default="1",
        help="Worker processes for --with-morphology. Use an integer or 'auto'. Default: 1.",
    )

    convert = subparsers.add_parser("labelme-to-masks", help="Convert LabelMe JSON files to masks.")
    convert.add_argument("config", type=Path)
    convert.add_argument("--out", type=Path, default=None)
    convert.add_argument("--no-progress", action="store_true", help="Disable progress bars.")

    coco = subparsers.add_parser("labelme-to-coco", help="Convert LabelMe JSON files to COCO JSON.")
    coco.add_argument("config", type=Path)
    coco.add_argument("--out", type=Path, required=True)

    split = subparsers.add_parser("split", help="Create source-image-level dataset splits.")
    split.add_argument("config", type=Path)
    split.add_argument("--out", type=Path, default=None)
    split.add_argument("--train", type=float, default=0.7)
    split.add_argument("--val", type=float, default=0.15)
    split.add_argument("--seed", type=int, default=42)
    split.add_argument("--allow-missing-masks", action="store_true")

    tile = subparsers.add_parser("tile", help="Generate image/mask tiles and a tile manifest.")
    tile.add_argument("config", type=Path)
    tile.add_argument("--out", type=Path, required=True)
    tile.add_argument("--tile-size", default=None, help="Tile size as WIDTHxHEIGHT, e.g. 1024x1024.")
    tile.add_argument("--stride", default=None, help="Stride as WIDTHxHEIGHT, e.g. 768x768.")
    tile.add_argument("--no-progress", action="store_true", help="Disable progress bars.")

    overlay = subparsers.add_parser("overlay", help="Export image/mask overlay figures.")
    overlay.add_argument("config", type=Path)
    overlay.add_argument("--out", type=Path, required=True)
    overlay.add_argument("--limit", type=int, default=None)
    overlay.add_argument("--alpha", type=float, default=0.45)
    overlay.add_argument("--no-progress", action="store_true", help="Disable progress bars.")

    plot_morphology = subparsers.add_parser(
        "plot-morphology",
        help="Generate morphology plots from morphology_descriptors.csv.",
    )
    plot_morphology.add_argument("csv", type=Path)
    plot_morphology.add_argument("--out", type=Path, required=True)
    plot_morphology.add_argument(
        "--formats",
        default="png",
        help="Comma-separated output formats, e.g. png,pdf. Default: png.",
    )

    args = parser.parse_args(argv)

    if args.command == "validate":
        config = load_config(args.config)
        issues = validate_dataset(config)
        if issues:
            for issue in issues:
                print(f"ERROR: {issue}")
            return 1
        print(f"OK: {config.name}")
        return 0

    if args.command == "manifest":
        config = load_config(args.config)
        items = collect_dataset_items(config, require_masks=not args.allow_missing_masks)
        output = write_manifest(items, args.out)
        print(output)
        return 0

    if args.command == "analyze":
        config = load_config(args.config)
        report_path = generate_dataset_report(
            config,
            args.out,
            with_morphology=args.with_morphology,
            show_progress=not args.no_progress,
            morphology_workers=args.workers,
        )
        print(report_path)
        return 0

    if args.command == "labelme-to-masks":
        config = load_config(args.config)
        if config.paths.annotations is None:
            print("ERROR: config.paths.annotations is required.")
            return 1
        output_dir = args.out or config.paths.masks
        if output_dir is None:
            print("ERROR: provide --out or config.paths.masks.")
            return 1
        label_items = []
        for class_info in config.classes:
            label_items.append((class_info.name, class_info.id))
            for alias in class_info.aliases:
                label_items.append((alias, class_info.id))
        outputs = convert_labelme_directory(
            config.paths.annotations,
            output_dir,
            dict(label_items),
            background_id=config.background_id,
            show_progress=not args.no_progress,
        )
        print(f"Converted {len(outputs)} masks to {output_dir}")
        return 0

    if args.command == "labelme-to-coco":
        config = load_config(args.config)
        if config.paths.annotations is None:
            print("ERROR: config.paths.annotations is required.")
            return 1
        label_items = []
        for class_info in config.classes:
            label_items.append((class_info.name, class_info.id))
            for alias in class_info.aliases:
                label_items.append((alias, class_info.id))
        output = labelme_directory_to_coco(
            config.paths.annotations,
            args.out,
            dict(label_items),
            background_id=config.background_id,
        )
        print(output)
        return 0

    if args.command == "split":
        config = load_config(args.config)
        output_dir = args.out or config.paths.splits
        if output_dir is None:
            print("ERROR: provide --out or config.paths.splits.")
            return 1
        split_csv = split_dataset(
            config,
            output_dir,
            train=args.train,
            val=args.val,
            seed=args.seed,
            require_masks=not args.allow_missing_masks,
        )
        print(split_csv)
        return 0

    if args.command == "tile":
        config = load_config(args.config)
        manifest_path = tile_dataset(
            config,
            args.out,
            tile_size=_parse_pair(args.tile_size),
            stride=_parse_pair(args.stride),
            show_progress=not args.no_progress,
        )
        print(manifest_path)
        return 0

    if args.command == "overlay":
        config = load_config(args.config)
        outputs = export_mask_overlays(
            config,
            args.out,
            limit=args.limit,
            alpha=args.alpha,
            show_progress=not args.no_progress,
        )
        for output in outputs:
            print(output)
        return 0

    if args.command == "plot-morphology":
        formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
        outputs = save_morphology_plots(args.csv, args.out, formats=formats)
        for output in outputs:
            print(output)
        return 0

    return 1


def _parse_pair(value: str | None) -> tuple[int, int] | None:
    if value is None:
        return None
    cleaned = value.lower().replace(",", "x")
    parts = [part for part in cleaned.split("x") if part]
    if len(parts) != 2:
        raise ValueError(f"Expected WIDTHxHEIGHT, got: {value}")
    return int(parts[0]), int(parts[1])


if __name__ == "__main__":
    raise SystemExit(main())
