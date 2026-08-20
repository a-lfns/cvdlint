<p align="center">
  <picture>
    <source
      media="(prefers-color-scheme: dark)"
      srcset="https://raw.githubusercontent.com/a-lfns/cvdlint/main/docs/assets/cvdlint-lockup-dark.svg"
    >
    <source
      media="(prefers-color-scheme: light)"
      srcset="https://raw.githubusercontent.com/a-lfns/cvdlint/main/docs/assets/cvdlint-lockup-light.svg"
    >
    <img
      src="https://raw.githubusercontent.com/a-lfns/cvdlint/main/docs/assets/cvdlint-lockup-light.svg"
      width="620"
      alt="cvdlint — colour vision deficiency linting"
    >
  </picture>
</p>

<p align="center">
  <a href="https://pypi.org/project/cvdlint/">
    <img src="https://img.shields.io/pypi/v/cvdlint?style=for-the-badge" alt="PyPI release" height="20">
  </a>
  <a href="https://github.com/a-lfns/cvdlint/actions/workflows/main.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/a-lfns/cvdlint/main.yml?branch=main&amp;style=for-the-badge&amp;label=CI" alt="CI status" height="20">
  </a>
</p>


> **Catch confusable colour palettes before they ship.**\
`cvdlint` is a colour vision deficiency linter for Python projects, notebooks, and palette configuration files, available as a pre-commit hook, CLI tool, and Python API.

<p align="center">
  <img
    src="https://raw.githubusercontent.com/a-lfns/cvdlint/main/docs/assets/cvdlint-demo.gif"
    alt="cvdlint static linter, direct CLI check, and Python API demonstration"
    width="620"
  >
</p>

## Usage

### Pre-commit hook

Add the
[hook configuration](https://cvdlint.readthedocs.io/en/latest/cli-configuration.html#pre-commit) to your repository,
then run:

```console
pre-commit install
pre-commit run --all-files
```

### Local use

Install `cvdlint`:

```console
pip install cvdlint
```

Check a known palette:

```console
cvdlint '#E41A1C' '#4DAF4A' '#377EB8'
```

Scan the current project or selected paths:

```console
cvdlint [dir1] [dir2] [filepath1] [filepath2] ...
```

Use `cvdlint` in your Python code:

```python
from cvdlint import palette_check

report = palette_check(["#E41A1C", "#4DAF4A", "#377EB8"])
report.raise_for_failure()
```

See the [plotting adapter guide](https://cvdlint.readthedocs.io/en/latest/python-api-adapters.html)
for runtime validation with Matplotlib and Plotly.

## Documentation

See the [full documentation](https://cvdlint.readthedocs.io/en/latest/) for
supported static patterns, configuration, CLI options, CI and pre-commit
integration, plotting adapters, methodology, limitations, and the API
reference.

## Contributing

Contributions are welcome; see [CONTRIBUTING.md](https://github.com/a-lfns/cvdlint/blob/main/CONTRIBUTING.md) to get
started.

## Acknowledgements

The palette-analysis API and original relative-tolerance policy were informed
by Jakub Nowosad's R package
[colorblindcheck](https://github.com/Nowosad/colorblindcheck), whose published
results are used as compatibility references. `cvdlint` is an independent
Python implementation with its own static-linting and reporting features.

## Licence

[Apache License 2.0](https://github.com/a-lfns/cvdlint/blob/main/LICENSE) © 2026 Alice Alfonsi
