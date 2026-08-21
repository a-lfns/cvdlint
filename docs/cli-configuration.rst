CLI, configuration, and CI
==========================

Options
-------

``--tolerance FLOAT``
   Set the minimum acceptable perceptual distance. CIEDE2000 defaults to
   ``10``.

``--relative``
   Use the closest normal-vision pair as the threshold. This can flag colours
   that remain visibly different, so it is opt-in and cannot be combined with
   ``--tolerance``.

``--metric METRIC``
   Select ``CIEDE2000`` (default), ``CIE94``, or ``CIE76``. The latter two
   require an explicit tolerance or relative mode because their scales differ.

``--severity FLOAT``
   Set simulation severity from ``0.0`` to ``1.0``; the default is ``1.0``.

``--exclude GLOB``
   Exclude matching paths. Repeat the option for multiple patterns.

``--format FORMAT``
   Select ``text``, ``json``, or ``sarif`` output.

.. _terminal-output:

Output in terminals
-------------------

When the terminal environment supports colour, text reports display ANSI
true-colour swatches beside original and simulated hexadecimal values. Set
``NO_COLOR=1`` to disable swatches explicitly.

Project configuration
---------------------

Store shared defaults in the ``pyproject.toml`` in the directory from which
``cvdlint`` is run. The linter does not currently search parent directories for
configuration.

.. code-block:: toml

   [tool.cvdlint]
   tolerance = 10
   severity = 1.0
   metric = "CIEDE2000"
   exclude = ["generated/**", "vendor/**"]
   format = "text"

The supported settings are:

``tolerance``
   A finite, non-negative number. It defaults to ``10`` for CIEDE2000 when
   neither this setting nor relative mode is selected.

``relative``
   ``true`` or ``false``. Set it to ``true`` instead of defining ``tolerance``
   to use the closest normal-vision pair as the threshold. The two settings are
   mutually exclusive.

``severity``
   A number from ``0`` to ``1`` inclusive.

``metric``
   One of ``"CIEDE2000"``, ``"CIE94"``, or ``"CIE76"``. CIE94 and CIE76
   require an explicit tolerance or relative mode.

``exclude``
   A list of glob patterns. Each pattern is matched against both the path
   relative to a supplied directory and the complete supplied path. For
   example, ``"generated/**"`` excludes everything below a directory named
   ``generated`` when scanning the project root. Values passed with
   ``--exclude`` are added to the configured patterns.

``format``
   One of ``"text"``, ``"json"``, or ``"sarif"``.

Explicit command-line values take precedence over corresponding scalar
defaults. Exclusion patterns from the command line and configuration are
combined.

Configuration errors
--------------------

Configuration is validated before any targets are checked. Unknown settings,
incorrect TOML types, unsupported values, malformed TOML, and incompatible
``tolerance`` and ``relative`` settings are rejected. For example, a misspelt
setting does not silently fall back to the default:

.. code-block:: text

   error: unknown tool.cvdlint setting(s): tolernace

Invalid configuration is written to standard error and the command exits with
status ``2``. A valid configuration that finds potentially confusable pairs
still exits with status ``1``.

CI reports
----------

Machine-readable output can be retained as an artefact or uploaded to a code
scanning service:

.. code-block:: console

   cvdlint --format json . > cvdlint.json
   cvdlint --format sarif . > cvdlint.sarif

.. _pre-commit-hook:

Install and use the pre-commit hook
-----------------------------------

The repository publishes a pre-commit hook:

.. code-block:: yaml

   repos:
     - repo: https://github.com/a-lfns/cvdlint
       rev: v0.1.0
       hooks:
         - id: cvdlint

Install the hook once, then run it automatically on commits or explicitly
against every tracked file:

.. code-block:: console

   pre-commit install
   pre-commit run cvdlint --all-files

A failing hook reports the source location, extracted palette, problematic
pair, and modelled colours:

.. code-block:: text

   cvdlint..................................................................Failed
   - hook id: cvdlint
   - exit code: 1

   palette.json:1:1:
     palette: #E41A1C  #4DAF4A  #377EB8
     CVD001 deuteranopia: distance 9.60 < 10.00
       original:  #E41A1C  #4DAF4A
       simulated: #938208  #A69852
   Checked 1 palette(s) in 1 file(s); found 1 problem(s).
