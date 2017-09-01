#!/usr/bin/env python3

import os.path
import pickle


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

    def set(self, key: str, value: object) -> None:
        self.cache[key] = value

    def get(self, key: str) -> object:
        return self.cache.get(key)

    def is_cached(self, key: str) -> bool:
        return key in self.cache.keys()


class FileCache(Cache):
    @classmethod
    def __check_directory__(cls, root: str) -> bool:
        return os.path.isdir(root)

    def __init__(self, root: str):
        super().__init__()
        if not self.__check_directory__(root):
            os.mkdir(root)
        self.root = root

    def is_cached(self, key: str) -> bool:
        return self.__check_directory__(os.path.join(self.root, key))

    def get(self, key: str) -> object:
        base_path = os.path.join(self.root, key)
        with open(os.path.join(base_path, 'data'), 'rb') as fh:
            return pickle.load(fh)

    def set(self, key: str, value: object):
        base_path = os.path.join(self.root, key)
        if not self.__check_directory__(base_path):
            os.mkdir(base_path)
        with open(os.path.join(base_path, 'data'), 'wb') as fh:
            pickle.dump(value, fh)
