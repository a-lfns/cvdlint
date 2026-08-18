Getting started
===============

Installation
------------

Install the core package from PyPI:

.. code-block:: console

   pip install cvdlint

Plotting adapters have optional dependencies:

.. code-block:: console

   pip install "cvdlint[matplotlib,plotly]"

PyROOT is supplied by the ROOT project, so the ``root`` extra does not install
it for you.

Choose a workflow
-----------------

Lint a project without executing its code:

.. code-block:: console

   cvdlint .

Check a known palette directly:

.. code-block:: console

   cvdlint '#E41A1C' '#4DAF4A' '#377EB8'

Check a palette produced at runtime:

.. code-block:: python

   from cvdlint import palette_check

   result = palette_check(["#E41A1C", "#4DAF4A", "#377EB8"])
   result.raise_for_failure()

The default policy reports simulated pairs whose CIEDE2000 distance is below
``10``. Exit status ``0`` means the CLI check passed, ``1`` means potential
confusion was found, and ``2`` means the input was invalid.

Next steps
----------

Read :doc:`static-linter` for supported source patterns,
:doc:`cli-configuration` for CI and project settings, and
:doc:`python-api-adapters` for runtime objects.
