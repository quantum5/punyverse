from punyverse import framedata
from math import radians, sin, cos
from punyverse.orbit import KeplerOrbit


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
        self.distance = kwargs.pop('distance', 100)
        self.eccentricity = kwargs.pop('eccentricity', 0)

        # Inclination and longitude of ascending node defines orbital plane
        self.inclination = kwargs.pop('inclination', 0)

        self.theta = 0
        # OpenGL's z-axis is reversed
        self.orbit = KeplerOrbit(self.distance, self.eccentricity, -self.inclination)
        super(Satellite, self).__init__(*args, **kwargs)

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

