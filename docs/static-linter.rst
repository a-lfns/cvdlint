Static source-code linter
=========================

Run ``cvdlint`` with one or more files or directories:

.. code-block:: console

   cvdlint src notebooks examples/chart.py

Directories are searched recursively. The linter reads ``.py``, ``.ipynb``,
``.json``, ``.toml``, ``.yaml``, and ``.yml`` files. It does not import or
execute the inspected project.

What it extracts
----------------

The static analyser recognises:

* hexadecimal and CSS4 named colours;
* RGB tuples with channels on either the ``0–1`` or ``0–255`` scale;
* lists, tuples, sets, and dictionary values;
* simple variable references, concatenation, and starred expansion; and
* constant definitions carried forward between notebook code cells.

For notebooks, only code cells are inspected. Markdown, saved outputs, and
runtime kernel state are ignored. A finding includes the filename, notebook
cell where applicable, line and column, the extracted palette, and each
problematic original and simulated colour pair.

.. code-block:: text

   examples/chart.py:4:10:
     palette:    #E41A1C     #4DAF4A     #377EB8
     CVD001 deuteranopia: distance 9.60 < 10.00
       original:     #E41A1C     #4DAF4A
       simulated:    #938208     #A69852

Interactive terminals show colour swatches alongside the hexadecimal values;
see :ref:`terminal-output` for details.

Static-analysis boundary
------------------------

The linter deliberately handles expressions whose values can be established
from source alone. It cannot generally know the result of function calls,
arbitrary control flow, data loading, library theme defaults, or other runtime
state. Use a direct CLI check or the :doc:`python-api-adapters` for those
palettes.

Suppressions
------------

Suppress an intentional Python palette on its source line with either marker:

.. code-block:: python

   brand_colours = ["#123456", "#234567"]  # noqa: CVD001
   decorative = ["#345678", "#456789"]  # cvdlint: ignore
