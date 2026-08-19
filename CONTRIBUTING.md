# Contributing

Contributions, bug reports, and documentation improvements are welcome.

Set up the development environment and run the checks with:

```console
uv sync --all-extras --dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run --extra docs sphinx-build -W -b html docs docs/_build/html
```

Please add or update tests for behavioural changes and keep project-authored
documentation in British English. Open an issue before beginning a substantial
or potentially breaking change so its scope can be discussed first.
