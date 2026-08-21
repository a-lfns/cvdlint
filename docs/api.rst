API reference
=============

Core API
--------

.. autofunction:: cvdlint.palette_check

.. autofunction:: cvdlint.palette_dist

.. autofunction:: cvdlint.simulate_palette

.. autofunction:: cvdlint.check_figure

Result models
-------------

.. autoclass:: cvdlint.CheckResult
   :members:

.. autoclass:: cvdlint.ConditionSummary
   :members:

.. autoclass:: cvdlint.ProblemPair
   :members:

Matplotlib and Seaborn adapter
------------------------------

.. autofunction:: cvdlint.adapters.matplotlib.colors_from_figure

.. autofunction:: cvdlint.adapters.matplotlib.check_figure

Plotly adapter
--------------

.. autofunction:: cvdlint.adapters.plotly.colors_from_figure

.. autofunction:: cvdlint.adapters.plotly.check_figure

PyROOT adapter
--------------

.. autofunction:: cvdlint.adapters.root.colors_from_canvas

.. autofunction:: cvdlint.adapters.root.check_canvas
