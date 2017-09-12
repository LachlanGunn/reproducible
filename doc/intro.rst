============
Introduction
============

The ``reproducible`` module for Python provides tools to aid in performing reproducible scientific computations.

By supporting a more functional style of programming, we allow parameters to
be described at the top level of a computation. This will allow us to make
full use of the literate programming capabilities provided by PythonTeX without
either a long wait every time we compile or external result caches that must
be kept in sync.

------------
Installation
------------

``reproducible`` can be installed directly from Github using `pip`::

    $ pip install https://github.com/LachlanGunn/reproducible

The module is compatible with Python ≥2.7 and ≥3.4.

--------
Synopsis
--------

We demonstrate the use of ``reproducible`` with a simple example::

    >>> def slow_add(a, b):
    ...     time.sleep(3)
    ...     return a+b

This function performs a simple computation, but uses a delay to simulate
more complex internals.  Repeated execution is slow::

    >>> %time slow_add(1, 2)
    Wall time: 3 s
    >>> %time slow_add(1, 2)
    Wall time: 3 s

We now define an identical function, but with the
:meth:`@reproducible.operation <reproducible.operation>` decorator::

    >>> @reproducible.operation
    ... def less_slow_add(a, b):
    ...     time.sleep(3)
    ...     return a+b

With the decorator, the results will be cached in memory::

    >>> %time less_slow_add(1, 2)
    Wall time: 3 s

    >>> %time less_slow_add(1, 2)
    Wall time: 502 µs

The function looks up cached results based on its arguments; if we
change the arguments, the computation will be performed again::

    >>> %time less_slow_add(2, 2)
    Wall time: 3 s

