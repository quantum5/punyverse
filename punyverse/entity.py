import random
from math import sqrt, pi

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

from punyverse.glgeom import compile, sphere, flare, disk, glMatrix, glRestore, belt
from punyverse.orbit import KeplerOrbit
from punyverse.texture import get_best_texture, load_clouds

try:
    from punyverse._model import model_list, load_model
except ImportError:
    from punyverse.model import model_list, load_model

G = 6.67384e-11  # Gravitation Constant


class Entity(object):
    background = False

    def __init__(self, name, location, rotation=(0, 0, 0), direction=(0, 0, 0)):
        self.name = name
        self.location = location
        self.rotation = rotation
        self.direction = direction

    def update(self):
        x, y, z = self.location
        dx, dy, dz = self.direction
        self.location = x + dx, y + dy, z + dz

    def collides(self, x, y, z):
        return False

    def draw(self, options):
        raise NotImplementedError()


class Asteroid(Entity):
    def __init__(self, asteroid_id, location, direction):
        super(Asteroid, self).__init__('Asteroid', location, direction=direction)
        self.asteroid_id = asteroid_id

    def update(self):
        super(Asteroid, self).update()

        rx, ry, rz = self.rotation
        # Increment all axis to 'spin' 
        self.rotation = rx + 1, ry + 1, rz + 1

    def draw(self, options):
        with glMatrix(self.location, self.rotation), glRestore(GL_CURRENT_BIT):
            glCallList(self.asteroid_id)


class AsteroidManager(object):
    def __init__(self):
        self.asteroids = []

    def __bool__(self):
        return bool(self.asteroids)
    __nonzero__ = __bool__

    def load(self, file):
        self.asteroids.append(model_list(load_model(file), 5, 5, 5, (0, 0, 0)))

    def new(self, location, direction):
        return Asteroid(random.choice(self.asteroids), location, direction)


class Belt(Entity):
    def __init__(self, name, world, info):
        self.world = world

        x = world.evaluate(info.get('x', 0))
        y = world.evaluate(info.get('y', 0))
        z = world.evaluate(info.get('z', 0))
        radius = world.evaluate(info.get('radius', 0))
        cross = world.evaluate(info.get('cross', 0))
        count = int(world.evaluate(info.get('count', 0)))
        scale = info.get('scale', 1)
        longitude = info.get('longitude', 0)
        inclination = info.get('inclination', 0)
        argument = info.get('argument', 0)
        rotation = info.get('period', 31536000)
        models = info['model']
        if not isinstance(models, list):
            models = [models]

        objects = [model_list(load_model(model), info.get('sx', scale), info.get('sy', scale),
                              info.get('sz', scale), (0, 0, 0)) for model in models]

        self.belt_id = compile(belt, radius, cross, objects, count)
        self.rotation_angle = 360.0 / rotation if rotation else 0

        super(Belt, self).__init__(name, (x, y, z), (inclination, longitude, argument))

    def update(self):
        super(Belt, self).update()
        pitch, yaw, roll = self.rotation
        self.rotation = pitch, self.world.tick * self.rotation_angle % 360, roll

    def draw(self, options):
        with glMatrix(self.location, self.rotation), glRestore(GL_CURRENT_BIT):
            glCallList(self.belt_id)


class Sky(Entity):
    background = True

    def __init__(self, world, info):
        pitch = world.evaluate(info.get('pitch', 0))
        yaw = world.evaluate(info.get('yaw', 0))
        roll = world.evaluate(info.get('roll', 0))

        super(Sky, self).__init__('Sky', (0, 0, 0), (pitch, yaw, roll))
        self.world = world

        texture = get_best_texture(info['texture'])
        division = info.get('division', 30)
        self.sky_id = compile(sphere, info.get('radius', 1000000), division, division, texture,
                              inside=True, lighting=False)

    def draw(self, options):
        cam = self.world.cam
        with glMatrix((-cam.x, -cam.y, -cam.z), self.rotation), glRestore(GL_CURRENT_BIT):
            glCallList(self.sky_id)


