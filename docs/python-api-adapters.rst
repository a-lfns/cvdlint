Python API and plot adapters
============================

Palette checks
--------------

Use :func:`cvdlint.palette_check` when a palette is available at runtime:

.. code-block:: python

   from cvdlint import palette_check

   result = palette_check(["#E41A1C", "#4DAF4A", "#377EB8"])
   print(result.passed)
   print(result.problems)
   result.raise_for_failure()

It uses an absolute CIEDE2000 tolerance of ``10`` by default, matching the
CLI. Pass ``relative=True`` to use the closest normal-vision pair instead.

Use :func:`cvdlint.simulate_palette` to obtain the modelled colours and
:func:`cvdlint.palette_dist` to calculate a pairwise distance matrix.

Common figure check
-------------------

Use the common dispatcher for Matplotlib, Seaborn, Plotly, and PyROOT objects:

.. code-block:: python

   from cvdlint import check_figure

   result = check_figure(fig)
   result.raise_for_failure()

The backend is inferred from supported native figure objects and their
subclasses; no backend name is required. Matplotlib and Plotly are recognised
from their class hierarchies, while PyROOT uses ROOT's runtime type
information. Seaborn produces Matplotlib figures, so it is detected as
Matplotlib.

Pass the underlying figure rather than an axes, grid, or custom wrapper. For
example, use ``check_figure(ax.figure)`` for a Matplotlib axes or
``check_figure(grid.fig)`` for a Seaborn grid. An unrecognised object raises
``TypeError`` rather than selecting an adapter speculatively.

The specialised adapter imports remain available for applications that need
direct colour extraction.

Matplotlib and Seaborn
----------------------

.. code-block:: python

   from cvdlint.adapters.matplotlib import colors_from_figure

   colours = colors_from_figure(fig)

Plotly
------

.. code-block:: python

   from cvdlint.adapters.plotly import colors_from_figure

   colours = colors_from_figure(fig)

PyROOT
------

.. code-block:: python

   from cvdlint.adapters.root import colors_from_canvas

   colours = colors_from_canvas(canvas)

Adapters inspect colours that can be resolved from an already-created object.
They do not promise to resolve every theme default, gradient, texture,
transparency interaction, or data-driven colour expression.
