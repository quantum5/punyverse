from punyverse import framedata
from punyverse.orbit import KeplerOrbit

from pyglet.gl import *


class Entity(object):
    def __init__(self, id, location, rotation=(0, 0, 0), direction=(0, 0, 0), background=False):
        self.id = id
        self.location = location
        self.rotation = rotation
        self.direction = direction
        self.background = background

    def update(self):
        x, y, z = self.location
        dx, dy, dz = self.direction
        self.location = x + dx, y + dy, z + dz


class Asteroid(Entity):
    def __init__(self, *args, **kwargs):
        super(Asteroid, self).__init__(*args, **kwargs)

    def update(self):
        super(Asteroid, self).update()
        rx, ry, rz = self.rotation
        # Increment all axis to 'spin' 
        self.rotation = rx + 1, ry + 1, rz + 1


class Planet(Entity):
    def __init__(self, *args, **kwargs):
        self.delta = kwargs.pop('delta', 5)
        self.atmosphere = kwargs.pop('atmosphere', 0)
        self.cloudmap = kwargs.pop('cloudmap', 0)
        self.last_tick = 0
        self.mass = kwargs.pop('mass', None)
        super(Planet, self).__init__(*args, **kwargs)

    def update(self):
        super(Planet, self).update()

        if self.last_tick != framedata.tick:
            self.last_tick = framedata.tick
            pitch, yaw, roll = self.rotation
            roll += self.delta / 100.0
            self.rotation = pitch, yaw, roll


class Satellite(Planet):
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent')
        self.orbit_speed = kwargs.pop('orbit_speed', 1)

        # Semi-major axis and eccentricity defines orbit
        distance = kwargs.pop('distance', 100)
        eccentricity = kwargs.pop('eccentricity', 0)

        # Inclination, longitude of ascending node, and argument of periapsis defines orbital plane
        inclination = kwargs.pop('inclination', 0)
        longitude = kwargs.pop('longitude', 0)
        argument = kwargs.pop('argument', 0)

        # Orbit calculation
        self.orbit_id = None
        self.orbit_cache = None

        self.theta = 0
        # OpenGL's z-axis is reversed
        self.orbit = KeplerOrbit(distance, eccentricity, inclination, longitude, argument)
        super(Satellite, self).__init__(*args, **kwargs)

    def get_orbit(self):
        # Cache key is the three orbital plane parameters and eccentricity
        cache = (self.orbit.eccentricity, self.orbit.longitude, self.orbit.inclination, self.orbit.argument)
        if self.orbit_cache == cache:
            return self.orbit_id

        if self.orbit_id is not None:
            glDeleteLists(self.orbit_id, 1)

        id = glGenLists(1)
        glNewList(id, GL_COMPILE)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glPushAttrib(GL_LINE_BIT | GL_CURRENT_BIT)
        glColor3f(0, 1, 0)
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        for theta in xrange(360):
            x, z, y = self.orbit.orbit(theta)
            glVertex3f(x, y, z)
        glEnd()
        glPopAttrib()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEndList()

        self.orbit_id = id
        self.orbit_cache = cache
        return id

    def update(self):
        super(Planet, self).update()

        if self.last_tick != framedata.tick:
            self.last_tick = framedata.tick
            pitch, yaw, roll = self.rotation
            roll += self.delta / 100.0
            self.rotation = pitch, yaw, roll

            self.parent.update()
            px, py, pz = self.parent.location
            self.theta += self.orbit_speed
            x, z, y = self.orbit.orbit(self.theta)
            self.location = (x + px, y + py, z + pz)

