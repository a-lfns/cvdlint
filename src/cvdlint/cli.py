"""Command-line interface for CI and local use."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .core import palette_check, simulate_palette
from .scanner import discover_source_files, scan_paths


def _format_color(color: str) -> str:
    """Add a true-colour swatch when stdout is an interactive colour terminal."""
    use_color = (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and "NO_COLOR" not in os.environ
        and os.environ.get("TERM") != "dumb"
    )
    if not use_color:
        return color
    red, green, blue = (int(color[index : index + 2], 16) for index in (1, 3, 5))
    return f"\033[48;2;{red};{green};{blue}m  \033[0m {color}"


def _print_simulation_context(severity: float) -> None:
    print(f"Simulation: Machado, Oliveira & Fernandes (2009); severity {severity:.2f}.")
    print("Simulated colours are model-specific approximations.")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cvdlint",
        description=(
            "Check literal palettes in Python files, or check colours supplied "
            "directly."
        ),
    )
    parser.add_argument(
        "targets",
        nargs="+",
        metavar="TARGET",
        help="Python/notebook path to scan, or palette colour in #RRGGBB format",
    )
    tolerance_group = parser.add_mutually_exclusive_group()
    tolerance_group.add_argument(
        "--tolerance",
        type=float,
        metavar="FLOAT",
        help=("minimum acceptable perceptual distance (default: 10 for CIEDE2000)"),
    )
    tolerance_group.add_argument(
        "--relative",
        action="store_true",
        help="use the closest normal-vision pair as the tolerance",
    )
    parser.add_argument(
        "--metric",
        choices=("CIE76", "CIE94", "CIEDE2000"),
        default="CIEDE2000",
        metavar="METRIC",
        help="colour-distance metric: CIE76, CIE94, or CIEDE2000 (default: CIEDE2000)",
    )
    parser.add_argument(
        "--severity",
        type=float,
        default=1.0,
        metavar="FLOAT",
        help="CVD simulation severity from 0.0 to 1.0 (default: 1.0)",
    )
    return parser


def main() -> None:
    """Run the palette linter and return a CI-friendly exit status."""
    args = _parser().parse_args()
    direct_colors = all(target.startswith("#") for target in args.targets)
    try:
        if args.relative:
            tolerance = None
        elif args.tolerance is not None:
            tolerance = args.tolerance
        elif args.metric == "CIEDE2000":
            tolerance = 10.0
        else:
            raise ValueError(
                f"--metric {args.metric} requires --tolerance or --relative"
            )
        if direct_colors:
            report = palette_check(
                args.targets,
                tolerance=tolerance,
                relative=args.relative,
                severity=args.severity,
                metric=args.metric,
            )
        else:
            if any(target.startswith("#") for target in args.targets):
                raise ValueError("cannot mix source paths and direct colours")
            source_files = discover_source_files(
                Path(target) for target in args.targets
            )
            diagnostics = scan_paths(
                source_files,
                tolerance=tolerance,
                relative=args.relative,
                severity=args.severity,
                metric=args.metric,
            )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error

    if not direct_colors:
        _print_simulation_context(args.severity)
        problem_count = 0
        for diagnostic in diagnostics:
            occurrence = diagnostic.occurrence
            location = f"{occurrence.path}"
            if occurrence.cell is not None:
                location += f":cell {occurrence.cell}"
            location += f":{occurrence.line}:{occurrence.column}"
            print(f"{location}:")
            print(
                "  palette: "
                + "  ".join(_format_color(color) for color in occurrence.colors)
            )
            if diagnostic.report.passed:
                print("  PASS")
                continue
            for problem in diagnostic.report.problems:
                problem_count += 1
                simulated = simulate_palette(
                    (problem.first_color, problem.second_color),
                    problem.condition,  # type: ignore[arg-type]
                    severity=args.severity,
                )
                print(
                    f"  CVD001 {problem.condition}: distance "
                    f"{problem.distance:.2f} < {problem.tolerance:.2f}"
                )
                print(
                    "    original:  "
                    + "  ".join(
                        _format_color(color)
                        for color in (problem.first_color, problem.second_color)
                    )
                )
                print(
                    "    simulated: "
                    + "  ".join(_format_color(color) for color in simulated)
                )
        palette_count = len(diagnostics)
        file_count = len(source_files)
        print(
            f"Checked {palette_count} palette(s) in {file_count} file(s); "
            f"found {problem_count} problem(s)."
        )
        if problem_count:
            raise SystemExit(1)
        return

    _print_simulation_context(args.severity)
    for summary in report.summaries:
        print(
            f"{summary.name:14} {summary.distinguishable_pair_count:>3}/"
            f"{summary.pair_count:<3} distinguishable; "
            f"minimum distance {summary.minimum_distance:.2f}"
        )
    if report.passed:
        print("PASS: palette meets the configured CVD tolerance")
        return
    print("FAIL: potentially indistinguishable colour pairs", file=sys.stderr)
    for problem in report.problems:
        print(
            f"  {problem.condition}: {problem.first_color} / "
            f"{problem.second_color} = {problem.distance:.2f}",
            file=sys.stderr,
        )
    raise SystemExit(1)
