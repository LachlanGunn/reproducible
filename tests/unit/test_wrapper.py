#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import pytest
import reproducible
import shutil
import tempfile

side_effects = 0


@pytest.fixture
def memory_cache():
    return reproducible.MemoryCache()


def test_wrapper(memory_cache):
    global side_effects
    reproducible.set_cache(memory_cache)

    side_effects = 0

    @reproducible.operation
    def foo(x):
        global side_effects
        side_effects += 1
        return side_effects - 1

    foo(0)
    assert side_effects == 1
    foo(0)
    assert side_effects == 1
    foo(1)
    assert side_effects == 2
    foo('bar')
    assert side_effects == 3
    foo(1)
    assert side_effects == 3
    foo(x=1)
    assert side_effects == 4
    foo(x=1)
    assert side_effects == 4


def test_wrapper_use_data_directly(memory_cache):
    global side_effects
    reproducible.set_cache(memory_cache)

    side_effects = 0

    @reproducible.operation
    def bar(x):
        global side_effects
        side_effects += 1
        return side_effects - 1

    bar("x")
    assert side_effects == 1
    bar(reproducible.get_data_wrapper("x"))
    assert side_effects == 1


def test_wrapper_ignore_argument(memory_cache):
    global side_effects
    reproducible.set_cache(memory_cache)

    side_effects = 0

    @reproducible.operation
    def bar(x):
        global side_effects
        side_effects += 1
        return side_effects - 1

    bar(0)
    assert side_effects == 1
    bar(0)
    assert side_effects == 1
    bar(reproducible.cache_ignore(1))
    assert side_effects == 2
    bar(reproducible.cache_ignore(2))
    assert side_effects == 2

    class C(object):
        def __init__(self, x):
            self.x = x

    @reproducible.operation
    def check(obj):
        assert isinstance(obj, C)
        assert obj.x == 3

    bar(reproducible.cache_ignore(C(3)))


def test_wrapper_file_cache(memory_cache):
    global side_effects
    reproducible.set_cache(memory_cache)
    root_dir = tempfile.mkdtemp()
    try:
        reproducible.set_cache(reproducible.FileCache(root_dir))

        @reproducible.operation
        def baz(x):
            global side_effects
            side_effects += 1
            return side_effects - 1

        side_effects = 0
        baz(0)
        assert side_effects == 1
        baz(0)
        assert side_effects == 1
    finally:
        shutil.rmtree(root_dir)
