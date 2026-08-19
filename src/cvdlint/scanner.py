"""Static extraction of literal colour palettes from Python source files."""

from __future__ import annotations

import ast
import fnmatch
import json
import re
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .core import Metric, palette_check
from .models import CheckResult
from .named_colours import CSS4_COLOURS

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
_SUPPORTED_SUFFIXES = {".py", ".ipynb", ".json", ".toml", ".yaml", ".yml"}
_SKIPPED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


@dataclass(frozen=True, slots=True)
class PaletteOccurrence:
    """A literal palette and its source location."""

    path: Path
    line: int
    column: int
    colors: tuple[str, ...]
    cell: int | None = None


@dataclass(frozen=True, slots=True)
class PaletteDiagnostic:
    """The result of checking one statically discovered palette."""

    occurrence: PaletteOccurrence
    report: CheckResult


class SourceSyntaxError(ValueError):
    """Raised when a Python source file cannot be parsed."""


class _PaletteVisitor(ast.NodeVisitor):
    def __init__(
        self,
        path: Path,
        source: str,
        cell: int | None = None,
        environment: dict[str, str | tuple[str, ...]] | None = None,
    ) -> None:
        self.path = path
        self.cell = cell
        self.environment = environment if environment is not None else {}
        self.occurrences: list[PaletteOccurrence] = []
        self._recorded: set[int] = set()
        self._suppressed_lines = {
            number
            for number, line in enumerate(source.splitlines(), start=1)
            if "cvdlint: ignore" in line or "noqa: CVD001" in line
        }

    def visit_Assign(self, node: ast.Assign) -> None:
        value = self._evaluate(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name) and value is not None:
                self.environment[target.id] = value
        if isinstance(value, tuple):
            self._record(node.value, value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None and isinstance(node.target, ast.Name):
            value = self._evaluate(node.value)
            if value is not None:
                self.environment[node.target.id] = value
            if isinstance(value, tuple):
                self._record(node.value, value)
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:
        value = self._evaluate_palette(node)
        if value is not None:
            self._record(node, value)
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        value = self._evaluate_palette(node)
        if value is not None:
            self._record(node, value)
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:
        value = self._evaluate_palette(node)
        if value is not None:
            self._record(node, value)
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        value = self._evaluate_palette(node)
        if value is not None:
            self._record(node, value)
        self.generic_visit(node)

    def _evaluate(self, node: ast.expr) -> str | tuple[str, ...] | None:
        colour = _evaluate_colour_node(node, self.environment)
        if colour is not None:
            return colour
        return self._evaluate_palette(node)

    def _evaluate_palette(self, node: ast.expr) -> tuple[str, ...] | None:
        if isinstance(node, ast.Name):
            value = self.environment.get(node.id)
            return value if isinstance(value, tuple) else None
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._evaluate_palette(node.left)
            right = self._evaluate_palette(node.right)
            return left + right if left is not None and right is not None else None
        if isinstance(node, ast.Dict):
            elements = node.values
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            elements = node.elts
        else:
            return None

        colours: list[str] = []
        for element in elements:
            if isinstance(element, ast.Starred):
                nested = self._evaluate_palette(element.value)
                if nested is None:
                    return None
                colours.extend(nested)
                continue
            colour = _evaluate_colour_node(element, self.environment)
            if colour is None:
                return None
            colours.append(colour)
        return tuple(colours) if len(colours) >= 2 else None

    def _record(self, node: ast.expr, colours: tuple[str, ...]) -> None:
        if id(node) in self._recorded or node.lineno in self._suppressed_lines:
            return
        self._recorded.add(id(node))
        if len(colours) >= 2:
            self.occurrences.append(
                PaletteOccurrence(
                    path=self.path,
                    line=node.lineno,
                    column=node.col_offset + 1,
                    colors=colours,
                    cell=self.cell,
                )
            )


def _normalise_colour(value: object) -> str | None:
    if isinstance(value, str):
        if _HEX_COLOR.fullmatch(value):
            return value.upper()
        return CSS4_COLOURS.get(value.lower().replace(" ", ""))
    if isinstance(value, (list, tuple)) and len(value) in {3, 4}:
        channels = value[:3]
        if not all(isinstance(channel, (int, float)) for channel in channels):
            return None
        numbers = [float(channel) for channel in channels]
        if all(0 <= channel <= 1 for channel in numbers):
            numbers = [channel * 255 for channel in numbers]
        elif not all(0 <= channel <= 255 for channel in numbers):
            return None
        red, green, blue = (round(channel) for channel in numbers)
        return f"#{red:02X}{green:02X}{blue:02X}"
    return None


def _evaluate_colour_node(
    node: ast.expr, environment: dict[str, str | tuple[str, ...]]
) -> str | None:
    if isinstance(node, ast.Name):
        value = environment.get(node.id)
        return value if isinstance(value, str) else None
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError):
        return None
    return _normalise_colour(value)


def extract_palettes(
    path: Path,
    source: str,
    *,
    cell: int | None = None,
    environment: dict[str, str | tuple[str, ...]] | None = None,
) -> tuple[PaletteOccurrence, ...]:
    """Extract statically resolvable palettes without executing Python code."""
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        cell_location = f":cell {cell}" if cell is not None else ""
        location = f"{path}{cell_location}:{error.lineno or 1}:{error.offset or 1}"
        raise SourceSyntaxError(f"{location}: syntax error: {error.msg}") from error
    visitor = _PaletteVisitor(path, source, cell, environment)
    visitor.visit(tree)
    return tuple(visitor.occurrences)


