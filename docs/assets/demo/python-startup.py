"""Style Python input for the generated terminal demonstration."""

import sys

_displayhook = sys.displayhook
_excepthook = sys.excepthook
_output_colour = "\033[0m\033[38;2;240;243;246m"


def _normal_weight_displayhook(value: object) -> None:
    print(_output_colour, end="", flush=True)
    _displayhook(value)


def _normal_weight_excepthook(exc_type, exc_value, traceback) -> None:
    print(_output_colour, end="", flush=True)
    _excepthook(exc_type, exc_value, traceback)


def _reset_before_execution(frame, event, _arg):
    if event == "call" and frame.f_code.co_filename == "<stdin>":
        print(_output_colour, end="", flush=True)


_prompt_colour = "\033[1;38;2;155;121;208m"
_input_colour = "\033[1;38;2;255;255;255m"
sys.ps1 = f"{_prompt_colour}>>> {_input_colour}"
sys.ps2 = f"{_prompt_colour}... {_input_colour}"
sys.displayhook = _normal_weight_displayhook
sys.excepthook = _normal_weight_excepthook
sys.tracebacklimit = 0
sys.settrace(_reset_before_execution)
