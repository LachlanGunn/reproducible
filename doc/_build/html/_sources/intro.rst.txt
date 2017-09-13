===========
Basic Usage
===========

------------
Installation
------------

:mod:`reproducible` can be installed directly from Github using `pip`::

    $ pip install https://github.com/LachlanGunn/reproducible

The module is compatible with Python ≥2.7 and ≥3.4.

--------
Synopsis
--------

We demonstrate the use of :mod:`reproducible` with a simple example::

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

