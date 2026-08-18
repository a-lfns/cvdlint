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

Project configuration
---------------------

Store shared defaults in ``pyproject.toml``. Command-line options take
precedence.

.. code-block:: toml

   [tool.cvdlint]
   tolerance = 10
   severity = 1.0
   metric = "CIEDE2000"
   exclude = ["generated/**", "vendor/**"]
   format = "text"

Use ``relative = true`` instead of ``tolerance`` for relative mode.

CI reports
----------

Machine-readable output can be retained as an artefact or uploaded to a code
scanning service:

.. code-block:: console

   cvdlint --format json . > cvdlint.json
   cvdlint --format sarif . > cvdlint.sarif

Pre-commit
----------

The repository publishes a pre-commit hook:

.. code-block:: yaml

   repos:
     - repo: https://github.com/a-lfns/cvdlint
       rev: v0.1.0
       hooks:
         - id: cvdlint
