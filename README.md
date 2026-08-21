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
  <a href="https://github.com/a-lfns/cvdlint/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/a-lfns/cvdlint/ci.yml?branch=main&amp;style=for-the-badge&amp;label=CI" alt="CI status" height="20">
  </a>
  <a href="https://cvdlint.readthedocs.io/en/latest/?badge=latest">
    <img src="https://readthedocs.org/projects/cvdlint/badge/?version=latest&amp;style=for-the-badge&amp;label=Docs" alt="Docs status" height="20">
  </a>
</p>


> **Catch confusable colour palettes before they ship.**\
`cvdlint` is a colour vision deficiency linter for Python projects, notebooks, and palette configuration files, available as a pre-commit hook, CLI tool, and Python API.

<p align="center">
  <img
    src="https://raw.githubusercontent.com/a-lfns/cvdlint/main/docs/assets/cvdlint-demo.gif"
    alt="cvdlint static linter, direct CLI, Python API, and Matplotlib adapter demonstration"
    width="620"
  >
</p>

## Quick start

### Pre-commit

After [installing the cvdlint pre-commit hook](https://cvdlint.readthedocs.io/en/latest/cli-configuration.html#pre-commit-hook),

```console
pre-commit run cvdlint --all-files
```
will scan every supported tracked file for potentially confusable palettes.

### Local usage

After [installing `cvdlint`](https://cvdlint.readthedocs.io/en/latest/getting-started.html#installation),
you can:

**Check a known palette:**

```console
cvdlint '#E41A1C' '#4DAF4A' '#377EB8'
```

**Scan selected paths for potentially confusable palettes:**

```console
cvdlint [dir1] [dir2] [filepath1] [filepath2] ...
```

**Check explicit palettes or completed figures at runtime:**

```python
import matplotlib.pyplot as plt

from cvdlint import check_figure, palette_check

report = palette_check(["#E41A1C", "#4DAF4A", "#377EB8"])
report.raise_for_failure()

fig = plt.figure()
plt.bar(["A", "B", "C"], [3, 2, 4], color=plt.colormaps["Set1"].colors[:3])
check_figure(fig).raise_for_failure()
```


## Documentation

See the [full documentation](https://cvdlint.readthedocs.io/en/latest/) for
supported static patterns, configuration, CLI options, CI and pre-commit
integration, supported plotting libraries, methodology, limitations, and the API
reference.

## Contributing

Contributions, bug reports, and real-world testing are welcome. If you use
`cvdlint` in your projects, feedback on missed palettes, false positives, and
plotting-library compatibility is especially valuable. See
[CONTRIBUTING.md](https://github.com/a-lfns/cvdlint/blob/main/CONTRIBUTING.md)
to get started.

## Acknowledgements

The palette-analysis API and original relative-tolerance policy were informed
by Jakub Nowosad's R package
[colorblindcheck](https://github.com/Nowosad/colorblindcheck), whose published
results are used as compatibility references. `cvdlint` is an independent
Python implementation with its own static-linting, runtime API, and reporting features.

## Licence

[Apache License 2.0](https://github.com/a-lfns/cvdlint/blob/main/LICENSE) © 2026 Alice Alfonsi
