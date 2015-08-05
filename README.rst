Objects
=======

Dependency injection framework for Python projects.

+---------------------------------------+-------------------------------------------------------------------+
| *PyPi*                                | .. image:: https://img.shields.io/pypi/v/Objects.svg              |
|                                       |    :target: https://pypi.python.org/pypi/Objects/                 |
|                                       |    :alt: Latest Version                                           |
|                                       | .. image:: https://img.shields.io/pypi/dm/Objects.svg             |
|                                       |    :target: https://pypi.python.org/pypi/Objects/                 |
|                                       |    :alt: Downloads                                                |
|                                       | .. image:: https://img.shields.io/pypi/l/Objects.svg              |
|                                       |    :target: https://pypi.python.org/pypi/Objects/                 |
|                                       |    :alt: License                                                  |
+---------------------------------------+-------------------------------------------------------------------+
| *Python versions and implementations* | .. image:: https://img.shields.io/pypi/pyversions/Objects.svg     |
|                                       |    :target: https://pypi.python.org/pypi/Objects/                 |
|                                       |    :alt: Supported Python versions                                |
|                                       | .. image:: https://img.shields.io/pypi/implementation/Objects.svg |
|                                       |    :target: https://pypi.python.org/pypi/Objects/                 |
|                                       |    :alt: Supported Python implementations                         |
+---------------------------------------+-------------------------------------------------------------------+
| *Builds and tests coverage*           | .. image:: https://travis-ci.org/rmk135/objects.svg?branch=master |
|                                       |    :target: https://travis-ci.org/rmk135/objects                  |
|                                       |    :alt: Build Status                                             |
|                                       | .. image:: https://coveralls.io/repos/rmk135/objects/badge.svg    |
|                                       |    :target: https://coveralls.io/r/rmk135/objects                 |
|                                       |    :alt: Coverage Status                                          |
+---------------------------------------+-------------------------------------------------------------------+

*Objects* is a dependency injection framework for Python projects. 
It was designed to be unified, developer's friendly tool for managing any kind
of Python objects and their dependencies in formal, pretty way.

Below is a list of some key features and points of *Objects* framework:

- Easy, smart, pythonic style.
- Obvious, clear structure.
- Memory efficiency.
- Semantic versioning.

Main idea of *Objects* is to keep dependencies under control.

Installation
------------

*Objects* library is available on PyPi_::

    pip install objects

Documentation
-------------

*Objects* documentation is hosted on ReadTheDocs:

- `Stable version`_
- `Latest version`_

Examples
--------

.. code-block:: python

    """Concept example of `Objects`."""

    from objects.catalog import AbstractCatalog

    from objects.providers import Factory
    from objects.providers import Singleton

    from objects.injections import KwArg
    from objects.injections import Attribute
    from objects.decorators import inject

    import sqlite3


    class ObjectA(object):

        """Example class ObjectA, that has dependency on database."""

        def __init__(self, db):
            """Initializer."""
            self.db = db


    class ObjectB(object):

        """Example class ObjectB, that has dependencies on ObjectA and database."""

        def __init__(self, a, db):
            """Initializer."""
            self.a = a
            self.db = db


    class Catalog(AbstractCatalog):

        """Catalog of objects providers."""

        database = Singleton(sqlite3.Connection,
                             KwArg('database', ':memory:'),
                             Attribute('row_factory', sqlite3.Row))
        """:type: (objects.Provider) -> sqlite3.Connection"""

        object_a_factory = Factory(ObjectA,
                                   KwArg('db', database))
        """:type: (objects.Provider) -> ObjectA"""

        object_b_factory = Factory(ObjectB,
                                   KwArg('a', object_a_factory),
                                   KwArg('db', database))
        """:type: (objects.Provider) -> ObjectB"""


    # Catalog static provides.
    a1, a2 = Catalog.object_a_factory(), Catalog.object_a_factory()
    b1, b2 = Catalog.object_b_factory(), Catalog.object_b_factory()

    assert a1 is not a2
    assert b1 is not b2
    assert a1.db is a2.db is b1.db is b2.db is Catalog.database()


    # Example of inline injections.
    @inject(KwArg('a', Catalog.object_a_factory))
    @inject(KwArg('b', Catalog.object_b_factory))
    @inject(KwArg('database', Catalog.database))
    def example(a, b, database):
        """Example callback."""
        assert a.db is b.db is database is Catalog.database()


    example()

You can get more *Objects* examples in ``/examples`` directory on
GitHub:

    https://github.com/rmk135/objects


Feedback
--------

Feel free to post questions, bugs, feature requests, proposals etc. on
*Objects*  GitHub Issues:

    https://github.com/rmk135/objects/issues

Your feedback is quite important!


.. _PyPi: https://pypi.python.org/pypi/Objects
.. _Stable version: http://objects.readthedocs.org/en/stable/
.. _Latest version: http://objects.readthedocs.org/en/latest/
.. _SLOC: http://en.wikipedia.org/wiki/Source_lines_of_code
.. _SOLID: http://en.wikipedia.org/wiki/SOLID_%28object-oriented_design%29
.. _IoC: http://en.wikipedia.org/wiki/Inversion_of_control
.. _dependency injection: http://en.wikipedia.org/wiki/Dependency_injection
