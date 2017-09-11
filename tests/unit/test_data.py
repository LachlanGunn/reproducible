#!/usr/bin/env python3

import io
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


DATA_OBJECT_EXAMPLES = [
    (reproducible.ObjectData, PlaceholderClass('x')),
    (reproducible.FileData, tempfile.mkstemp()[1]),
]


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


@pytest.mark.parametrize('datatype,test_object', DATA_OBJECT_EXAMPLES)
def test_data_roundtrip_string_out_string_in(datatype, test_object):
    object_data_x1 = datatype(test_object)
    object_data_x2 = datatype.loads(object_data_x1.dumps())
    assert object_data_x1.value == object_data_x2.value


@pytest.mark.parametrize('datatype,test_object', DATA_OBJECT_EXAMPLES)
def test_data_roundtrip_string_out_file_in(datatype, test_object):
    object_data_x1 = datatype(test_object)
    serialised_object = object_data_x1.dumps()
    serialised_object_file = io.BytesIO(serialised_object)
    object_data_x2 = datatype.load(serialised_object_file)
    assert object_data_x1.value == object_data_x2.value


@pytest.mark.parametrize('datatype,test_object', DATA_OBJECT_EXAMPLES)
def test_data_roundtrip_file_out_string_in(datatype, test_object):
    object_data_x1 = datatype(test_object)
    serialised_object_file = io.BytesIO()
    object_data_x1.dump(serialised_object_file)
    object_data_x2 = datatype.loads(serialised_object_file.getvalue())
    assert object_data_x1.value == object_data_x2.value


@pytest.mark.parametrize('datatype,test_object', DATA_OBJECT_EXAMPLES)
def test_data_roundtrip_file_out_file_in(datatype, test_object):
    object_data_x1 = datatype(test_object)
    serialised_object_file = io.BytesIO()
    object_data_x1.dump(serialised_object_file)
    serialised_object_file.seek(0)
    object_data_x2 = datatype.load(serialised_object_file)
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
def test_keras_model():
    import keras.models, keras.layers
    import reproducible.data.keras
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
