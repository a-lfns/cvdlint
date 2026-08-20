import json
from pathlib import Path

import pytest

from cvdlint.cli import _parser, main


def test_help_explains_cli_options(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        _parser().parse_args(["--help"])

    assert exit_info.value.code == 0
    help_text = capsys.readouterr().out
    assert "minimum acceptable perceptual distance" in help_text
    assert "closest normal-vision pair" in help_text
    assert "CIEDE2000" in help_text
    assert "severity from 0.0 to 1.0" in help_text
    assert "TARGET [TARGET ...]" in help_text


def test_cli_scans_python_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = 'palette = ["#E41A1C", "#4DAF4A"]\n'
    path = tmp_path / "chart.py"
    path.write_text(source)
    monkeypatch.setattr("sys.argv", ["cvdlint", "--tolerance", "100", str(path)])

    with pytest.raises(SystemExit) as exit_info:
        main()

    output = capsys.readouterr().out
    assert exit_info.value.code == 1
    assert "model-specific approximations" in output
    assert f"{path}:1:11:" in output
    assert "palette: #E41A1C  #4DAF4A" in output
    assert "CVD001 deuteranopia: distance" in output
    assert "original:  #E41A1C  #4DAF4A" in output
    assert "simulated:" in output
    assert "Checked 1 palette(s) in 1 file(s)" in output


def test_cli_reports_notebook_cell(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "chart.ipynb"
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": ['palette = ["#E41A1C", "#4DAF4A"]'],
                    }
                ]
            }
        )
    )
    monkeypatch.setattr("sys.argv", ["cvdlint", "--tolerance", "100", str(path)])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 1
    output = capsys.readouterr().out
    assert f"{path}:cell 1:1:11:" in output
    assert "palette: #E41A1C  #4DAF4A" in output
    assert "original:  #E41A1C  #4DAF4A" in output
    assert "simulated:" in output


def test_cli_reports_passing_palette_colors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "chart.py"
    path.write_text('palette = ["#000000", "#FFFFFF"]\n')
    monkeypatch.setattr("sys.argv", ["cvdlint", "--tolerance", "10", str(path)])

    main()

    output = capsys.readouterr().out
    assert "palette: #000000  #FFFFFF" in output
    assert "  PASS" in output


def test_cli_defaults_to_absolute_ciede2000_tolerance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "chart.py"
    path.write_text('palette = ["#4DAF4A", "#377EB8"]\n')
    monkeypatch.setattr("sys.argv", ["cvdlint", str(path)])

    main()

    output = capsys.readouterr().out
    assert "  PASS" in output
    assert "found 0 problem(s)" in output


def test_cli_reports_configured_simulation_severity(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["cvdlint", "--severity", "0.5", "#000000", "#FFFFFF"],
    )

    main()

    assert "severity 0.50" in capsys.readouterr().out


def test_direct_cli_reports_palette_and_simulated_problem_colours(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "cvdlint",
            "--tolerance",
            "10",
            "#E41A1C",
            "#4DAF4A",
            "#377EB8",
        ],
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    captured = capsys.readouterr()
    assert exit_info.value.code == 1
    assert "palette: #E41A1C  #4DAF4A  #377EB8" in captured.out
    assert "CVD001 deuteranopia: distance 9.60 < 10.00" in captured.err
    assert "original:  #E41A1C  #4DAF4A" in captured.err
    assert "simulated: #938208  #A69852" in captured.err


def test_cli_relative_mode_retains_normal_vision_threshold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "chart.py"
    path.write_text('palette = ["#4DAF4A", "#377EB8"]\n')
    monkeypatch.setattr("sys.argv", ["cvdlint", "--relative", str(path)])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 1
    assert "CVD001 deuteranopia" in capsys.readouterr().out


@pytest.mark.parametrize("metric", ["CIE76", "CIE94"])
def test_nondefault_metric_requires_threshold_policy(
    metric: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv", ["cvdlint", "--metric", metric, "#000000", "#FFFFFF"]
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2
    assert "requires --tolerance or --relative" in capsys.readouterr().err


def test_reads_pyproject_configuration_and_excludes_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.cvdlint]\ntolerance = 100\nexclude = ["ignored.py"]\n'
    )
    (tmp_path / "checked.py").write_text('p = ["#000000", "#FFFFFF"]\n')
    (tmp_path / "ignored.py").write_text('p = ["#000000", "#FFFFFF"]\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["cvdlint", "."])

    with pytest.raises(SystemExit) as exit_info:
        main()

    output = capsys.readouterr().out
    assert exit_info.value.code == 1
    assert "checked.py" in output
    assert "ignored.py" not in output
    assert "in 2 file(s)" in output


def test_cli_tolerance_overrides_configured_relative_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.cvdlint]\nrelative = true\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "sys.argv",
        ["cvdlint", "--tolerance", "10", "#4DAF4A", "#377EB8"],
    )

    main()

    assert "PASS" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("configuration", "message"),
    [
        ("tolernace = 10", "unknown tool.cvdlint setting(s): tolernace"),
        ("tolerance = true", "tolerance must be a number"),
        ("severity = true", "severity must be between 0 and 1"),
        ('metric = ["CIE76"]', "metric must be CIE76, CIE94, or CIEDE2000"),
        ("format = false", "format must be text, json, or sarif"),
    ],
)
def test_rejects_invalid_pyproject_configuration(
    configuration: str,
    message: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "pyproject.toml").write_text(f"[tool.cvdlint]\n{configuration}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["cvdlint", "#000000", "#FFFFFF"])

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2
    assert message in capsys.readouterr().err


@pytest.mark.parametrize("output_format", ["json", "sarif"])
def test_machine_readable_output(
    output_format: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "chart.py"
    path.write_text('p = ["#E41A1C", "#4DAF4A"]\n')
    monkeypatch.setattr(
        "sys.argv",
        ["cvdlint", "--tolerance", "100", "--format", output_format, str(path)],
    )

    with pytest.raises(SystemExit):
        main()

    report = json.loads(capsys.readouterr().out)
    if output_format == "json":
        assert report["palettes"][0]["colors"] == ["#E41A1C", "#4DAF4A"]
    else:
        assert report["version"] == "2.1.0"
        assert report["runs"][0]["results"][0]["ruleId"] == "CVD001"


@pytest.mark.parametrize("severity", ["-0.1", "1.1"])
def test_cli_rejects_severity_outside_supported_range(
    severity: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv", ["cvdlint", "--severity", severity, "#000000", "#FFFFFF"]
    )

    with pytest.raises(SystemExit) as exit_info:
        main()

    assert exit_info.value.code == 2
    assert "severity must be between 0 and 1" in capsys.readouterr().err