def discover_source_files(
    paths: Iterable[Path], *, exclude: Iterable[str] = ()
) -> tuple[Path, ...]:
    """Resolve Python and notebook files under the supplied paths."""
    discovered: set[Path] = set()
    patterns = tuple(exclude)
    for path in paths:
        if not path.exists():
            raise ValueError(f"path does not exist: {path}")
        if path.is_file():
            if path.suffix.lower() not in _SUPPORTED_SUFFIXES:
                raise ValueError(
                    f"expected a Python file, notebook, or directory: {path}"
                )
            if not any(
                fnmatch.fnmatch(path.as_posix(), pattern) for pattern in patterns
            ):
                discovered.add(path)
            continue
        for candidate in path.rglob("*"):
            if candidate.suffix.lower() not in _SUPPORTED_SUFFIXES:
                continue
            relative_parts = candidate.relative_to(path).parts[:-1]
            relative = candidate.relative_to(path).as_posix()
            excluded = any(
                fnmatch.fnmatch(relative, pattern)
                or fnmatch.fnmatch(candidate.as_posix(), pattern)
                for pattern in patterns
            )
            if not excluded and not any(
                part in _SKIPPED_DIRECTORIES for part in relative_parts
            ):
                discovered.add(candidate)
    return tuple(sorted(discovered))


def discover_python_files(paths: Iterable[Path]) -> tuple[Path, ...]:
    """Backward-compatible alias for source-file discovery."""
    return discover_source_files(paths)


def _extract_notebook(path: Path, source: str) -> tuple[PaletteOccurrence, ...]:
    try:
        notebook = json.loads(source)
    except json.JSONDecodeError as error:
        raise ValueError(f"cannot parse notebook {path}: {error.msg}") from error
    if not isinstance(notebook, dict) or not isinstance(notebook.get("cells"), list):
        raise ValueError(f"invalid notebook structure: {path}")

    occurrences: list[PaletteOccurrence] = []
    environment: dict[str, str | tuple[str, ...]] = {}
    for cell_number, cell_data in enumerate(notebook["cells"], start=1):
        if not isinstance(cell_data, dict) or cell_data.get("cell_type") != "code":
            continue
        cell_source = cell_data.get("source", "")
        if isinstance(cell_source, list) and all(
            isinstance(line, str) for line in cell_source
        ):
            cell_source = "".join(cell_source)
        if not isinstance(cell_source, str):
            raise ValueError(f"invalid source in {path}, cell {cell_number}")
        occurrences.extend(
            extract_palettes(
                path,
                cell_source,
                cell=cell_number,
                environment=environment,
            )
        )
    return tuple(occurrences)


def _palettes_from_data(value: object) -> list[tuple[str, ...]]:
    palettes: list[tuple[str, ...]] = []
    if isinstance(value, dict):
        colours = tuple(_normalise_colour(item) for item in value.values())
        if len(colours) >= 2 and all(colour is not None for colour in colours):
            palettes.append(tuple(colour for colour in colours if colour is not None))
        for item in value.values():
            palettes.extend(_palettes_from_data(item))
    elif isinstance(value, list):
        colours = tuple(_normalise_colour(item) for item in value)
        if len(colours) >= 2 and all(colour is not None for colour in colours):
            palettes.append(tuple(colour for colour in colours if colour is not None))
        else:
            for item in value:
                palettes.extend(_palettes_from_data(item))
    return palettes


def _parse_simple_yaml(source: str) -> object:
    """Parse the common mapping-to-list YAML subset used for palette files."""
    result: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in source.splitlines():
        line = raw_line.rstrip()
        if line.lstrip().startswith("#"):
            continue
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith((" ", "-")) and line.endswith(":"):
            current_key = line[:-1].strip()
            result[current_key] = []
            continue
        if current_key is not None and line.lstrip().startswith("-"):
            scalar = line.lstrip()[1:].strip().strip("'\"")
            current = result[current_key]
            if isinstance(current, list):
                current.append(scalar)
            continue
        if current_key is not None and ":" in line.lstrip():
            name, scalar = line.lstrip().split(":", 1)
            current = result[current_key]
            if isinstance(current, list) and not current:
                current = {}
                result[current_key] = current
            if isinstance(current, dict):
                current[name.strip()] = scalar.strip().strip("'\"")
    return result


def _extract_configuration(path: Path, source: str) -> tuple[PaletteOccurrence, ...]:
    try:
        if path.suffix.lower() == ".json":
            data = json.loads(source)
        elif path.suffix.lower() == ".toml":
            data = tomllib.loads(source)
        else:
            data = _parse_simple_yaml(source)
    except (json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"cannot parse configuration {path}: {error}") from error
    return tuple(
        PaletteOccurrence(path, 1, 1, colours) for colours in _palettes_from_data(data)
    )


def scan_paths(
    paths: Iterable[Path],
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
    exclude: Iterable[str] = (),
) -> tuple[PaletteDiagnostic, ...]:
    """Find and check every literal palette under the supplied paths."""
    diagnostics: list[PaletteDiagnostic] = []
    for path in discover_source_files(paths, exclude=exclude):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"cannot read {path}: {error}") from error
        if path.suffix == ".ipynb":
            occurrences = _extract_notebook(path, source)
        elif path.suffix == ".py":
            occurrences = extract_palettes(path, source)
        else:
            occurrences = _extract_configuration(path, source)
        for occurrence in occurrences:
            diagnostics.append(
                PaletteDiagnostic(
                    occurrence=occurrence,
                    report=palette_check(
                        occurrence.colors,
                        tolerance=tolerance,
                        relative=relative,
                        severity=severity,
                        metric=metric,
                    ),
                )
            )
    return tuple(diagnostics)
