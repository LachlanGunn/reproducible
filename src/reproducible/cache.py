#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import os.path
import pickle

import reproducible
import reproducible.data


class Cache(object):
    pass


class MemoryCache(Cache):
    """Memory-backed cache.

    MemoryCache provides a key-value object store in memory, stored in
    a standard dictionary.
    """
    def __init__(self):
        super(MemoryCache, self).__init__()
        self.cache = {}

    def set(self, key, value):
        # type: (str, reproducible.data.Data) -> None
        self.cache[key] = value

    def get(self, key):
        # type: (str) -> object
        return self.cache.get(key)

    def is_cached(self, key):
        # type: (str) -> bool
        return key in self.cache.keys()


class FileCache(Cache):
    """Disk-backed cache.

    FileCache provides a key-value store on disk.  Each item in the cache
    has a directory, named for its key.  The directory contains two files:

        - /type: The pickled object type.
        - /data: The serialised data itself.

    As the objects in question are of type reproducible.Data, we can use
    the unpickled type object to get access to the appropriate
    .load() class method.
    """
    @classmethod
    def __check_directory__(cls, root):
        # type: (str) -> bool
        return os.path.isdir(root)

    def __init__(self, root, debug=None):
        """
        Args:
            root   (str): The root directory of the cache.
            debug (file): A file-like object to which to log cache accesses.
        """
        # type: (str, bool) -> None
        super(FileCache, self).__init__()
        if not self.__check_directory__(root):
            os.mkdir(root)
        self.root = root
        self.debug = debug

    def is_cached(self, key):
        # type: (str) -> bool
        return self.__check_directory__(os.path.join(self.root, key))

    def get(self, key):
        # type: (str) -> object
        if self.debug:
            print("GET %s\n -> " % (key, ), file=self.debug, end="")
        base_path = os.path.join(self.root, key)
        with open(os.path.join(base_path, 'data'), 'rb') as fh, \
             open(os.path.join(base_path, 'type'), 'rb') as fh_type:
            data_type = pickle.load(fh_type)
            if self.debug:
                data = fh.read()
                hash_context = reproducible.hash_family()
                hash_context.update(data)
                print(hash_context.hexdigest(), file=self.debug)
                return data_type.loads(data)
            return data_type.load(fh)

    def set(self, key, value):
        # type: (str, reproducible.data.Data) -> None
        if self.debug:
            print('SET %s' % key, file=self.debug)
        base_path = os.path.join(self.root, key)
        if not self.__check_directory__(base_path):
            os.mkdir(base_path)
        with open(os.path.join(base_path, 'data'), 'wb') as fh, \
             open(os.path.join(base_path, 'type'), 'wb') as fh_type:
            value.dump(fh)
            pickle.dump(type(value), fh_type)


def set_cache(cache):
    """Set the global cache.

    Args:
        cache (reproducible.Cache): The new cache object.

    Return:
        Nothing.
    """
    # type: (Cache) -> None
    global _cache
    _cache = cache


def get_cache():
    # type: () -> Cache
    global _cache
    return _cache


_cache = MemoryCache()
