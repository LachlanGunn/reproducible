#!/usr/bin/env python3

import os
import tempfile

import reproducible


def test_file_data_create():
    (fh, filename) = tempfile.mkstemp()
    os.write(fh, b"foo")
    os.close(fh)
    data = reproducible.FileData(filename)
    assert data.cache_id(None) ==\
           '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
    os.unlink(filename)


def test_file_data_update():
    (fh, filename) = tempfile.mkstemp()
    os.write(fh, b"foo")
    os.close(fh)
    data = reproducible.FileData(filename)
    assert data.cache_id(None) ==\
           '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
    fh = os.open(filename, os.O_WRONLY | os.O_BINARY)
    os.write(fh, b"bar")
    os.close(fh)
    assert data.cache_id(None) == \
           'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9'
    os.unlink(filename)
