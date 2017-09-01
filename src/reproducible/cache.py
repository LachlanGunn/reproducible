#!/usr/bin/env python3


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
