#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, unicode_literals

import tempfile

import reproducible
import numpy
import shutil


class PlaceholderClass:
    pass


def test_memory_cache():
    cache = reproducible.MemoryCache()

    cache.set('foo', reproducible.get_data_wrapper('bar'))
    assert cache.is_cached('foo')
    assert cache.get('foo').value == 'bar'
    assert not cache.is_cached('baz')


def test_file_cache_strings():
    root_dir = tempfile.mkdtemp()
    try:
        cache = reproducible.FileCache(root_dir)

        cache.set('foo', reproducible.get_data_wrapper('bar'))
        assert cache.is_cached('foo')
        assert cache.get('foo').value == 'bar'
        assert not cache.is_cached('baz')
    finally:
        shutil.rmtree(root_dir)


def test_file_cache_objects():
    root_dir = tempfile.mkdtemp()
    try:
        cache = reproducible.FileCache(root_dir)

        cache.set('foo', reproducible.get_data_wrapper(['bar', 'baz']))
        assert cache.is_cached('foo')
        assert cache.get('foo').value == ['bar', 'baz']
        assert not cache.is_cached('bar')

        value = PlaceholderClass()
        value.x = 'y'
        cache.set('bar', reproducible.get_data_wrapper(value))
        assert cache.is_cached('bar')
        assert cache.get('bar').value.x == 'y'
        assert cache.get('foo').value == ['bar', 'baz']
    finally:
        shutil.rmtree(root_dir)


def test_file_cache_numpy():
    with tempfile.TemporaryDirectory() as root_dir:
        cache = reproducible.FileCache(root_dir)

        x = numpy.random.randn(100, 2)

        cache.set('foo', reproducible.get_data_wrapper(x))
        assert cache.is_cached('foo')
        assert (cache.get('foo').value == x).all()


def test_file_cache_numpy():
    with tempfile.TemporaryDirectory() as root_dir:
        cache = reproducible.FileCache(root_dir)

        x = numpy.random.randn(100, 2)

        cache.set('foo', reproducible.get_data_wrapper(x))
        assert cache.is_cached('foo')
        assert (cache.get('foo').value == x).all()