class Body(Entity):
    def __init__(self, name, world, info, parent=None):
        self.world = world
        self.parent = parent
        self.satellites = []

        x = world.evaluate(info.get('x', 0))
        y = world.evaluate(info.get('y', 0))
        z = world.evaluate(info.get('z', 0))
        pitch = world.evaluate(info.get('pitch', 0))
        yaw = world.evaluate(info.get('yaw', 0))
        roll = world.evaluate(info.get('roll', 0))
        rotation = world.evaluate(info.get('rotation', 86400))

        self.mass = info.get('mass')

        orbit_distance = float(world.evaluate(info.get('orbit_distance', world.au)))
        self.orbit_show = orbit_distance * 1.25
        self.orbit_blend = orbit_distance / 4
        self.orbit_opaque = orbit_distance

        super(Body, self).__init__(name, (x, y, z), (pitch, yaw, roll))
        self.initial_roll = roll

        self.orbit = None
        self.orbit_speed = None

        if parent:
            # Semi-major axis when actually displayed in virtual space
            distance = world.evaluate(info.get('distance', 100))
            # Semi-major axis used to calculate orbital speed
            sma = world.evaluate(info.get('sma', distance))

            if hasattr(parent, 'mass') and parent.mass is not None:
                period = 2 * pi * sqrt((sma * 1000) ** 3 / (G * parent.mass))
                self.orbit_speed = 360.0 / period
                if not rotation:  # Rotation = 0 assumes tidal lock
                    rotation = period
            else:
                self.orbit_speed = info.get('orbit_speed', 1)

            self.orbit = KeplerOrbit(distance / world.length, info.get('eccentricity', 0), info.get('inclination', 0),
                                     info.get('longitude', 0), info.get('argument', 0))

        self.rotation_angle = 360.0 / rotation if rotation else 0

        # Orbit calculation
        self.orbit_id = None
        self.orbit_cache = None

    def update(self):
        super(Body, self).update()

        pitch, yaw, roll = self.rotation
        roll = (self.initial_roll + self.world.tick * self.rotation_angle) % 360
        self.rotation = pitch, yaw, roll

        if self.orbit:
            px, py, pz = self.parent.location
            x, z, y = self.orbit.orbit(self.world.tick * self.orbit_speed % 360)
            self.location = (x + px, y + py, z + pz)

        for satellite in self.satellites:
            satellite.update()

    def get_orbit(self):
        if not self.orbit:
            return

        # Cache key is the three orbital plane parameters and eccentricity
        cache = (self.orbit.eccentricity, self.orbit.longitude, self.orbit.inclination, self.orbit.argument)
        if self.orbit_cache == cache:
            return self.orbit_id

        if self.orbit_id is not None:
            glDeleteLists(self.orbit_id, 1)

        id = glGenLists(1)
        glNewList(id, GL_COMPILE)
        glBegin(GL_LINE_LOOP)
        for theta in range(360):
            x, z, y = self.orbit.orbit(theta)
            glVertex3f(x, y, z)
        glEnd()
        glEndList()

        self.orbit_id = id
        self.orbit_cache = cache
        return id

    def _draw_orbits(self, distance):
        with glMatrix(self.parent.location), glRestore(GL_ENABLE_BIT | GL_LINE_BIT | GL_CURRENT_BIT):
            glDisable(GL_LIGHTING)
            solid = distance < self.parent.orbit_opaque
            glColor4f(1, 1, 1, 1 if solid else (1 - (distance - self.parent.orbit_opaque) / self.parent.orbit_blend))
            if not solid:
                glEnable(GL_BLEND)
            glLineWidth(1)
            glCallList(self.get_orbit())

    def draw(self, options):
        self._draw(options)

        if options.orbit and self.orbit:
            dist = self.world.cam.distance(*self.parent.location)
            if dist < self.parent.orbit_show:
                self._draw_orbits(dist)

        for satellite in self.satellites:
            satellite.draw(options)

    def _draw(self, options):
        raise NotImplementedError()

    def collides(self, x, y, z):
        return self._collides(x, y, z) or any(satellite.collides(x, y, z) for satellite in self.satellites)

    def _collides(self, x, y, z):
        return False


