cvdlint's documentation
=======

``cvdlint`` finds colour pairs that may become confusable under common
colour-vision deficiencies. It can lint palettes in source files without
executing them, check colours supplied on the command line, or validate
runtime palettes and plotting objects through its Python API.

.. code-block:: console

   pip install cvdlint
   cvdlint .

Start with :doc:`getting-started`, then choose the workflow that matches where
your colours exist.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   getting-started
   static-linter
   cli-configuration
   python-api-adapters
   methodology-limitations

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   licence
