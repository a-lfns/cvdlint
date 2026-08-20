Output docs/assets/cvdlint-demo.gif

Require uv
Require pre-commit

Set Shell "zsh"
Set FontSize 22
Set Width 1000
Set Height 550
Set TypingSpeed 60ms
Set Padding 24
Set PlaybackSpeed 0.75
Set WindowBar Colorful
Set WaitTimeout 30s

Hide
Type "preexec() { printf '\e[0m\e[38;2;240;243;246m'; }"
Enter
Type "export PS1=$'%{\e[1;38;2;155;121;208m%}> %{\e[1;38;2;255;255;255m%}'"
Enter
Type "unset NO_COLOR"
Enter
Type "export TERM=xterm-256color"
Enter
Type "export COLORTERM=truecolor"
Enter
Type "export MPLBACKEND=Agg"
Enter
Type "uv sync --locked"
Enter
Sleep 250ms
Type "export PATH=$PWD/.venv/bin:$PATH"
Enter
Type "export CVDLINT_DEMO_BIN=$PWD/.venv/bin/cvdlint"
Enter
Type "export PYTHONSTARTUP=$PWD/docs/assets/demo/python-startup.py"
Enter
Type "mkdir -p /tmp/cvdlint-demo"
Enter
Type "export MPLCONFIGDIR=/tmp/cvdlint-demo/matplotlib"
Enter
Type "cp docs/assets/demo/palette-problem.json.example /tmp/cvdlint-demo/palette.json"
Enter
Type "cp docs/assets/demo/pre-commit-config.yaml.example /tmp/cvdlint-demo/.pre-commit-config.yaml"
Enter
Type "git -C /tmp/cvdlint-demo init -q"
Enter
Type "git -C /tmp/cvdlint-demo add ."
Enter
Type "clear"
Enter
Show

# PRE-COMMIT

Hide
Type "cd /tmp/cvdlint-demo"
Enter
Type "clear; print -P '%B%F{#F2A65A}SCAN REPOSITORY FOR CONFUSABLE COLOUR PALETTES%f%b'"
Enter
Show
Sleep 2s
Type "pre-commit run --all-files"
Enter
Sleep 10s
Hide
Type "cd -"
Enter

# LOCAL USE

# Direct CLI: check a declared palette.
Hide
Type "clear; print -P '%B%F{#F2A65A}CHECK A KNOWN COLOUR PALETTE%f%b'"
Enter
Show
Sleep 2s
Type "cvdlint '#E41A1C' '#4DAF4A' '#377EB8'"
Enter
Sleep 10s

# Python API: inspect the result programmatically.
Hide
Type "clear; print -P '%B%F{#F2A65A}CHECK PYTHON FIGURES AT RUNTIME%f%b'"
Enter
Show
Sleep 2s
Hide
Type "python -q"
Enter
Wait+Line />>>/
Type "import matplotlib.pyplot as plt"
Enter
Show
Wait+Line />>>/
Type "from cvdlint.adapters.matplotlib import check_figure"
Enter
Wait+Line />>>/
Type "fig = plt.figure()"
Enter
Wait+Line />>>/
Type "plt.bar(['A','B','C'], [3,2,4], color=plt.colormaps['Set1'].colors[:3])"
Enter
Wait+Line />>>/
Type "check_figure(fig).raise_for_failure()"
Enter
Wait+Line />>>/
Sleep 10s
Hide
Type "exit()"
Enter

Type "rm /tmp/cvdlint-demo/palette.json /tmp/cvdlint-demo/.pre-commit-config.yaml"
Enter
Show
