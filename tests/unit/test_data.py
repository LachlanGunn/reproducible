#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import io
import itertools
import os
import numpy
import pytest
import tempfile

import reproducible


class PlaceholderClass:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value


IO_TYPES = ['string', 'file']

DATA_OBJECT_EXAMPLE_OBJECTS = {
    reproducible.ObjectData: PlaceholderClass('x'),
    reproducible.FileData: tempfile.mkstemp()[1],
}

DATA_OBJECT_EXAMPLES = \
    [(reproducible.ObjectData, out_type, in_type)
        for out_type, in_type in itertools.product(IO_TYPES, IO_TYPES)] + \
    [(reproducible.FileData,   out_type, in_type)
        for out_type, in_type in itertools.product(IO_TYPES, IO_TYPES)]


def test_ignored_data():
    x = PlaceholderClass('x')
    x_ignored = reproducible.cache_ignore(x)
    assert x == x_ignored

    x_ignored.value = 'Hello!'
    # We use x.value here to make sure that it is touching the original object.
    assert x.value == 'Hello!'


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
    fh = os.open(filename, os.O_WRONLY)
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


@pytest.mark.parametrize('datatype,out_type,in_type', DATA_OBJECT_EXAMPLES)
def test_data_roundtrips(out_type, in_type, datatype):
    test_object = DATA_OBJECT_EXAMPLE_OBJECTS[datatype]
    object_data_x1 = datatype(test_object)

    if out_type == 'string':
        serialised_data = object_data_x1.dumps()
    elif out_type == 'file':
        sio = io.BytesIO()
        object_data_x1.dump(sio)
        serialised_data = sio.getvalue()
    else:
        raise ValueError("Invalid type parameter.")

    if in_type == 'string':
        object_data_x2 = datatype.loads(serialised_data)
    elif in_type == 'file':
        sio = io.BytesIO(serialised_data)
        object_data_x2 = datatype.load(sio)
    else:
        raise ValueError("Invalid type parameter.")

    assert object_data_x1.value == object_data_x2.value


@pytest.mark.slow
def test_object_auto_model():
    import keras.models, keras.layers
    import reproducible.data.keras
    x = keras.models.Sequential([keras.layers.Dense(32, input_shape=(2, ))])
    data = reproducible.get_data_wrapper(x)
    assert isinstance(data, reproducible.data.keras.ModelData)
    data.cache_id(None)


@pytest.mark.slow
@pytest.mark.parametrize('out_type,in_type', [
    ('string', 'string'),
    ('string', 'file'),
    ('file', 'string'),
    ('file', 'file'),
])
def test_keras_model(out_type, in_type):
    import keras.models, keras.layers
    import reproducible.data.keras
    x = keras.models.Sequential([keras.layers.Dense(32, input_shape=(2, ))])
    data = reproducible.get_data_wrapper(x)
    assert isinstance(data, reproducible.data.keras.ModelData)

    if out_type == 'string':
        serialised_data = data.dumps()
    elif out_type == 'file':
        sio = io.BytesIO()
        data.dump(sio)
        serialised_data = sio.getvalue()
    else:
        raise ValueError("Invalid type parameter.")

    if in_type == 'string':
        data_rt = reproducible.data.keras.ModelData.loads(serialised_data)
    elif in_type == 'file':
        sio = io.BytesIO(serialised_data)
        data_rt = reproducible.data.keras.ModelData.load(sio)
    else:
        raise ValueError("Invalid type parameter.")

    assert data.value.get_config() == data_rt.value.get_config()

    weights_initial = data.value.get_weights()
    weights_roundtrip = data_rt.value.get_weights()
    assert len(weights_initial) == len(weights_roundtrip)
    for i in range(len(weights_initial)):
        assert (weights_initial[i] == weights_roundtrip[i]).all()
