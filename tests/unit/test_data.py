#!/usr/bin/env python3

import os
import numpy
import pytest
import tempfile

import reproducible
import reproducible.data.keras


class PlaceholderClass:
    def __init__(self, value):
        self.value = value


def test_file_data_create():
    (fh, filename) = tempfile.mkstemp()
    os.write(fh, b"foo")
    os.close(fh)
    data = reproducible.FileData(filename)
    assert data.cache_id(None) ==\
           '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
    os.unlink(filename)


def test_file_data_update(monkeypatch):
    (fh, filename) = tempfile.mkstemp()
    os.write(fh, b"foo")
    os.close(fh)
    data = reproducible.FileData(filename)

    monkeypatch.setattr('os.path.getmtime', lambda x: 0)
    assert data.cache_id(None) ==\
           '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
    fh = os.open(filename, os.O_WRONLY | os.O_BINARY)
    os.write(fh, b"bar")
    os.fsync(fh)
    os.close(fh)
    monkeypatch.setattr('os.path.getmtime', lambda x: 1)
    assert data.cache_id(None) == \
           'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9'
    os.unlink(filename)


def test_object_data_strings():
    object_data_1 = reproducible.ObjectData('foo')
    object_data_2 = reproducible.ObjectData('foo')
    object_data_3 = reproducible.ObjectData('bar')

    assert object_data_1.cache_id(None) == object_data_2.cache_id(None)
    assert object_data_1.cache_id(None) != object_data_3.cache_id(None)


def test_object_data_strings():
    object_data_1 = reproducible.ObjectData(b'foo')
    object_data_2 = reproducible.ObjectData(b'foo')
    object_data_3 = reproducible.ObjectData(b'bar')
    object_data_4 = reproducible.ObjectData('foo')

    assert object_data_1.cache_id(None) == object_data_2.cache_id(None)
    assert object_data_1.cache_id(None) != object_data_3.cache_id(None)
    assert object_data_1.cache_id(None) != object_data_4.cache_id(None)


def test_object_data_numpy():
    x = numpy.random.randn(100, 2)
    y = numpy.random.randn(2, 100)
    z = x.reshape(2, 100)
    object_data_1 = reproducible.ObjectData(x)
    object_data_2 = reproducible.ObjectData(x)
    object_data_3 = reproducible.ObjectData(y)
    object_data_4 = reproducible.ObjectData(z)

    assert object_data_1.cache_id(None) == object_data_2.cache_id(None)
    assert object_data_1.cache_id(None) != object_data_3.cache_id(None)
    assert object_data_1.cache_id(None) != object_data_4.cache_id(None)


def test_object_data_object():
    x1 = PlaceholderClass('x')
    x2 = PlaceholderClass('x')
    y = PlaceholderClass('y')

    object_data_x1 = reproducible.ObjectData(x1)
    object_data_x2 = reproducible.ObjectData(x2)
    object_data_y = reproducible.ObjectData(y)

    assert object_data_x1.cache_id(None) == object_data_x2.cache_id(None)
    assert object_data_x1.cache_id(None) != object_data_y.cache_id(None)


def test_object_auto_object():
    x = PlaceholderClass('x')
    data = reproducible.get_data_wrapper(x)
    assert isinstance(data, reproducible.ObjectData)
    data.cache_id(None)


def test_object_auto_model():
    import keras.models, keras.layers
    x = keras.models.Sequential([keras.layers.Dense(32, input_shape=(2, ))])
    data = reproducible.get_data_wrapper(x)
    assert isinstance(data, reproducible.data.keras.ModelData)
    data.cache_id(None)


def test_keras_model():
    import keras.models, keras.layers
    x = keras.models.Sequential([keras.layers.Dense(32, input_shape=(2, ))])
    data = reproducible.get_data_wrapper(x)
    assert isinstance(data, reproducible.data.keras.ModelData)
    data_rt = reproducible.data.keras.ModelData.loads(data.dumps())

    assert data.model.get_config() == data_rt.model.get_config()

    weights_initial = data.model.get_weights()
    weights_roundtrip = data_rt.model.get_weights()
    assert len(weights_initial) == len(weights_roundtrip)
    for i in range(len(weights_initial)):
        assert (weights_initial[i] == weights_roundtrip[i]).all()
