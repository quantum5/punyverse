from collections import OrderedDict
from functools import partial
import os.path

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print "No compatible JSON decoder found. Translation: you're fucked."

try:
    from _model import model_list, load_model
except ImportError:
    from model import model_list, load_model

from punyverse.glgeom import *
from punyverse.entity import *
from punyverse.texture import *

from math import pi, sqrt

G = 6.67384e-11  # Gravitation Constant


def get_best_texture(info, optional=False):
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
                texture = load_texture(item)
            except ValueError:
                pass
            else:
                break
    else:
        try:
            texture = load_texture(info)
        except ValueError:
            if optional:
                skip = True
            else:
                cheap = True
                texture = [1, 1, 1, 1]
    return cheap, skip, texture


def load_world(file):
    with open(os.path.join(os.path.dirname(__file__), file)) as f:
        root = json.load(f, object_pairs_hook=OrderedDict)

        world = World()
        e = lambda x: eval(str(x), {'__builtins__': None}, {'AU': root.get('au', 2000)})
        tick = root.get('tick', 4320)  # How many second is a tick?
        length = root.get('length', 4320)  # Satellite distance is in km, divide by this gets in world units

        if 'start' in root:
            info = root['start']
            x = e(info.get('x', 0))
            y = e(info.get('y', 0))
            z = e(info.get('z', 0))
            pitch = e(info.get('pitch', 0))
            yaw = e(info.get('yaw', 0))
            roll = e(info.get('roll', 0))
            world.start = (x, y, z)
            world.direction = (pitch, yaw, roll)

        def body(name, info, parent=None):
            lighting = info.get('lighting', True)
            x = e(info.get('x', 0))
            y = e(info.get('y', 0))
            z = e(info.get('z', 0))
            pitch = e(info.get('pitch', 0))
            yaw = e(info.get('yaw', 0))
            roll = e(info.get('roll', 0))
            delta = e(info.get('delta', 5))
            radius = e(info.get('radius', None))
            background = info.get('background', False)

            if 'texture' in info:
                cheap, skip, texture = get_best_texture(info['texture'], optional=info.get('optional', False))
                if skip:
                    return
                if cheap:
                    object_id = compile(colourball, radius, int(radius / 2), int(radius / 2), texture)
                else:
                    object_id = compile(sphere, radius, int(radius / 2), int(radius / 2), texture, lighting=lighting)
            elif 'model' in info:
                scale = info.get('scale', 1)
                object_id = model_list(load_model(info['model']), info.get('sx', scale), info.get('sy', scale),
                                       info.get('sz', scale), (0, 0, 0))
            else:
                print 'Nothing to load for %s.' % name

            params = {}
            if parent is None:
                type = Planet
            else:
                x, y, z = parent.location
                distance = info.get('distance', 100)  # Semi-major axis when actually displayed in virtual space
                sma = info.get('sma', distance)       # Semi-major axis used to calculate orbital speed
                if hasattr(parent, 'mass') and parent.mass is not None:
                    speed = 360 / (2 * pi * sqrt((sma * 1000) ** 3 / (G * parent.mass)) / tick)
                else:
                    speed = info.get('orbit_speed', 1)
                type = Satellite
                params.update(parent=parent, orbit_speed=speed,
                              distance=distance / length, eccentricity=info.get('eccentricity', 0),
                              inclination=info.get('inclination', 0), longitude=info.get('longitude', 0),
                              argument=info.get('argument', 0))

            if 'mass' in info:
                params['mass'] = info['mass']

            atmosphere_id = 0
            cloudmap_id = 0
            if 'atmosphere' in info:
                atmosphere_data = info['atmosphere']
                size = e(atmosphere_data.get('diffuse_size', None))
                atm_texture = atmosphere_data.get('diffuse_texture', None)
                cloud_texture = atmosphere_data.get('cloud_texture', None)
                cheap, _, cloud_texture = get_best_texture(cloud_texture)
                if not cheap:
                    cloudmap_id = compile(sphere, radius + 2, int(radius / 2), int(radius / 2), cloud_texture,
                                          lighting=False)
                cheap, _, atm_texture = get_best_texture(atm_texture)
                if not cheap:
                    atmosphere_id = compile(disk, radius, radius + size, 30, atm_texture)

            object = type(object_id, (x, y, z), (pitch, yaw, roll), delta=delta,
                          atmosphere=atmosphere_id, cloudmap=cloudmap_id, background=background, **params)
            world.tracker.append(object)

            if 'ring' in info:
                ring_data = info['ring']
                texture = ring_data.get('texture', None)
                distance = e(ring_data.get('distance', radius * 1.2))
                size = e(ring_data.get('size', radius / 2))
                pitch = e(ring_data.get('pitch', pitch))
                yaw = e(ring_data.get('yaw', yaw))
                roll = e(ring_data.get('roll', roll))

                cheap, _, texture = get_best_texture(texture)
                if not cheap:
                    world.tracker.append(
                        type(compile(disk, distance, distance + size, 30, texture), (x, y, z),
                             (pitch, yaw, roll)))

            for satellite, info in info.get('satellites', {}).iteritems():
                print "Loading %s, satellite of %s." % (satellite, name)
                body(satellite, info, object)

        for planet, info in root['planets'].iteritems():
            print "Loading %s." % planet
            body(planet, info)

        return world


class World(object):
    def __init__(self):
        self.tracker = []
        self.start = (0, 0, 0)
        self.direction = (0, 0, 0)
        self.x = None
        self.y = None
        self.z = None
