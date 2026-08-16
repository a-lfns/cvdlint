"""Static extraction of literal colour palettes from Python source files."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .core import Metric, palette_check
from .models import CheckResult

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
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
    def __init__(self, path: Path, cell: int | None = None) -> None:
        self.path = path
        self.cell = cell
        self.occurrences: list[PaletteOccurrence] = []

    def visit_List(self, node: ast.List) -> None:
        self._record(node, node.elts)
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        self._record(node, node.elts)
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:
        self._record(node, node.elts)
        self.generic_visit(node)

    def _record(self, node: ast.expr, elements: list[ast.expr]) -> None:
        colors: list[str] = []
        for element in elements:
            if not (
                isinstance(element, ast.Constant)
                and isinstance(element.value, str)
                and _HEX_COLOR.fullmatch(element.value)
            ):
                return
            colors.append(element.value)
        if len(colors) >= 2:
            self.occurrences.append(
                PaletteOccurrence(
                    path=self.path,
                    line=node.lineno,
                    column=node.col_offset + 1,
                    colors=tuple(colors),
                    cell=self.cell,
                )
            )


def extract_palettes(
    path: Path, source: str, *, cell: int | None = None
) -> tuple[PaletteOccurrence, ...]:
    """Extract literal hex palettes from Python source without executing it."""
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        cell_location = f":cell {cell}" if cell is not None else ""
        location = f"{path}{cell_location}:{error.lineno or 1}:{error.offset or 1}"
        raise SourceSyntaxError(f"{location}: syntax error: {error.msg}") from error
    visitor = _PaletteVisitor(path, cell)
    visitor.visit(tree)
    return tuple(visitor.occurrences)


def discover_source_files(paths: Iterable[Path]) -> tuple[Path, ...]:
    """Resolve Python and notebook files under the supplied paths."""
    discovered: set[Path] = set()
    for path in paths:
        if not path.exists():
            raise ValueError(f"path does not exist: {path}")
        if path.is_file():
            if path.suffix not in {".py", ".ipynb"}:
                raise ValueError(
                    f"expected a Python file, notebook, or directory: {path}"
                )
            discovered.add(path)
            continue
        for candidate in path.rglob("*"):
            if candidate.suffix not in {".py", ".ipynb"}:
                continue
            relative_parts = candidate.relative_to(path).parts[:-1]
            if not any(part in _SKIPPED_DIRECTORIES for part in relative_parts):
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
        occurrences.extend(extract_palettes(path, cell_source, cell=cell_number))
    return tuple(occurrences)


def scan_paths(
    paths: Iterable[Path],
    *,
    tolerance: float | None = None,
    relative: bool = False,
    severity: float = 1.0,
    metric: Metric = "CIEDE2000",
) -> tuple[PaletteDiagnostic, ...]:
    """Find and check every literal palette under the supplied paths."""
    diagnostics: list[PaletteDiagnostic] = []
    for path in discover_source_files(paths):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"cannot read {path}: {error}") from error
        occurrences = (
            _extract_notebook(path, source)
            if path.suffix == ".ipynb"
            else extract_palettes(path, source)
        )
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
