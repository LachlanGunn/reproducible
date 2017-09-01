#!/usr/bin/env python3

import base64
import os.path
import numbers
import pickle

import reproducible
import numpy


class Data(object):
    def __init__(self, parent):
        self.parent = parent

    def cache_id(self, context):
        raise NotImplementedError("Base Data class contains no data.")


class ObjectData(Data):
    def __init__(self, value: object):
        super().__init__(None)
        self.value = value

    def cache_id(self, context):
        if isinstance(self.value, numpy.ndarray):
            hash_context = reproducible.hash_family()
            hash_context.update(numpy.array_repr(self.value))
            return str(base64.b16encode(hash_context.digest()),
                       'ascii').lower()
        elif isinstance(self.value, numbers.Number):
            return str(self.value)
        elif isinstance(self.value, str):
            hash_context = reproducible.hash_family()
            hash_context.update(self.value.encode('utf8'))
            return str(base64.b16encode(hash_context.digest()),
                       'ascii').lower()
        elif isinstance(self.value, bytes):
            hash_context = reproducible.hash_family()
            hash_context.update(self.value)
            return str(base64.b16encode(hash_context.digest()),
                       'ascii').lower()
        else:
            hash_context = reproducible.hash_family()
            hash_context.update(pickle.dumps(self.value))
            return str(base64.b16encode(hash_context.digest()),
                       'ascii').lower()


class FileData(Data):
    def __init__(self, filename):
        super().__init__(None)
        self.filename = filename
        self.id_cached = None
        self.id_cached_modification_time = None

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
