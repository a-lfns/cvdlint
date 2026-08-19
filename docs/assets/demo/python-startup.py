"""Style Python input for the generated terminal demonstration."""

import sys

_displayhook = sys.displayhook
_excepthook = sys.excepthook


def _normal_weight_displayhook(value: object) -> None:
    print("\033[0m", end="")
    _displayhook(value)


def _normal_weight_excepthook(exc_type, exc_value, traceback) -> None:
    print("\033[0m", end="")
    _excepthook(exc_type, exc_value, traceback)


sys.ps1 = "\033[1m>>> "
sys.ps2 = "\033[1m... "
sys.displayhook = _normal_weight_displayhook
sys.excepthook = _normal_weight_excepthook
sys.tracebacklimit = 0
