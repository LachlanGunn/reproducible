=======
Caching
=======

Much of the utility of :mod:`reproducible` is lost if we do not
cache our results.  The (global) cache can be set
using :func:`set_cache <reproducible.set_cache>`,
which can accept instances of other cache types::

    reproducible.set_cache(SomeCacheClass())

By default we use a memory-backed
cache, implemented by :class:`MemoryCache <reproducible.MemoryCache>`.
However, for most purposes, we desire a cache that persists longer than
the Python interpreter.  To this end, we provide the
:class:`FileCache <reproducible.FileCache>`
class, which is used as below::

    reproducible.set_cache(reproducible.FileCache("/path/to/cache/"))

This setting applies globally.  :class:`FileCache <reproducible.FileCache>`
will automatically create the directory if it does not exist.

.. warning:: **Never use a cache whose contents you do not trust.**
    Many objects are serialised using :mod:`pickle <python:pickle>`,
    which allows the execution of arbitrary code when its output
    is read back.

The cache is not automatically purged, and changes to arguments and
function source-code will result in a directory whose size will
grow without bound.