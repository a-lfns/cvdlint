Output docs/assets/cvdlint-demo.gif

Require uv

Set FontSize 22
Set Width 1000
Set Height 440
Set TypingSpeed 70ms
Set Theme "Dracula"
Set Padding 24
Set PlaybackSpeed 0.75
Set WindowBar Colorful

Hide
Type "preexec() { printf '\e[0m'; }"
Enter
Type "export PS1=$'\e[1m> '"
Enter
Type "unset NO_COLOR"
Enter
Type "export TERM=xterm-256color"
Enter
Type "export COLORTERM=truecolor"
Enter
Type "uv sync --locked"
Enter
Wait+Screen /Audited/
Sleep 250ms
Type "export PATH=$PWD/.venv/bin:$PATH"
Enter
Type "export PYTHONSTARTUP=$PWD/docs/assets/demo/python-startup.py"
Enter
Type "mkdir -p /tmp/cvdlint-demo"
Enter
Type "cp docs/assets/demo/palette-problem.json.example /tmp/cvdlint-demo/palette.json"
Enter
Type "clear"
Enter
Show

# Static linter: scan a JSON palette file.
Type "cvdlint --tolerance 10 /tmp/cvdlint-demo"
Enter
Sleep 10s

Hide
Type "clear"
Enter
Show

# Direct CLI: check a declared palette.
Type "cvdlint '#E41A1C' '#4DAF4A' '#377EB8'"
Enter
Sleep 10s

Hide
Type "clear"
Enter
Show

# Python API: inspect the result programmatically.
Type "python"
Enter
Wait+Line />>>/
Type "from cvdlint import palette_check"
Enter
Wait+Line />>>/
Type "report = palette_check(['#E41A1C', '#4DAF4A', '#377EB8'])"
Enter
Wait+Line />>>/
Type "report.raise_for_failure()"
Enter
Wait+Line />>>/
Sleep 10s

Hide
Type "rm /tmp/cvdlint-demo/palette.json"
Enter
Type "rmdir /tmp/cvdlint-demo"
Enter
Show
