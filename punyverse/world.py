from __future__ import division

import json
import os
from collections import OrderedDict

import six

from punyverse import texture
from punyverse.camera import Camera
from punyverse.entity import *
from punyverse.shader import Program


def load_world(file, callback=lambda message, completion: None):
    return World(file, callback)


class World(object):
    PROGRAMS = {
        'sky': ('sky.vertex.glsl', 'sky.fragment.glsl'),
        'planet': ('planet.vertex.glsl', 'planet.fragment.glsl'),
        'clouds': ('clouds.vertex.glsl', 'clouds.fragment.glsl'),
        'star': ('star.vertex.glsl', 'star.fragment.glsl'),
        'ring': ('ring.vertex.glsl', 'ring.fragment.glsl'),
        'atmosphere': ('atmosphere.vertex.glsl', 'atmosphere.fragment.glsl'),
        'text': ('text.vertex.glsl', 'text.fragment.glsl'),
        'line': ('line.vertex.glsl', 'line.fragment.glsl'),
        'model': ('model.vertex.glsl', 'model.fragment.glsl'),
        'belt': ('belt.vertex.glsl', 'model.fragment.glsl'),
    }

    def __init__(self, file, callback):
        self.tracker = []
        self.x = None
        self.y = None
        self.z = None
        self.tick_length = 0
        self.tick = 0
        self.asteroids = AsteroidManager(self)
        self.cam = Camera()

        self._program = None
        self.callback = callback
        self.programs = self._load_programs()
        self._parse(file)

        del self.callback  # So it can't be used after loading finishes

        self._time_accumulate = 0
        self._projection_matrix = self.cam.projection_matrix()

        for entity in self.tracker:
            entity.update()

        for name in ('planet', 'model', 'belt'):
            shader = self.activate_shader(name)
            shader.uniform_vec3('u_sun.ambient', 0.1, 0.1, 0.1)
            shader.uniform_vec3('u_sun.diffuse', 1, 1, 1)
            shader.uniform_vec3('u_sun.specular', 0.5, 0.5, 0.5)
            shader.uniform_vec3('u_sun.position', 0, 0, 0)
            shader.uniform_float('u_sun.intensity', 1)

        shader = self.activate_shader('clouds')
        shader.uniform_vec3('u_sun', 0, 0, 0)
        self.activate_shader(None)

    def _load_programs(self):
        programs = {}
        count = len(self.PROGRAMS)
        for i, (name, (vertex, fragment)) in enumerate(six.iteritems(self.PROGRAMS)):
            self.callback('Loading shaders (%d of %d)...' % (i, count),
                          'Loading shader "%s" (%s, %s).' % (name, vertex, fragment), i / count)
            programs[name] = Program(vertex, fragment)
        return programs

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
        self._context = {'AU': self._au, 'TEXTURE': texture.max_texture_size(), 'KM': 1.0 / self._length}

        self.tick_length = root.get('tick', 4320)  # How many second is a tick?

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
            self.cam.x = self.evaluate(info.get('x', 0))
            self.cam.y = self.evaluate(info.get('y', 0))
            self.cam.z = self.evaluate(info.get('z', 0))
            self.cam.pitch = self.evaluate(info.get('pitch', 0))
            self.cam.yaw = self.evaluate(info.get('yaw', 0))
            self.cam.roll = self.evaluate(info.get('roll', 0))

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
            def callback(index, file):
                self.callback('Loading sky...', 'Loading %s.' % file, index / 6)
            self.tracker.append(Sky(self, root['sky'], callback))

        if 'asteroids' in root:
            asteroids = root['asteroids']
            for i, file in enumerate(asteroids):
                self.callback('Loading asteroids...', 'Loading %s...' % file, i / len(asteroids))
                self.asteroids.load(file)

        self.font_tex = load_alpha_mask(root['font'], clamp=True)

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

    def spawn_asteroid(self):
        if self.asteroids:
            c = self.cam
            dx, dy, dz = c.direction()
            speed = abs(self.cam.speed) * 1.1 + 5
            self.tracker.append(self.asteroids.new((c.x, c.y - 3, c.z + 5), (dx * speed, dy * speed, dz * speed)))

    def update(self, dt, move, tick):
        c = self.cam
        c.update(dt, move)
        self.vp_matrix = None

        if tick:
            delta = self.tick_length * dt
            update = int(delta + self._time_accumulate + 0.5)
            if update:
                self._time_accumulate = 0
                self.tick += update

                for entity in self.tracker:
                    entity.update()
                    collision = entity.collides(c.x, c.y, c.z)
                    if collision:
                        c.speed *= -1
                        c.move(c.speed * 12 * dt)
            else:
                self._time_accumulate += delta

    def view_matrix(self):
        return self.cam.view_matrix

    def projection_matrix(self):
        return self._projection_matrix

    @cached_property
    def vp_matrix(self):
        return self._projection_matrix * self.cam.view_matrix

    def resize(self, width, height):
        self.cam.aspect = width / max(height, 1)
        self._projection_matrix = self.cam.projection_matrix()
        self.vp_matrix = None

    def activate_shader(self, name):
        program = None
        if self._program != name:
            if name is None:
                glUseProgram(0)
            else:
                program = self.programs[name]
                glUseProgram(program.program)
            self._program = name
        elif self._program is not None:
            program = self.programs[self._program]
        return program
