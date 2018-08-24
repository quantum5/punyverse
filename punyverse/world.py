from __future__ import division

import json
import os
from collections import OrderedDict

import six

try:
    from punyverse._model import model_list, load_model
except ImportError:
    from punyverse.model import model_list, load_model

from punyverse.entity import *
from punyverse import texture


def load_world(file, callback=lambda message, completion: None):
    return World(file, callback)


class World(object):
    def __init__(self, file, callback):
        self.tracker = []
        self.start = (0, 0, 0)
        self.direction = (0, 0, 0)
        self.x = None
        self.y = None
        self.z = None
        self.tick_length = 1
        self.tick = 0

        self.callback = callback
        self._parse(file)
        del self.callback  # So it can't be used after loading finishes

    def evaluate(self, value):
        return eval(str(value), {'__builtins__': None}, self._context)

    @property
    def length(self):
        return self._length

    @property
    def au(self):
        return self._au

    def _parse(self, file):
        self.callback('Parsing configuration...', 'Loading configuration file...', 0)
        with open(os.path.join(os.path.dirname(__file__), file)) as f:
            root = json.load(f, object_pairs_hook=OrderedDict)
        self._au = root.get('au', 2000)
        self._length = root.get('length', 4320)
        self._context = {'AU': self._au, 'TEXTURE': texture.max_texture, 'KM': 1.0 / self._length}

        tick = root.get('tick', 4320)  # How many second is a tick?
        self.tick_length = tick

        # Need to know how many objects are being loaded
        self._objects = 0
        self._current_object = 0

        def count_objects(bodies):
            for body in six.itervalues(bodies):
                self._objects += 1
                count_objects(body.get('satellites', {}))
        count_objects(root['bodies'])

        if 'start' in root:
            info = root['start']
            x = self.evaluate(info.get('x', 0))
            y = self.evaluate(info.get('y', 0))
            z = self.evaluate(info.get('z', 0))
            pitch = self.evaluate(info.get('pitch', 0))
            yaw = self.evaluate(info.get('yaw', 0))
            roll = self.evaluate(info.get('roll', 0))
            self.start = (x, y, z)
            self.direction = (pitch, yaw, roll)

        for planet, info in six.iteritems(root['bodies']):
            self.callback('Loading objects (%d of %d)...' % (self._current_object, self._objects),
                          'Loading %s.' % planet, self._current_object / self._objects)
            self._body(planet, info)
            self._current_object += 1

        if 'belts' in root:
            belt_count = len(root['belts'])
            for i, (name, info) in enumerate(six.iteritems(root['belts']), 1):
                self.callback('Loading belts (%d of %d)...' % (i, belt_count),
                              'Loading %s.' % name, i / belt_count)
                self.tracker.append(Belt(name, self, info))

        if 'sky' in root:
            self.callback('Loading sky...', 'Loading sky.', 0)
            self.tracker.append(Sky(self, root['sky']))

    def _body(self, name, info, parent=None):
        if 'texture' in info:
            body = SphericalBody(name, self, info, parent)
        elif 'model' in info:
            body = ModelBody(name, self, info, parent)
        else:
            raise ValueError('Nothing to load for %s.' % name)

        if parent:
            parent.satellites.append(body)
        else:
            self.tracker.append(body)

        for satellite, info in six.iteritems(info.get('satellites', {})):
            self.callback('Loading objects (%d of %d)...' % (self._current_object, self._objects),
                          'Loading %s, satellite of %s.' % (satellite, name), self._current_object / self._objects)
            self._body(satellite, info, body)
            self._current_object += 1
