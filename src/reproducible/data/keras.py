#!/usr/bin/env python3

import base64
import keras.models
import numpy
import reproducible


class ModelData(reproducible.generic.Data):
    def __init__(self, model: keras.models.Model):
        self.model = model

    def cache_id(self, context):
        hash_context = reproducible.hash_family()
        hash_context.update(type(self.model).__name__.encode('utf8'))
        hash_context.update(self.model.to_json().encode('utf8'))
        hash_context.update(';'.join([
            numpy.array2string(weight) for weight in self.model.get_weights()
        ]).encode('utf8'))
        return str(base64.b16encode(hash_context.digest()), 'ascii').lower()


reproducible.register_type(keras.models.Model, ModelData)
