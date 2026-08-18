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

Matplotlib and Seaborn
----------------------

Seaborn produces Matplotlib figures, so both use the Matplotlib adapter:

.. code-block:: python

   from cvdlint.adapters.matplotlib import check_figure

   result = check_figure(fig)
   result.raise_for_failure()

Plotly
------

.. code-block:: python

   from cvdlint.adapters.plotly import check_figure

   result = check_figure(fig)

PyROOT
------

.. code-block:: python

   from cvdlint.adapters.root import check_canvas

   result = check_canvas(canvas)

Adapters inspect colours that can be resolved from an already-created object.
They do not promise to resolve every theme default, gradient, texture,
transparency interaction, or data-driven colour expression.
