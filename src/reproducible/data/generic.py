#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import base64
import os.path
import pickle

import reproducible

auto_type_registry = {}


class Data(object):
    pass


class IgnoredData(Data):
    def __init__(self):  # pragma: no cover
        pass


def cache_ignore(obj):
    """Ignore an object when deciding whether or not to cache.

    `cache_ignore` returns a proxy object that can be detected as data
    to be ignored.  When passed to a function wrapped in
    :func:`@reproducible.operation <reproducible.operation>`, its value
    will not be considered when determining whether the result is already
    cached.

    This is useful when configuration data is passed into a function
    that is necessary to run the computation, but does not affect
    the final result, for example the address of a remote server.

    Args:
        obj (object): The object to be ignored.

    Return:
        A proxy object for obj that will be ignored for caching purposes.
    """

    class IgnoredObjectData(obj.__class__, IgnoredData):
        def __init__(self):
            pass

        def __getattr__(self, item):
            return getattr(obj, item)

        def __setattr__(self, key, value):
            return setattr(obj, key, value)

    return IgnoredObjectData()


def cache_ignored(obj):
    """Determine whether or not an object should be ignored while caching."""
    return isinstance(obj, IgnoredData)


class ObjectData(Data):
    def __init__(self, value):
        # type: (object) -> None
        super(ObjectData, self).__init__()
        self.obj = value

    @property
    def value(self):
        return self.obj

    def cache_id(self, _):
        hash_context = reproducible.hash_family()
        hash_context.update(type(self.obj).__name__.encode('utf8'))
        hash_context.update(self.dumps())
        return base64.b16encode(hash_context.digest()).decode('utf8')

    def dump(self, fh):
        return pickle.dump(self.obj, fh)

    def dumps(self):
        return pickle.dumps(self.obj)

    @classmethod
    def load(cls, fh):
        return ObjectData(pickle.load(fh))

    @classmethod
    def loads(cls, s):
        return ObjectData(pickle.loads(s))


class FileData(Data):
    def __init__(self, filename):
        super(FileData, self).__init__()
        self.filename = filename
        self.id_cached = None
        self.id_cached_modification_time = None

    @property
    def value(self):
        return self.filename

    def cache_id(self, _):
        modification_time = os.path.getmtime(self.filename)
        if (not self.id_cached
                or modification_time > self.id_cached_modification_time):
            with open(self.filename, 'rb') as fh:
                hash_context = reproducible.hash_family()
                for chunk in iter(lambda: fh.read(1024), b''):
                    hash_context.update(chunk)
                file_hash = hash_context.digest()
                self.id_cached = base64.b16encode(file_hash).decode(
                    'ascii').lower()
                self.id_cached_modification_time = modification_time

        return self.id_cached

    def dump(self, fh):
        fh.write(self.filename.encode('utf8'))

    def dumps(self):
        return self.filename.encode('utf8')

    @classmethod
    def load(cls, fh):
        return FileData(fh.read().decode('utf8'))

    @classmethod
    def loads(cls, s):
        return FileData(s.decode('utf8'))


def get_data_wrapper(obj):
    """Automatically select the right reproducible.Data type for an object."""
    for key in auto_type_registry:
        if isinstance(obj, key):
            return auto_type_registry[key](obj)
    return ObjectData(obj)


def register_type(datatype, handler):
    """Register a type in the auto-wrapper."""
    auto_type_registry[datatype] = handler
