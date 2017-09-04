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
        hash_context.update(type(self.value).__name__.encode('utf8'))
        hash_context.update(self.value.to_json().encode('utf8'))
        hash_context.update(numpy.array2string(self.value.get_weights()))
        return str(base64.b16encode(hash_context.digest()),
                   'ascii').lower()


reproducible.register_type(keras.models.Model, ModelData)
