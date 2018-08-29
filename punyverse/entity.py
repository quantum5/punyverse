import random
from math import sqrt, pi

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

from punyverse.glgeom import *
from punyverse.model import load_model, WavefrontVBO
from punyverse.orbit import KeplerOrbit
from punyverse.texture import get_best_texture, load_alpha_mask, get_cube_map, load_texture_1d
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
    def model_matrix(self):
        return Matrix4f.from_angles(self.location, self.rotation)

    @cached_property
    def mv_matrix(self):
        return self.world.view_matrix() * self.model_matrix

    @cached_property
    def mvp_matrix(self):
        return self.world.vp_matrix * self.model_matrix

    def update(self):
        self.model_matrix = None
        self.mv_matrix = None
        self.mvp_matrix = None
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
        shader = self.world.activate_shader('model')
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)
        shader.uniform_mat4('u_mvMatrix', self.mv_matrix)
        shader.uniform_mat4('u_modelMatrix', self.model_matrix)
        self.model.draw(shader)


class AsteroidManager(object):
    def __init__(self, world):
        self.world = world
        self.asteroids = []

    def __bool__(self):
        return bool(self.asteroids)
    __nonzero__ = __bool__

    def load(self, file):
        shader = self.world.activate_shader('model')
        self.asteroids.append(WavefrontVBO(load_model(file), shader, 5, 5, 5))

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
        self.rotation_angle = 360.0 / rotation if rotation else 0

        shader = world.activate_shader('belt')
        if not isinstance(models, list):
            models = [models]

        self.belt = BeltVBO(radius, cross, len(models), count)
        self.objects = [
            WavefrontVBO(load_model(model), shader, info.get('sx', scale),
                         info.get('sy', scale), info.get('sz', scale))
            for model in models
        ]

        def callback():
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            shader.vertex_attribute('a_translate', self.belt.location_size, self.belt.type, GL_FALSE,
                                    self.belt.stride, self.belt.location_offset, divisor=1)
            shader.vertex_attribute('a_scale', self.belt.scale_size, self.belt.type, GL_FALSE,
                                    self.belt.stride, self.belt.scale_offset, divisor=1)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

        for model, vbo, count in zip(self.objects, self.belt.vbo, self.belt.sizes):
            model.additional_attributes(callback)

        super(Belt, self).__init__(world, name, (x, y, z), (inclination, longitude, argument))

    def update(self):
        super(Belt, self).update()
        pitch, yaw, roll = self.rotation
        self.rotation = pitch, self.world.tick * self.rotation_angle % 360, roll

    def draw(self, options):
        shader = self.world.activate_shader('belt')
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)
        shader.uniform_mat4('u_mvMatrix', self.mv_matrix)
        shader.uniform_mat4('u_modelMatrix', self.model_matrix)

        for object, vbo, count in zip(self.objects, self.belt.vbo, self.belt.sizes):
            object.draw(shader, instances=count)


