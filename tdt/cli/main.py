"""Command-line interface for tunnel-defect-toolkit."""

from __future__ import annotations

import argparse
from pathlib import Path

from tdt.datasets.converters import convert_labelme_directory
from tdt.datasets.registry import load_config
from tdt.datasets.validation import validate_dataset
from tdt.reporting.dataset_report import generate_dataset_report
from tdt.visualization.morphology_plots import save_morphology_plots


def main(argv: list[str] | None = None) -> int:
    """Run the tdt command-line interface."""

    parser = argparse.ArgumentParser(prog="tdt")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a dataset config.")
    validate.add_argument("config", type=Path)

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

    if args.command == "plot-morphology":
        formats = tuple(item.strip() for item in args.formats.split(",") if item.strip())
        outputs = save_morphology_plots(args.csv, args.out, formats=formats)
        for output in outputs:
            print(output)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
