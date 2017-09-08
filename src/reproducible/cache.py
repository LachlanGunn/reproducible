#!/usr/bin/env python3

import os.path
import pickle

import reproducible
import reproducible.data
import sys


class Cache(object):
    def set(self, key, value):
        raise NotImplementedError("This is an abstract cache.")

    def get(self, key):
        raise NotImplementedError("This is an abstract cache.")

    def is_cached(self, key: str) -> bool:
        return False


class MemoryCache(Cache):
    def __init__(self):
        super().__init__()
        self.cache = {}

    def set(self, key: str, value: reproducible.data.Data) -> None:
        self.cache[key] = value

    def get(self, key: str) -> object:
        return self.cache.get(key)

    def is_cached(self, key: str) -> bool:
        return key in self.cache.keys()


class FileCache(Cache):
    @classmethod
    def __check_directory__(cls, root: str) -> bool:
        return os.path.isdir(root)

    def __init__(self, root: str, debug: bool=False):
        super().__init__()
        if not self.__check_directory__(root):
            os.mkdir(root)
        self.root = root
        self.debug = debug

    def is_cached(self, key: str) -> bool:
        return self.__check_directory__(os.path.join(self.root, key))

    def get(self, key: str) -> object:
        if self.debug:
            print("GET %s\n -> " % (key), file=sys.stderr, end="")
        base_path = os.path.join(self.root, key)
        with open(os.path.join(base_path, 'data'), 'rb') as fh, \
             open(os.path.join(base_path, 'type'), 'rb') as fh_type:
            data_type = pickle.load(fh_type)
            if self.debug:
                data = fh.read()
                hash_context = reproducible.hash_family()
                hash_context.update(data)
                print(hash_context.hexdigest(), file=sys.stderr)
                return data_type.loads(data)
            return data_type.load(fh)

    def set(self, key: str, value: reproducible.data.Data):
        if self.debug:
            print('SET %s' % key, file=sys.stderr)
        base_path = os.path.join(self.root, key)
        if not self.__check_directory__(base_path):
            os.mkdir(base_path)
        with open(os.path.join(base_path, 'data'), 'wb') as fh, \
             open(os.path.join(base_path, 'type'), 'wb') as fh_type:
            value.dump(fh)
            pickle.dump(type(value), fh_type)


def set_cache(cache: Cache) -> None:
    global _cache
    _cache = cache


def get_cache() -> Cache:
    global _cache
    return _cache


_cache = MemoryCache()
