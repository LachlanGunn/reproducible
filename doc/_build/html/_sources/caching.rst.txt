=======
Caching
=======

Much of the utility of :mod:`reproducible` is lost if we do not
persistently cache our results.  To this end, we provide the
:class:`FileCache` class, which is used as below::

    reproducible.set_cache(reproducible.FileCache("/path/to/cache/"))

This setting applies globally.  :class:`FileCache` will automatically create
the directory if it does not exist.

The cache is not automatically purged, and changes to arguments and
function source-code will result in a directory whose size will
grow without bound.