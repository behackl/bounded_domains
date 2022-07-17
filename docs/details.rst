Miscellaneous Details
=====================

Project Overview
----------------

The project is implemented in form of a small Python package. In
the root directory, ``pyproject.toml`` contains the project
dependencies. As a project management tool `Poetry <https://python-poetry.org/>`__
is used; ``poetry.lock`` is the corresponding dependency lockfile.

The ``bounded_domains`` directory contains the module implementation;
the code is distributed into three submodules (see :doc:`reference`
for a description of the modules and their members).

In the ``tests`` directory there are some test files that can be run
with ``pytest``. In fact, every time a commit is pushed to the
repository on GitHub, the configuration in ``.github/workflows/ci.yml``
triggers the tests to be run on the instances tagged with
``ubuntu-latest``, ``macos-latest``, and ``windows-latest``, each
for Python version ``3.7``, ``3.8``, and ``3.9``.

The project also has a setup linter and code style check: for linting,
``flake8`` configured via the ``.flake8`` file is used, and the code
style is checked and enforced via `Black <https://github.com/psf/black>`__.

The ``docs`` directory contains the basic configuration for the
documentation pages you are currently reading. The pages are deployed
manually (because setting up automatic deployment did not quite pay off
for this project).

And finally, ``demo.ipynb`` contains a Jupyter notebook illustrating
basic usage of the package.

.. NOTE::

    ``notebook`` has not been specified as a dependency of ``bounded_domains``.
    Be sure to ``pip install notebook`` in case you run into problems when
    trying to play the file.


Quadrilaterals instead of Triangles
-----------------------------------

The present implementation of :class:`.PolygonalDomain` relies on
the passed :class:`.Element` objects describing triangles. Theoretically,
more complex structures (like quadrilaterals) would be possible too.
Depending on the concrete use case, the implementation has to be changed
more or less substantially:

- In case it is only important that users should be able to pass
  quadrilaterals (or general polygons), then I propose implementing
  :class:`.Element` such that internally a triangulation of the element
  is computed and stored. All other structures would then still use
  (and *rely* on) the fact that internally the domain is still triangulated.
  As an example: :meth:`.PolygonalDomain.closest_element` might then
  find that one of the internally created triangular elements is the
  closest one; it would be easy to return the index of the (more complex)
  original element instead of the determined sub-element.
- Otherwise, if for whatever reason computations have to happen with
  quadrilaterals, then several methods have to be changed substantially
  -- among them, for example, :meth:`.PolygonalDomain.build_mappings`
  (for the adjacent vertex mapping, etc.).
