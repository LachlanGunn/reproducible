#!/usr/bin/env python3

import reproducible
import tempfile

side_effects = 0


def test_wrapper():
    global side_effects

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


def test_wrapper_ignore_argument():
    global side_effects

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


def test_wrapper_file_cache():
    global side_effects
    with tempfile.TemporaryDirectory() as root_dir:
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
