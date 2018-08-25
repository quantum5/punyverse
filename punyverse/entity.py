import random
from math import sqrt, pi

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

from punyverse.glgeom import compile, glRestore, belt, Sphere, Disk, OrbitVBO, Matrix4f
from punyverse.model import load_model, WavefrontVBO
from punyverse.orbit import KeplerOrbit
from punyverse.texture import get_best_texture, load_clouds
from punyverse.utils import cached_property

G = 6.67384e-11  # Gravitation Constant


class Entity(object):
    background = False

    def __init__(self, world, name, location, rotation=(0, 0, 0), direction=(0, 0, 0)):
        self.world = world
        self.name = name
        self.location = location
        self.rotation = rotation
        self.direction = direction

    @cached_property
    def mv_matrix(self):
        return self.world.view_matrix() * Matrix4f.from_angles(self.location, self.rotation)

    def update(self):
        self.mv_matrix = None
        x, y, z = self.location
        dx, dy, dz = self.direction
        self.location = x + dx, y + dy, z + dz

    def collides(self, x, y, z):
        return False

    def draw(self, options):
        raise NotImplementedError()


class Asteroid(Entity):
    def __init__(self, world, model, location, direction):
        super(Asteroid, self).__init__(world, 'Asteroid', location, direction=direction)
        self.model = model

    def update(self):
        super(Asteroid, self).update()
        rx, ry, rz = self.rotation
        # Increment all axis to 'spin' 
        self.rotation = rx + 1, ry + 1, rz + 1

    def draw(self, options):
        glLoadMatrixf(self.mv_matrix.as_gl())
        self.model.draw()


class AsteroidManager(object):
    def __init__(self, world):
        self.world = world
        self.asteroids = []

    def __bool__(self):
        return bool(self.asteroids)
    __nonzero__ = __bool__

    def load(self, file):
        self.asteroids.append(WavefrontVBO(load_model(file), 5, 5, 5))

    def new(self, location, direction):
        return Asteroid(self.world, random.choice(self.asteroids), location, direction)


class Belt(Entity):
    def __init__(self, name, world, info):
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

        objects = [WavefrontVBO(load_model(model), info.get('sx', scale), info.get('sy', scale),
                                info.get('sz', scale)) for model in models]

        self.belt_id = compile(belt, radius, cross, objects, count)
        self.rotation_angle = 360.0 / rotation if rotation else 0

        super(Belt, self).__init__(world, name, (x, y, z), (inclination, longitude, argument))

    def update(self):
        super(Belt, self).update()
        pitch, yaw, roll = self.rotation
        self.rotation = pitch, self.world.tick * self.rotation_angle % 360, roll

    def draw(self, options):
        glLoadMatrixf(self.mv_matrix.as_gl())
        glCallList(self.belt_id)


class Sky(Entity):
    background = True

    def __init__(self, world, info):
        pitch = world.evaluate(info.get('pitch', 0))
        yaw = world.evaluate(info.get('yaw', 0))
        roll = world.evaluate(info.get('roll', 0))

        super(Sky, self).__init__(world, 'Sky', (0, 0, 0), (pitch, yaw, roll))

        self.texture = get_best_texture(info['texture'])
        division = info.get('division', 30)
        self.sphere = Sphere(info.get('radius', 1000000), division, division)

    def draw(self, options):
        cam = self.world.cam
        with glRestore(GL_TEXTURE_BIT | GL_ENABLE_BIT):
            matrix = self.world.view_matrix() * Matrix4f.from_angles((-cam.x, -cam.y, -cam.z), self.rotation)
            glLoadMatrixf(matrix.as_gl())
            glEnable(GL_CULL_FACE)
            glEnable(GL_TEXTURE_2D)
            glDisable(GL_LIGHTING)

            glCullFace(GL_FRONT)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.sphere.draw()


