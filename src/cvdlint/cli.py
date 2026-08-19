"""Command-line interface for CI and local use."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from .core import palette_check, simulate_palette
from .scanner import discover_source_files, scan_paths

_CONFIG_KEYS = {"tolerance", "relative", "severity", "metric", "exclude", "format"}


@dataclass(frozen=True, slots=True)
class _Config:
    tolerance: float | None = None
    relative: bool = False
    severity: float = 1.0
    metric: str = "CIEDE2000"
    exclude: tuple[str, ...] = ()
    output_format: str = "text"


def _load_config(path: Path = Path("pyproject.toml")) -> _Config:
    if not path.is_file():
        return _Config()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"cannot read cvdlint configuration: {error}") from error
    values = data.get("tool", {}).get("cvdlint", {})
    if not isinstance(values, dict):
        raise ValueError("[tool.cvdlint] must be a table")
    unknown = set(values) - _CONFIG_KEYS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"unknown tool.cvdlint setting(s): {names}")
    exclude = values.get("exclude", [])
    if not isinstance(exclude, list) or not all(
        isinstance(pattern, str) for pattern in exclude
    ):
        raise ValueError("tool.cvdlint.exclude must be a list of strings")
    tolerance = values.get("tolerance")
    relative = values.get("relative", False)
    severity = values.get("severity", 1.0)
    metric = values.get("metric", "CIEDE2000")
    output_format = values.get("format", "text")
    if tolerance is not None:
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
            raise ValueError("tool.cvdlint.tolerance must be a number")
        if not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError(
                "tool.cvdlint.tolerance must be a finite non-negative number"
            )
    if not isinstance(relative, bool):
        raise ValueError("tool.cvdlint.relative must be true or false")
    if relative and tolerance is not None:
        raise ValueError("tool.cvdlint.tolerance and relative are mutually exclusive")
    if (
        isinstance(severity, bool)
        or not isinstance(severity, (int, float))
        or not math.isfinite(severity)
        or not 0 <= severity <= 1
    ):
        raise ValueError("tool.cvdlint.severity must be between 0 and 1")
    if not isinstance(metric, str) or metric not in {"CIE76", "CIE94", "CIEDE2000"}:
        raise ValueError("tool.cvdlint.metric must be CIE76, CIE94, or CIEDE2000")
    if not isinstance(output_format, str) or output_format not in {
        "text",
        "json",
        "sarif",
    }:
        raise ValueError("tool.cvdlint.format must be text, json, or sarif")
    return _Config(
        tolerance=float(tolerance) if tolerance is not None else None,
        relative=relative,
        severity=float(severity),
        metric=metric,
        exclude=tuple(exclude),
        output_format=output_format,
    )


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
        default=None,
        help="use the closest normal-vision pair as the tolerance",
    )
    parser.add_argument(
        "--metric",
        choices=("CIE76", "CIE94", "CIEDE2000"),
        default=None,
        metavar="METRIC",
        help="colour-distance metric: CIE76, CIE94, or CIEDE2000 (default: CIEDE2000)",
    )
    parser.add_argument(
        "--severity",
        type=float,
        default=None,
        metavar="FLOAT",
        help="CVD simulation severity from 0.0 to 1.0 (default: 1.0)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="exclude paths matching a glob (repeatable)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        dest="output_format",
        default=None,
        help="report format (default: text)",
    )
    return parser


def _diagnostics_data(diagnostics: tuple[Any, ...]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for diagnostic in diagnostics:
        occurrence = diagnostic.occurrence
        output.append(
            {
                "path": str(occurrence.path),
                "cell": occurrence.cell,
                "line": occurrence.line,
                "column": occurrence.column,
                "colors": list(occurrence.colors),
                "passed": diagnostic.report.passed,
                "problems": [
                    {
                        "rule": "CVD001",
                        "condition": problem.condition,
                        "first_color": problem.first_color,
                        "second_color": problem.second_color,
                        "distance": problem.distance,
                        "tolerance": problem.tolerance,
                    }
                    for problem in diagnostic.report.problems
                ],
            }
        )
    return output


def _print_machine_report(output_format: str, diagnostics: tuple[Any, ...]) -> None:
    data = _diagnostics_data(diagnostics)
    if output_format == "json":
        print(json.dumps({"palettes": data}, indent=2))
        return
    results = []
    for palette in data:
        for problem in palette["problems"]:
            location: dict[str, Any] = {
                "physicalLocation": {
                    "artifactLocation": {"uri": palette["path"]},
                    "region": {
                        "startLine": palette["line"],
                        "startColumn": palette["column"],
                    },
                }
            }
            results.append(
                {
                    "ruleId": "CVD001",
                    "level": "warning",
                    "message": {
                        "text": (
                            f"{problem['condition']}: {problem['first_color']} / "
                            f"{problem['second_color']} = {problem['distance']:.2f} "
                            f"< {problem['tolerance']:.2f}"
                        )
                    },
                    "locations": [location],
                    "properties": {"cell": palette["cell"]},
                }
            )
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "cvdlint",
                        "rules": [
                            {
                                "id": "CVD001",
                                "shortDescription": {
                                    "text": "Potentially confusable colour pair"
                                },
                            }
                        ],
                    }
                },
                "results": results,
            }
        ],
    }
    print(json.dumps(sarif, indent=2))


def main() -> None:
    """Run the palette linter and return a CI-friendly exit status."""
    args = _parser().parse_args()
    try:
        config = _load_config()
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    if args.relative:
        relative = True
    elif args.tolerance is not None:
        relative = False
    else:
        relative = config.relative
    metric = args.metric or config.metric
    severity = config.severity if args.severity is None else args.severity
    output_format = args.output_format or config.output_format
    configured_tolerance = (
        config.tolerance if args.tolerance is None else args.tolerance
    )
    excludes = config.exclude + tuple(args.exclude)
    direct_colors = all(target.startswith("#") for target in args.targets)
    try:
        if relative:
            tolerance = None
        elif configured_tolerance is not None:
            tolerance = configured_tolerance
        elif metric == "CIEDE2000":
            tolerance = 10.0
        else:
            raise ValueError(f"--metric {metric} requires --tolerance or --relative")
        if direct_colors:
            report = palette_check(
                args.targets,
                tolerance=tolerance,
                relative=relative,
                severity=severity,
                metric=metric,
            )
        else:
            if any(target.startswith("#") for target in args.targets):
                raise ValueError("cannot mix source paths and direct colours")
            source_files = discover_source_files(
                (Path(target) for target in args.targets), exclude=excludes
            )
            diagnostics = scan_paths(
                source_files,
                tolerance=tolerance,
                relative=relative,
                severity=severity,
                metric=metric,
            )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error

    if not direct_colors:
        if output_format != "text":
            _print_machine_report(output_format, diagnostics)
            if any(not diagnostic.report.passed for diagnostic in diagnostics):
                raise SystemExit(1)
            return
        _print_simulation_context(severity)
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
                    severity=severity,
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

    _print_simulation_context(severity)
    print("palette: " + "  ".join(_format_color(color) for color in report.colors))
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
        simulated = simulate_palette(
            (problem.first_color, problem.second_color),
            problem.condition,  # type: ignore[arg-type]
            severity=severity,
        )
        print(
            f"  CVD001 {problem.condition}: distance "
            f"{problem.distance:.2f} < {problem.tolerance:.2f}",
            file=sys.stderr,
        )
        print(
            "    original:  "
            + "  ".join(
                _format_color(color)
                for color in (problem.first_color, problem.second_color)
            ),
            file=sys.stderr,
        )
        print(
            "    simulated: " + "  ".join(_format_color(color) for color in simulated),
            file=sys.stderr,
        )
    raise SystemExit(1)
