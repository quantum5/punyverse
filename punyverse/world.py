from __future__ import print_function

import os
from collections import OrderedDict

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise SystemExit('No JSON module found')

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
    def __init__(self, file, callback, options=None):
        self.tracker = []
        self.start = (0, 0, 0)
        self.direction = (0, 0, 0)
        self.x = None
        self.y = None
        self.z = None
        self.tick_length = 1
        self.tick = 0

        self.callback = callback
        self.options = options or {}
        self._phase = 'Parsing configuration...'
        self._parse(file)
        del self.callback # So it can't be used after loading finishes

    def evaluate(self, value):
        return eval(str(value), {'__builtins__': None}, self._context)

    @property
    def length(self):
        return self._length

    @property
    def au(self):
        return self._au

    def _parse(self, file):
        self.callback(self._phase, 'Loading configuration file...', 0)
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
        print(self._objects, 'objects to be loaded...')

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
            message = 'Loading %s.' % planet
            print(message)
            self.callback('Loading objects (%d of %d)...' % (self._current_object, self._objects),
                          message, float(self._current_object) / self._objects)
            self._body(planet, info)
            self._current_object += 1

        if 'belts' in root:
            self._phase = 'Loading belts...'
            self._current_object = 0
            for name, info in six.iteritems(root['belts']):
                message = 'Loading %s.' % name
                print(message)
                self.callback(self._phase, message, float(self._current_object) / len(root['belts']))
                self.tracker.append(Belt(name, self, info))

        if 'sky' in root:
            self._phase = 'Loading sky...'
            message = 'Loading sky.'
            print(message)
            self.callback(self._phase, message, 0)
            self.tracker.append(Sky(self, root['sky']))

    def _body(self, name, info, parent=None):
        if 'texture' in info:
            body = SphericalBody(name, self, info, parent)
        elif 'model' in info:
            body = ModelBody(name, self, info, parent)
        else:
            print('Nothing to load for %s.' % name)
            return

        if parent:
            parent.satellites.append(body)
        else:
            self.tracker.append(body)

        for satellite, info in six.iteritems(info.get('satellites', {})):
            message = 'Loading %s, satellite of %s.' % (satellite, name)
            print(message)
            self.callback('Loading objects (%d of %d)...' % (self._current_object, self._objects),
                          message, float(self._current_object) / self._objects)
            self._body(satellite, info, body)
            self._current_object += 1