class Body(Entity):
    def __init__(self, name, world, info, parent=None):
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

        super(Body, self).__init__(world, name, (x, y, z), (pitch, yaw, roll))
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
        self.orbit_vbo = None
        self.orbit_cache = None

    @cached_property
    def orbit_matrix(self):
        return self.world.view_matrix() * Matrix4f.from_angles(self.location)

    def update(self):
        super(Body, self).update()

        if self.rotation_angle:
            pitch, yaw, roll = self.rotation
            roll = (self.initial_roll + self.world.tick * self.rotation_angle) % 360
            self.rotation = pitch, yaw, roll

        if self.orbit:
            px, py, pz = self.parent.location
            x, z, y = self.orbit.orbit(self.world.tick * self.orbit_speed % 360)
            self.location = (x + px, y + py, z + pz)
            self.orbit_matrix = None

        for satellite in self.satellites:
            satellite.update()

    def get_orbit(self):
        if not self.orbit:
            return

        # Cache key is the three orbital plane parameters and eccentricity
        cache = (self.orbit.eccentricity, self.orbit.longitude, self.orbit.inclination, self.orbit.argument)
        if self.orbit_cache == cache:
            return self.orbit_vbo

        if self.orbit_vbo is not None:
            self.orbit_vbo.close()

        self.orbit_vbo = OrbitVBO(self.orbit)
        self.orbit_cache = cache
        return self.orbit_vbo

    def _draw_orbits(self, distance):
        with glRestore(GL_ENABLE_BIT | GL_LINE_BIT | GL_CURRENT_BIT):
            glLoadMatrixf(self.parent.orbit_matrix.as_gl())

            glDisable(GL_LIGHTING)
            solid = distance < self.parent.orbit_opaque
            glColor4f(1, 1, 1, 1 if solid else (1 - (distance - self.parent.orbit_opaque) / self.parent.orbit_blend))
            if not solid:
                glEnable(GL_BLEND)
            glLineWidth(1)
            self.get_orbit().draw()

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

        self.texture = get_best_texture(info['texture'])
        self.sphere = Sphere(self.radius, division, division)

        self.atmosphere = None
        self.clouds = None
        self.ring = 0

        if 'atmosphere' in info:
            atmosphere_data = info['atmosphere']
            atm_size = world.evaluate(atmosphere_data.get('diffuse_size', None))
            atm_texture = atmosphere_data.get('diffuse_texture', None)
            cloud_texture = atmosphere_data.get('cloud_texture', None)
            if cloud_texture is not None:
                self.cloud_texture = get_best_texture(cloud_texture, loader=load_clouds)
                self.clouds = Sphere(self.radius + 2, division, division)

            if atm_texture is not None:
                self.atm_texture = get_best_texture(atm_texture, clamp=True)
                self.atmosphere = Disk(self.radius, self.radius + atm_size, 30)

        if 'ring' in info:
            distance = world.evaluate(info['ring'].get('distance', self.radius * 1.2))
            size = world.evaluate(info['ring'].get('size', self.radius / 2))

            pitch, yaw, roll = self.rotation
            pitch = world.evaluate(info['ring'].get('pitch', pitch))
            yaw = world.evaluate(info['ring'].get('yaw', yaw))
            roll = world.evaluate(info['ring'].get('roll', roll))
            self.ring_rotation = pitch, yaw, roll

            self.ring_texture = get_best_texture(info['ring'].get('texture', None), clamp=True)
            self.ring = Disk(distance, distance + size, 30)

    def _draw_sphere(self, fv4=GLfloat * 4):
        with glRestore(GL_LIGHTING_BIT | GL_ENABLE_BIT | GL_TEXTURE_BIT):
            glLoadMatrixf(self.mv_matrix.as_gl())
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)

            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)

            if self.light_source:
                glDisable(GL_LIGHTING)
            else:
                glDisable(GL_BLEND)
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, fv4(1, 1, 1, 0))
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(1, 1, 1, 0))
                glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 125)

            self.sphere.draw()

    def _draw_atmosphere(self):
        with glRestore(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_TEXTURE_BIT):
            mv = self.mv_matrix.matrix
            matrix = Matrix4f([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, mv[12], mv[13], mv[14], 1])
            glLoadMatrixf(matrix.as_gl())

            glDisable(GL_LIGHTING)
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glDisable(GL_CULL_FACE)

            glBindTexture(GL_TEXTURE_2D, self.atm_texture)
            self.atmosphere.draw()

    def _draw_clouds(self):
        with glRestore(GL_ENABLE_BIT | GL_TEXTURE_BIT):
            glLoadMatrixf(self.mv_matrix.as_gl())
            glEnable(GL_BLEND)
            glEnable(GL_ALPHA_TEST)
            glEnable(GL_CULL_FACE)
            glDisable(GL_LIGHTING)
            glEnable(GL_TEXTURE_2D)

            glCullFace(GL_BACK)
            glBindTexture(GL_TEXTURE_2D, self.cloud_texture)
            self.clouds.draw()

    def _draw_rings(self):
        with glRestore(GL_ENABLE_BIT | GL_TEXTURE_BIT):
            glLoadMatrixf(self.mv_matrix.as_gl())
            glDisable(GL_LIGHTING)
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glDisable(GL_CULL_FACE)

            glBindTexture(GL_TEXTURE_2D, self.ring_texture)
            self.ring.draw()

    def _draw(self, options):
        self._draw_sphere()

        if options.atmosphere and self.atmosphere:
            self._draw_atmosphere()

        if options.cloud and self.clouds:
            self._draw_clouds()

        if self.ring:
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
        self.vbo = WavefrontVBO(load_model(info['model']), info.get('sx', scale), info.get('sy', scale),
                                info.get('sz', scale))

    def _draw(self, options):
        glLoadMatrixf(self.mv_matrix.as_gl())
        self.vbo.draw()
