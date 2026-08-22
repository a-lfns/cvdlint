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

## Releasing (maintainers only)

The following process requires maintainer permissions on the GitHub repository.
Publishing also requires the `release.yml` workflow to be registered as a
Trusted Publisher on TestPyPI and PyPI, using the `testpypi` and `pypi` GitHub
environments respectively.

Public contributors cannot dispatch this workflow, create repository Releases,
or modify the protected workflow on `main`. For additional protection, configure
required reviewers on both GitHub environments so publication needs explicit
maintainer approval.

1. Update the package version, for example:

   ```console
   uv version 0.1.0a3
   ```

2. Commit `pyproject.toml` and `uv.lock`, push the commit to `main`, and wait for
   CI to pass.

3. In GitHub Actions, manually run **Publish release to PyPI**. A manual run
   builds and smoke-tests both distributions, then publishes them to TestPyPI
   only.

4. Install the exact version from TestPyPI, using PyPI for dependencies:

   ```console
   pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     cvdlint==0.1.0a3
   ```

5. Create a GitHub Release from `main` with the matching `v`-prefixed tag, such
   as `v0.1.0a3`. Mark alpha, beta, and release-candidate versions as
   pre-releases.

6. Publish the GitHub Release. This triggers the same workflow, verifies that
   the tag matches the version in `pyproject.toml`, and publishes the tested
   wheel and source distribution to PyPI.

Package versions cannot be replaced on TestPyPI or PyPI. Increment the version
before retrying a release whose distributions were already uploaded.
