#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import functools
import inspect

import reproducible


def operation(func):
    """Make a function cacheable.

    The `@operation` decorator makes a function cacheable, with the cache
    in question being globally set with `reproducible.set_cache`.  Simply
    decorate a function definition with @operation, and the function return
    value will be cached.

    Cache lookup is performed with respect to all arguments.  An object which
    is not an instance of `reproducible.Data` will be wrapped with
    `reproducible.ObjectData` before its cache id is calculated.  There
    are special cases for some types, such as `numpy.ndarray`, but in
    general the cache id will be given by the SHA-256 checksum of the
    pickled value of the object.
    """

    def make_cache_value(value):
        # type: (object) -> str
        if isinstance(value, reproducible.Data):
            return value.cache_id(None)
        else:
            return reproducible.get_data_wrapper(value).cache_id(None)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache = reproducible.get_cache()

        cache_string_parts = []
        for i, arg in enumerate(args):
            if not reproducible.cache_ignored(arg):
                cache_value = make_cache_value(arg)
                cache_string_parts.append('arg_%d=%s' % (i, cache_value))

        for key in sorted(kwargs):
            if not reproducible.cache_ignored(kwargs[key]):
                cache_value = make_cache_value(kwargs[key])
                cache_string_parts.append('kwarg_%s=%s' % (key, cache_value))

        hash_context = reproducible.hash_family()
        hash_context.update(inspect.getsource(func).encode('utf8'))
        func_hash = base64.b16encode(hash_context.digest()).decode('ascii')

        hash_context = reproducible.hash_family()
        cache_string = '%s[%s]' % (func_hash, ':'.join(cache_string_parts))
        hash_context.update(cache_string.encode('utf8'))
        cache_key = func.__name__ + '.' + \
            base64.b16encode(hash_context.digest()).decode('utf8')

        if cache.is_cached(cache_key):
            return cache.get(cache_key).value

        result = func(*args, **kwargs)
        cache.set(cache_key, reproducible.get_data_wrapper(result))
        return result

    return wrapper