class SphericalBody(Body):
    def __init__(self, name, world, info, parent=None):
        super(SphericalBody, self).__init__(name, world, info, parent)

        self.radius = world.evaluate(info.get('radius', world.length)) / world.length
        division = info.get('division', max(min(int(self.radius / 8), 60), 10))
        self.light_source = info.get('light_source', False)

        texture = get_best_texture(info['texture'])
        self.sphere_id = compile(sphere, self.radius, division, division, texture)

        self.atmosphere_id = 0
        self.cloudmap_id = 0
        self.corona_id = 0
        self.ring_id = 0

        if 'atmosphere' in info:
            atmosphere_data = info['atmosphere']
            atm_size = world.evaluate(atmosphere_data.get('diffuse_size', None))
            atm_texture = atmosphere_data.get('diffuse_texture', None)
            cloud_texture = atmosphere_data.get('cloud_texture', None)
            corona_texture = atmosphere_data.get('corona_texture', None)
            if cloud_texture is not None:
                cloud_texture = get_best_texture(cloud_texture, loader=load_clouds)
                self.cloudmap_id = compile(sphere, self.radius + 2, division, division, cloud_texture, lighting=False)

            if corona_texture is not None:
                corona = get_best_texture(corona_texture)
                corona_size = atmosphere_data.get('corona_size', self.radius / 2)
                corona_division = atmosphere_data.get('corona_division', 100)
                corona_ratio = atmosphere_data.get('corona_ratio', 0.5)
                self.corona_id = compile(flare, self.radius, self.radius + corona_size, corona_division,
                                         corona_ratio, corona)

            if atm_texture is not None:
                atm_texture = get_best_texture(atm_texture)
                self.atmosphere_id = compile(disk, self.radius, self.radius + atm_size, 30, atm_texture)

        if 'ring' in info:
            distance = world.evaluate(info['ring'].get('distance', self.radius * 1.2))
            size = world.evaluate(info['ring'].get('size', self.radius / 2))

            pitch, yaw, roll = self.rotation
            pitch = world.evaluate(info['ring'].get('pitch', pitch))
            yaw = world.evaluate(info['ring'].get('yaw', yaw))
            roll = world.evaluate(info['ring'].get('roll', roll))
            self.ring_rotation = pitch, yaw, roll

            self.ring_id = compile(disk, distance, distance + size, 30,
                                   get_best_texture(info['ring'].get('texture', None)))

    def _draw_sphere(self):
        with glMatrix(self.location, self.rotation), glRestore(GL_CURRENT_BIT | GL_ENABLE_BIT):
            if self.light_source:
                glDisable(GL_LIGHTING)
            glCallList(self.sphere_id)

    def _draw_atmosphere(self, glMatrixBuffer=GLfloat * 16):
        with glMatrix(self.location), glRestore(GL_ENABLE_BIT | GL_CURRENT_BIT):
            matrix = glMatrixBuffer()
            glGetFloatv(GL_MODELVIEW_MATRIX, matrix)
            matrix[0: 3] = [1, 0, 0]
            matrix[4: 7] = [0, 1, 0]
            matrix[8:11] = [0, 0, 1]
            glLoadMatrixf(matrix)

            if self.atmosphere_id:
                glCallList(self.atmosphere_id)

            if self.corona_id:
                x, y, z = self.world.cam.direction()
                glTranslatef(-x, -y, -z)
                glEnable(GL_BLEND)
                glCallList(self.corona_id)

    def _draw_clouds(self):
        with glMatrix(self.location, self.rotation), glRestore(GL_ENABLE_BIT | GL_CURRENT_BIT):
            glEnable(GL_BLEND)
            glEnable(GL_ALPHA_TEST)
            glCallList(self.cloudmap_id)

    def _draw_rings(self):
        with glMatrix(self.location, self.ring_rotation), glRestore(GL_CURRENT_BIT):
            glCallList(self.ring_id)

    def _draw(self, options):
        self._draw_sphere()

        if options.atmosphere and (self.atmosphere_id or self.corona_id):
            self._draw_atmosphere()

        if options.cloud and self.cloudmap_id:
            self._draw_clouds()

        if self.ring_id:
            self._draw_rings()

    def _collides(self, x, y, z):
        ox, oy, oz = self.location
        dx, dy, dz = x - ox, y - oy, z - oz
        distance = sqrt(dx * dx + dy * dy + dz * dz)
        return distance <= self.radius


class ModelBody(Body):
    def __init__(self, name, world, info, parent=None):
        super(ModelBody, self).__init__(name, world, info, parent)

        scale = info.get('scale', 1)
        self.object_id = model_list(load_model(info['model']), info.get('sx', scale), info.get('sy', scale),
                               info.get('sz', scale), (0, 0, 0))

    def _draw(self, options):
        with glMatrix(self.location, self.rotation), glRestore(GL_CURRENT_BIT):
            glCallList(self.object_id)
