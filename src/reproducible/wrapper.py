#!/usr/bin/env python3

import reproducible


def operation(cache: reproducible.Cache):
    def operation_decorator(func):
        def make_cache_value(value: object) -> str:
            if isinstance(value, reproducible.Data):
                return value.cache_id(None)
            else:
                return reproducible.ObjectData(value).cache_id(None)

        def wrapper(*args, **kwargs):
            cache_string_parts = []
            for i, arg in enumerate(args):
                cache_value = make_cache_value(arg)
                cache_string_parts.append('arg_%d=%s' % (i, cache_value))

            for key, value in sorted(kwargs):
                cache_value = make_cache_value(value)
                cache_string_parts.append('kwarg_%s=%s' % (key, cache_value))

            cache_string = func.__name__ + '[%s]' % ':'.join(cache_string_parts)
            if cache.is_cached(cache_string):
                return cache.get(cache_string)

            result = func(*args, **kwargs)
            cache.set(cache_string, result)
            return result

        return wrapper

    return operation_decorator