class Sky(Entity):
    background = True

    def __init__(self, world, info, callback=None):
        pitch = world.evaluate(info.get('pitch', 0))
        yaw = world.evaluate(info.get('yaw', 0))
        roll = world.evaluate(info.get('roll', 0))

        super(Sky, self).__init__(world, 'Sky', (0, 0, 0), [pitch, yaw, roll])

        self.texture = get_best_texture(info['texture'], loader=get_cube_map, callback=callback)
        self.constellation = get_cube_map(info['constellation'])
        self.cube = Cube()
        self.vao = VAO()

        shader = self.world.activate_shader('sky')
        with self.vao:
            glBindBuffer(GL_ARRAY_BUFFER, self.cube.vbo)
            shader.vertex_attribute('a_direction', self.cube.direction_size, self.cube.type, GL_FALSE,
                                    self.cube.stride, self.cube.direction_offset)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, options):
        cam = self.world.cam
        shader = self.world.activate_shader('sky')
        shader.uniform_mat4('u_mvpMatrix', self.world.projection_matrix() *
                            Matrix4f.from_angles(rotation=(cam.pitch, cam.yaw, cam.roll)) *
                            Matrix4f.from_angles(rotation=self.rotation))

        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
        shader.uniform_texture('u_skysphere', 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.constellation)
        shader.uniform_texture('u_constellation', 1)

        shader.uniform_bool('u_lines', options.constellations)

        with self.vao:
            glDrawArrays(GL_TRIANGLES, 0, self.cube.vertex_count)

        glActiveTexture(GL_TEXTURE0)


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
        self.orbit_vao = None
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

    def get_orbit(self, shader):
        if not self.orbit:
            return

        # Cache key is the three orbital plane parameters and eccentricity
        cache = (self.orbit.eccentricity, self.orbit.longitude, self.orbit.inclination, self.orbit.argument)
        if self.orbit_cache == cache:
            return self.orbit_vbo, self.orbit_vao

        if self.orbit_vbo is not None:
            self.orbit_vbo.close()

        if self.orbit_vao is not None:
            self.orbit_vao.close()

        self.orbit_vbo = OrbitVBO(self.orbit)
        self.orbit_vao = VAO()

        with self.orbit_vao:
            glBindBuffer(GL_ARRAY_BUFFER, self.orbit_vbo.vbo)
            shader.vertex_attribute('a_position', self.orbit_vbo.position_size, self.orbit_vbo.type, GL_FALSE,
                                    self.orbit_vbo.stride, self.orbit_vbo.position_offset)

        self.orbit_cache = cache
        return self.orbit_vbo, self.orbit_vao

    def _draw_orbits(self, distance):
        shader = self.world.activate_shader('line')
        solid = distance < self.parent.orbit_opaque
        alpha = 1 if solid else (1 - (distance - self.parent.orbit_opaque) / self.parent.orbit_blend)
        shader.uniform_vec4('u_color', 1, 1, 1, alpha)
        shader.uniform_mat4('u_mvpMatrix', self.world.projection_matrix() * self.parent.orbit_matrix)

        if not solid:
            glEnable(GL_BLEND)

        vbo, vao = self.get_orbit(shader)
        with vao:
            glDrawArrays(GL_LINE_LOOP, 0, vbo.vertex_count)

        if not solid:
            glDisable(GL_BLEND)

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
    _sphere_cache = {}

    @classmethod
    def _get_sphere(cls, division, tangent=True):
        if (division, tangent) in cls._sphere_cache:
            return cls._sphere_cache[division, tangent]
        cls._sphere_cache[division, tangent] = sphere = \
            (TangentSphere if tangent else SimpleSphere)(division, division)
        return sphere

    def __init__(self, name, world, info, parent=None):
        super(SphericalBody, self).__init__(name, world, info, parent)

        self.radius = world.evaluate(info.get('radius', world.length)) / world.length
        division = info.get('division', max(min(int(self.radius / 8), 60), 10))

        self.light_source = info.get('light_source', False)
        self.shininess = info.get('shininess', 0)
        self.type = info.get('type', 'planet')

        self.texture = get_best_texture(info['texture'])
        self.normal_texture = None
        self.specular_texture = None
        self.emission_texture = None

        self.sphere = self._get_sphere(division, tangent=self.type == 'planet')
        self.vao = VAO()

        if self.type == 'planet':
            shader = self.world.activate_shader('planet')
            with self.vao:
                glBindBuffer(GL_ARRAY_BUFFER, self.sphere.vbo)
                shader.vertex_attribute('a_normal', self.sphere.direction_size, self.sphere.type, GL_FALSE,
                                        self.sphere.stride, self.sphere.direction_offset)
                shader.vertex_attribute('a_tangent', self.sphere.tangent_size, self.sphere.type, GL_FALSE,
                                        self.sphere.stride, self.sphere.tangent_offset)
                shader.vertex_attribute('a_uv', self.sphere.uv_size, self.sphere.type, GL_FALSE,
                                        self.sphere.stride, self.sphere.uv_offset)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
        elif self.type == 'star':
            shader = self.world.activate_shader('star')
            with self.vao:
                glBindBuffer(GL_ARRAY_BUFFER, self.sphere.vbo)
                shader.vertex_attribute('a_normal', self.sphere.direction_size, self.sphere.type, GL_FALSE,
                                        self.sphere.stride, self.sphere.direction_offset)
                shader.vertex_attribute('a_uv', self.sphere.uv_size, self.sphere.type, GL_FALSE,
                                        self.sphere.stride, self.sphere.uv_offset)
                glBindBuffer(GL_ARRAY_BUFFER, 0)
        else:
            raise ValueError('Invalid type: %s' % self.type)

        self.atmosphere = None
        self.clouds = None
        self.ring = 0

        if 'normal_map' in info:
            self.normal_texture = get_best_texture(info['normal_map'])

        if 'specular_map' in info:
            self.specular_texture = get_best_texture(info['specular_map'])

        if 'emission_map' in info:
            self.emission_texture = get_best_texture(info['emission_map'])

        if 'atmosphere' in info:
            atmosphere_data = info['atmosphere']
            atm_size = world.evaluate(atmosphere_data.get('glow_size', None))
            atm_texture = atmosphere_data.get('glow_texture', None)
            atm_color = atmosphere_data.get('glow_color', None)
            cloud_texture = atmosphere_data.get('cloud_texture', None)
            if cloud_texture is not None:
                self.cloud_transparency = get_best_texture(cloud_texture, loader=load_alpha_mask)
                self.cloud_radius = self.radius + 2
                self.clouds = self._get_sphere(division, tangent=False)
                self.cloud_vao = VAO()
                shader = self.world.activate_shader('clouds')
                with self.cloud_vao:
                    glBindBuffer(GL_ARRAY_BUFFER, self.clouds.vbo)
                    shader.vertex_attribute('a_normal', self.clouds.direction_size, self.clouds.type, GL_FALSE,
                                            self.clouds.stride, self.clouds.direction_offset)
                    shader.vertex_attribute('a_uv', self.clouds.uv_size, self.clouds.type, GL_FALSE,
                                            self.clouds.stride, self.clouds.uv_offset)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)

            if atm_texture is not None and atm_color is not None:
                self.atm_texture = load_texture_1d(atm_texture, clamp=True)
                self.atm_color = atm_color
                self.atmosphere = Disk(self.radius, self.radius + atm_size, 30)
                self.atmosphere_vao = VAO()
                shader = self.world.activate_shader('atmosphere')
                with self.atmosphere_vao:
                    glBindBuffer(GL_ARRAY_BUFFER, self.atmosphere.vbo)
                    shader.vertex_attribute('a_position', self.atmosphere.position_size, self.atmosphere.type, GL_FALSE,
                                            self.atmosphere.stride, self.atmosphere.position_offset)
                    shader.vertex_attribute('a_u', self.atmosphere.u_size, self.atmosphere.type, GL_FALSE,
                                            self.atmosphere.stride, self.atmosphere.u_offset)
                    glBindBuffer(GL_ARRAY_BUFFER, 0)

        if 'ring' in info:
            distance = world.evaluate(info['ring'].get('distance', self.radius * 1.2))
            size = world.evaluate(info['ring'].get('size', self.radius / 2))

            pitch, yaw, roll = self.rotation
            pitch = world.evaluate(info['ring'].get('pitch', pitch))
            yaw = world.evaluate(info['ring'].get('yaw', yaw))
            roll = world.evaluate(info['ring'].get('roll', roll))
            self.ring_rotation = pitch, yaw, roll

            self.ring_texture = load_texture_1d(info['ring'].get('texture'), clamp=True)
            self.ring = Disk(distance, distance + size, 30)

            self.ring_vao = VAO()
            shader = self.world.activate_shader('ring')
            with self.ring_vao:
                glBindBuffer(GL_ARRAY_BUFFER, self.ring.vbo)
                shader.vertex_attribute('a_position', self.ring.position_size, self.ring.type, GL_FALSE,
                                        self.ring.stride, self.ring.position_offset)
                shader.vertex_attribute('a_u', self.ring.u_size, self.ring.type, GL_FALSE,
                                        self.ring.stride, self.ring.u_offset)
                glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _draw_planet(self):
        shader = self.world.activate_shader('planet')
        shader.uniform_float('u_radius', self.radius)
        shader.uniform_mat4('u_modelMatrix', self.model_matrix)
        shader.uniform_mat4('u_mvMatrix', self.mv_matrix)
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        shader.uniform_texture('u_planet.diffuseMap', 0)

        shader.uniform_bool('u_planet.hasNormal', self.normal_texture)
        if self.normal_texture:
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.normal_texture)
            shader.uniform_texture('u_planet.normalMap', 1)

        shader.uniform_bool('u_planet.hasSpecular', self.specular_texture)
        if self.specular_texture:
            glActiveTexture(GL_TEXTURE2)
            glBindTexture(GL_TEXTURE_2D, self.specular_texture)
            shader.uniform_texture('u_planet.specularMap', 2)
            shader.uniform_vec3('u_planet.specular', 1, 1, 1)
            shader.uniform_float('u_planet.shininess', 10)
        else:
            shader.uniform_vec3('u_planet.specular', 0, 0, 0)
            shader.uniform_float('u_planet.shininess', 0)

        shader.uniform_bool('u_planet.hasEmission', self.emission_texture)
        if self.emission_texture:
            glActiveTexture(GL_TEXTURE3)
            glBindTexture(GL_TEXTURE_2D, self.emission_texture)
            shader.uniform_texture('u_planet.emissionMap', 3)
            shader.uniform_vec3('u_planet.ambient', 0, 0, 0)
            shader.uniform_vec3('u_planet.emission', 1, 1, 1)
        else:
            shader.uniform_vec3('u_planet.ambient', 1, 1, 1)
            shader.uniform_vec3('u_planet.emission', 0, 0, 0)

        shader.uniform_vec3('u_planet.diffuse', 1, 1, 1)

        with self.vao:
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.sphere.vertex_count)

        glActiveTexture(GL_TEXTURE0)

    def _draw_star(self):
        shader = self.world.activate_shader('star')
        shader.uniform_float('u_radius', self.radius)
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        shader.uniform_texture('u_emission', 0)

        with self.vao:
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.sphere.vertex_count)

    def _draw_sphere(self):
        if self.type == 'planet':
            self._draw_planet()
        elif self.type == 'star':
            self._draw_star()

    def _draw_atmosphere(self):
        glEnable(GL_BLEND)
        glDisable(GL_CULL_FACE)
        shader = self.world.activate_shader('atmosphere')

        mv = self.mv_matrix.matrix
        matrix = Matrix4f([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, mv[12], mv[13], mv[14], 1])
        shader.uniform_mat4('u_mvpMatrix', self.world.projection_matrix() * matrix)

        glBindTexture(GL_TEXTURE_1D, self.atm_texture)
        shader.uniform_texture('u_transparency', 0)
        shader.uniform_vec3('u_color', *self.atm_color)

        with self.atmosphere_vao:
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.atmosphere.vertex_count)

        glDisable(GL_BLEND)
        glEnable(GL_CULL_FACE)

    def _draw_clouds(self):
        glEnable(GL_BLEND)
        shader = self.world.activate_shader('clouds')
        shader.uniform_float('u_radius', self.cloud_radius)
        shader.uniform_mat4('u_modelMatrix', self.model_matrix)
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)

        glBindTexture(GL_TEXTURE_2D, self.cloud_transparency)
        shader.uniform_texture('u_transparency', 0)
        shader.uniform_vec3('u_diffuse', 1, 1, 1)
        shader.uniform_vec3('u_ambient', 0.1, 0.1, 0.1)

        with self.cloud_vao:
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.clouds.vertex_count)

        glDisable(GL_BLEND)

    def _draw_rings(self):
        glEnable(GL_BLEND)
        glDisable(GL_CULL_FACE)
        shader = self.world.activate_shader('ring')
        shader.uniform_mat4('u_modelMatrix', self.model_matrix)
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)
        shader.uniform_vec3('u_planet', *self.location)
        shader.uniform_vec3('u_sun', 0, 0, 0)
        shader.uniform_float('u_planetRadius', self.radius)
        shader.uniform_float('u_ambient', 0.1)

        glBindTexture(GL_TEXTURE_1D, self.ring_texture)
        shader.uniform_texture('u_texture', 0)

        with self.ring_vao:
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.ring.vertex_count)

        glDisable(GL_BLEND)
        glEnable(GL_CULL_FACE)

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
        shader = world.activate_shader('model')
        self.vbo = WavefrontVBO(load_model(info['model']), shader, info.get('sx', scale),
                                info.get('sy', scale), info.get('sz', scale))

    def _draw(self, options):
        shader = self.world.activate_shader('model')
        shader.uniform_mat4('u_mvpMatrix', self.mvp_matrix)
        shader.uniform_mat4('u_mvMatrix', self.mv_matrix)
        shader.uniform_mat4('u_modelMatrix', self.model_matrix)
        self.vbo.draw(shader)
