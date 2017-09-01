#!/usr/bin/env python3

import reproducible

side_effects = 0


def test_wrapper():
    global side_effects

    cache = reproducible.MemoryCache()

    side_effects = 0

    @reproducible.operation(cache)
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
