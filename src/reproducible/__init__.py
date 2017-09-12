#!/usr/bin/env python3
"""Reproducible scientific computing tools for Python

The reproducible module for Python provides tools to aid in performing
reproducible scientific computation.

By supporting a more functional style of programming, we allow parameters
to be described at the top level of a computation. This will allow us to
make full use of the literate programming capabilities provided by
PythonTex without either a long wait every time we compile or external
result caches that must be kept in sync.
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import hashlib

from .cache import *
from .data import *
from .wrapper import *

hash_family = hashlib.sha256

__all__ = ['operation', 'cache_ignore',
           'set_cache', 'MemoryCache', 'FileCache']
