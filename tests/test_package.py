from importlib.metadata import version

import cvdlint


def test_version_comes_from_package_metadata() -> None:
    assert cvdlint.__version__ == version("cvdlint")
