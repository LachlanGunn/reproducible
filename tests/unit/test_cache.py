#!/usr/bin/env python3

import tempfile

import reproducible
import numpy


def test_memory_cache():
    cache = reproducible.MemoryCache()

    cache.set('foo', 'bar')
    assert cache.is_cached('foo')
    assert cache.get('foo') == 'bar'
    assert not cache.is_cached('baz')


def test_file_cache_strings():
    with tempfile.TemporaryDirectory() as root_dir:
        cache = reproducible.FileCache(root_dir)

        cache.set('foo', 'bar')
        assert cache.is_cached('foo')
        assert cache.get('foo') == 'bar'
        assert not cache.is_cached('baz')


def test_file_cache_objects():
    with tempfile.TemporaryDirectory() as root_dir:
        cache = reproducible.FileCache(root_dir)

        cache.set('foo', ['bar', 'baz'])
        assert cache.is_cached('foo')
        assert cache.get('foo') == ['bar', 'baz']
        assert not cache.is_cached('bar')


def test_file_cache_numpy():
    with tempfile.TemporaryDirectory() as root_dir:
        cache = reproducible.FileCache(root_dir)

        x = numpy.random.randn(100, 100)

        cache.set('foo', x)
        assert cache.is_cached('foo')
        assert (cache.get('foo') == x).all()
