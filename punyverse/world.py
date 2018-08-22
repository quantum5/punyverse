from __future__ import print_function

from collections import OrderedDict
import os

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

from punyverse.glgeom import *
from punyverse.entity import *
from punyverse.texture import *
from punyverse import texture

from math import pi, sqrt

G = 6.67384e-11  # Gravitation Constant


def get_best_texture(info, optional=False, loader=load_texture):
    cheap = False
    skip = False
    texture = None
    if isinstance(info, list):
        for item in info:
            if isinstance(item, list):
                if len(item) == 4:
                    cheap = True
                    texture = item
                    break
                continue
            try:
                texture = loader(item)
            except ValueError:
                pass
            else:
                break
        else:
            cheap = True
            texture = [1, 1, 1, 1]
    else:
        try:
            texture = loader(info)
        except ValueError:
            if optional:
                skip = True
            else:
                cheap = True
                texture = [1, 1, 1, 1]
    return cheap, skip, texture


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

    def _eval(self, value):
        return eval(str(value), {'__builtins__': None}, self._context)

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
            x = self._eval(info.get('x', 0))
            y = self._eval(info.get('y', 0))
            z = self._eval(info.get('z', 0))
            pitch = self._eval(info.get('pitch', 0))
            yaw = self._eval(info.get('yaw', 0))
            roll = self._eval(info.get('roll', 0))
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
                self._belt(name, info)

    def _belt(self, name, info):
        x = self._eval(info.get('x', 0))
        y = self._eval(info.get('y', 0))
        z = self._eval(info.get('z', 0))
        radius = self._eval(info.get('radius', 0))
        cross = self._eval(info.get('cross', 0))
        count = int(self._eval(info.get('count', 0)))
        scale = info.get('scale', 1)
        longitude = info.get('longitude', 0)
        inclination = info.get('inclination', 0)
        argument = info.get('argument', 0)
        rotation = info.get('period', 31536000)
        theta = 360 / (rotation + .0) if rotation else 0

        models = info['model']
        if not isinstance(models, list):
            models = [models]
        objects = []
        for model in models:
            objects.append(model_list(load_model(model), info.get('sx', scale), info.get('sy', scale),
                                      info.get('sz', scale), (0, 0, 0)))

        self.tracker.append(Belt(compile(belt, radius, cross, objects, count),
                                 (x, y, z), (inclination, longitude, argument),
                                 rotation_angle=theta, world=self))

    def _body(self, name, info, parent=None):
        lighting = info.get('lighting', True)
        x = self._eval(info.get('x', 0))
        y = self._eval(info.get('y', 0))
        z = self._eval(info.get('z', 0))
        pitch = self._eval(info.get('pitch', 0))
        yaw = self._eval(info.get('yaw', 0))
        roll = self._eval(info.get('roll', 0))
        rotation = self._eval(info.get('rotation', 86400))
        radius = self._eval(info.get('radius', self._length)) / self._length
        background = info.get('background', False)
        orbit_distance = self._eval(info.get('orbit_distance', self._au))
        division = info.get('division', max(min(int(radius / 8), 60), 10))

        if 'texture' in info:
            cheap, skip, texture = get_best_texture(info['texture'], optional=info.get('optional', False))
            if skip:
                return
            if cheap:
                object_id = compile(colourball, radius, division, division, texture)
            else:
                if self.options.get('normal', False) and 'normal' in info:
                    object_id = compile(normal_sphere, radius, division, texture,
                                        info['normal'], lighting=lighting, inside=background)
                else:
                    object_id = compile(sphere, radius, division, division, texture,
                                        lighting=lighting, inside=background)
        elif 'model' in info:
            scale = info.get('scale', 1)
            object_id = model_list(load_model(info['model']), info.get('sx', scale), info.get('sy', scale),
                                   info.get('sz', scale), (0, 0, 0))
        else:
            print('Nothing to load for %s.' % name)
            return

        params = {'world': self, 'orbit_distance': orbit_distance, 'radius': None if background else radius}
        if parent is None:
            type = Body
        else:
            x, y, z = parent.location
            distance = self._eval(info.get('distance', 100))  # Semi-major axis when actually displayed in virtual space
            sma = self._eval(info.get('sma', distance))       # Semi-major axis used to calculate orbital speed
            if hasattr(parent, 'mass') and parent.mass is not None:
                period = 2 * pi * sqrt((sma * 1000) ** 3 / (G * parent.mass))
                speed = 360 / (period + .0)
                if not rotation:  # Rotation = 0 assumes tidal lock
                    rotation = period
            else:
                speed = info.get('orbit_speed', 1)
            type = Satellite
            params.update(parent=parent, orbit_speed=speed,
                          distance=distance / self._length, eccentricity=info.get('eccentricity', 0),
                          inclination=info.get('inclination', 0), longitude=info.get('longitude', 0),
                          argument=info.get('argument', 0))

        if 'mass' in info:
            params['mass'] = info['mass']

        atmosphere_id = 0
        cloudmap_id = 0
        corona_id = 0
        if 'atmosphere' in info:
            atmosphere_data = info['atmosphere']
            atm_size = self._eval(atmosphere_data.get('diffuse_size', None))
            atm_texture = atmosphere_data.get('diffuse_texture', None)
            cloud_texture = atmosphere_data.get('cloud_texture', None)
            corona_texture = atmosphere_data.get('corona_texture', None)
            if cloud_texture is not None:
                cheap, _, cloud_texture = get_best_texture(cloud_texture, loader=load_clouds)
                if not cheap:
                    cloudmap_id = compile(sphere, radius + 2, division, division, cloud_texture,
                                          lighting=False)
            if corona_texture is not None:
                cheap, _, corona = get_best_texture(corona_texture)
                if not cheap:
                    corona_size = atmosphere_data.get('corona_size', radius / 2)
                    corona_division = atmosphere_data.get('corona_division', 100)
                    corona_ratio = atmosphere_data.get('corona_ratio', 0.5)
                    corona_id = compile(flare, radius, radius + corona_size, corona_division,
                                        corona_ratio, corona)

            if atm_texture is not None:
                cheap, _, atm_texture = get_best_texture(atm_texture)
                if not cheap:
                    atmosphere_id = compile(disk, radius, radius + atm_size, 30, atm_texture)

        theta = 360.0 / rotation if rotation else 0
        object = type(object_id, (x, y, z), (pitch, yaw, roll), rotation_angle=theta,
                      atmosphere=atmosphere_id, cloudmap=cloudmap_id, background=background,
                      corona=corona_id, **params)
        self.tracker.append(object)

        if 'ring' in info:
            ring_data = info['ring']
            texture = ring_data.get('texture', None)
            distance = self._eval(ring_data.get('distance', radius * 1.2))
            size = self._eval(ring_data.get('size', radius / 2))
            pitch = self._eval(ring_data.get('pitch', pitch))
            yaw = self._eval(ring_data.get('yaw', yaw))
            roll = self._eval(ring_data.get('roll', roll))

            cheap, _, texture = get_best_texture(texture)
            if not cheap:
                self.tracker.append(
                    type(compile(disk, distance, distance + size, 30, texture), (x, y, z),
                         (pitch, yaw, roll), **params))

        for satellite, info in six.iteritems(info.get('satellites', {})):
            message = 'Loading %s, satellite of %s.' % (satellite, name)
            print(message)
            self.callback('Loading objects (%d of %d)...' % (self._current_object, self._objects),
                          message, float(self._current_object) / self._objects)
            self._body(satellite, info, object)
            self._current_object += 1
