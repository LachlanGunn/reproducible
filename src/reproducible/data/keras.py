#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import io
import json
import keras.models
import numpy
import reproducible


class ModelData(reproducible.generic.Data):
    def __init__(self, model: keras.models.Model):
        super(ModelData, self).__init__()
        self.model = model

    @property
    def value(self):
        return self.model

    def dumps(self):
        weights = []
        for weight in self.model.get_weights():
            sio = io.BytesIO()
            numpy.save(sio, weight)
            weights.append(str(base64.b64encode(sio.getvalue()), 'ascii'))
            sio.close()
        return json.dumps({
            'weights': weights,
            'architecture': self.model.to_json()
        }).encode('utf8')

    def dump(self, fh):
        fh.write(self.dumps())

    @classmethod
    def __from_dict(cls, parsed_data):
        model = keras.models.model_from_json(parsed_data['architecture'])
        weights = []
        for encoded_weights in parsed_data['weights']:
            sio = io.BytesIO(base64.b64decode(encoded_weights))
            weights.append(numpy.load(sio))
            sio.close()
        model.set_weights(weights)
        return ModelData(model)

    @classmethod
    def load(cls, fh):
        return cls.__from_dict(json.load(fh))

    @classmethod
    def loads(cls, s):
        return cls.__from_dict(json.loads(str(s, 'utf8')))

    def cache_id(self, context):
        hash_context = reproducible.hash_family()
        hash_context.update(type(self.model).__name__.encode('utf8'))
        hash_context.update(self.dumps())
        return str(base64.b16encode(hash_context.digest()), 'ascii').lower()


reproducible.register_type(keras.models.Model, ModelData)
