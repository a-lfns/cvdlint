"""Smoke test installed wheel and source distributions."""

import subprocess

from cvdlint import __version__, palette_check

assert __version__
assert palette_check(["#000000", "#FFFFFF"]).passed

completed = subprocess.run(
    ["cvdlint", "#000000", "#FFFFFF"],
    check=False,
    capture_output=True,
    text=True,
)
assert completed.returncode == 0, completed.stderr or completed.stdout
