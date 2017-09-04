#!/usr/bin/env python3

import base64
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
    def make_cache_value(value: object) -> str:
        if isinstance(value, reproducible.Data):
            return value.cache_id(None)
        else:
            return reproducible.get_data_wrapper(value).cache_id(None)

    def wrapper(*args, **kwargs):
        cache = reproducible.get_cache()

        cache_string_parts = []
        for i, arg in enumerate(args):
            cache_value = make_cache_value(arg)
            cache_string_parts.append('arg_%d=%s' % (i, cache_value))

        for key in sorted(kwargs):
            cache_value = make_cache_value(kwargs[key])
            cache_string_parts.append('kwarg_%s=%s' % (key, cache_value))

        hash_context = reproducible.hash_family()
        hash_context.update(inspect.getsource(func).encode('utf8'))
        func_hash = str(base64.b16encode(hash_context.digest()), 'ascii')

        cache_string = '%s:%s:[%s]' % (func.__name__, func_hash,
                                       ','.join(cache_string_parts))
        if cache.is_cached(cache_string):
            return cache.get(cache_string)

        result = func(*args, **kwargs)
        cache.set(cache_string, result)
        return result

    return wrapper
