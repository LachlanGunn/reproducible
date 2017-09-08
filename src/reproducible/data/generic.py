#!/usr/bin/env python3

import abc
import base64
import os.path
import numbers
import pickle

import reproducible
import numpy

auto_type_registry = {}


def cache_ignore(obj):
    """Ignore an object when deciding whether or not to cache."""

    class IgnoredObjectData(type(obj), IgnoredData):
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


class Data(abc.ABC):
    pass


class IgnoredData(Data):
    def __init__(self):
        pass


class ObjectData(Data):
    def __init__(self, value: object):
        super().__init__()
        self.obj = value

    @property
    def value(self):
        return self.obj

    def cache_id(self, context):
        hash_context = reproducible.hash_family()
        hash_context.update(type(self.obj).__name__.encode('utf8'))
        hash_context.update(self.dumps())
        return str(base64.b16encode(hash_context.digest()), 'utf8')

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
        super().__init__()
        self.filename = filename
        self.id_cached = None
        self.id_cached_modification_time = None

    @property
    def value(self):
        return self.filename

    def cache_id(self, context):
        modification_time = os.path.getmtime(self.filename)
        if (not self.id_cached
                or modification_time > self.id_cached_modification_time):
            with open(self.filename, 'rb') as fh:
                hash_context = reproducible.hash_family()
                for chunk in iter(lambda: fh.read(1024), b''):
                    hash_context.update(chunk)
                file_hash = hash_context.digest()
                self.id_cached = str(base64.b16encode(file_hash),
                                     'ascii').lower()
                self.id_cached_modification_time = modification_time

        return self.id_cached

    def dump(self, fh):
        fh.write(self.filename.encode('utf8'))

    def dumps(self):
        return self.filename.encode('utf8')

    @classmethod
    def load(cls, fh):
        return FileData(str(fh.read(), 'utf8'))

    @classmethod
    def loads(cls, s):
        return FileData(str(s, 'utf8'))


def get_data_wrapper(obj):
    """Automatically select the right reproducible.Data type for an object."""
    for key in auto_type_registry:
        if isinstance(obj, key):
            return auto_type_registry[key](obj)
    return ObjectData(obj)


def register_type(datatype, handler):
    """Register a type in the auto-wrapper."""
    auto_type_registry[datatype] = handler
