from __future__ import division

from array import array
from ctypes import c_int, c_float, byref, cast, POINTER, c_uint, c_short, c_ushort
from math import *
from random import random, gauss, choice

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

TWOPI = pi * 2

__all__ = ['FontEngine', 'Matrix4f', 'Disk', 'OrbitVBO', 'SimpleSphere',
           'TangentSphere', 'Cube', 'Circle', 'BeltVBO', 'VAO']


def array_to_ctypes(arr):
    return cast(arr.buffer_info()[0], POINTER({
        'f': c_float,
        'i': c_int,
        'I': c_uint,
        'h': c_short,
        'H': c_ushort,
    }[arr.typecode]))


def array_to_gl_buffer(buffer):
    vbo = c_uint()
    glGenBuffers(1, byref(vbo))
    glBindBuffer(GL_ARRAY_BUFFER, vbo.value)
    glBufferData(GL_ARRAY_BUFFER, buffer.itemsize * len(buffer), array_to_ctypes(buffer), GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo.value


def list_to_gl_buffer(buffer, array_type='f'):
    return array_to_gl_buffer(array(array_type, buffer))


class Matrix4f(object):
    def __init__(self, matrix):
        self.matrix = array('f', matrix)
        assert len(self.matrix) == 16

    @classmethod
    def from_angles(cls, location=(0, 0, 0), rotation=(0, 0, 0), view=False):
        m = [0] * 16
        x, y, z = location
        pitch, yaw, roll = rotation
        sp, sy, sr = sin(radians(pitch)), sin(radians(yaw)), sin(radians(roll))
        cp, cy, cr = cos(radians(pitch)), cos(radians(yaw)), cos(radians(roll))

        m[0x0] = cy * cr
        m[0x1] = sp * sy * cr + cp * sr
        m[0x2] = sp * sr - cp * sy * cr
        m[0x3] = 0
        m[0x4] = -cy * sr
        m[0x5] = cp * cr - sp * sy * sr
        m[0x6] = cp * sy * sr + sp * cr
        m[0x7] = 0
        m[0x8] = sy
        m[0x9] = -sp * cy
        m[0xA] = cp * cy
        m[0xB] = 0
        if view:
            m[0xC] = m[0x0] * -x + m[0x4] * -y + m[0x8] * -z
            m[0xD] = m[0x1] * -x + m[0x5] * -y + m[0x9] * -z
            m[0xE] = m[0x2] * -x + m[0x6] * -y + m[0xA] * -z
        else:
            m[0xC] = x
            m[0xD] = y
            m[0xE] = z
        m[0xF] = 1
        return cls(m)

    @property
    def _as_parameter_(self):
        return array_to_ctypes(self.matrix)

    @property
    def bytes(self):
        return self.matrix.itemsize * 16

    def __mul__(self, other):
        if not isinstance(other, Matrix4f):
            return NotImplemented

        rows = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))
        cols = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (12, 13, 14, 15))
        a, b = self.matrix, other.matrix
        return type(self)(sum(a[i] * b[j] for i, j in zip(r, c)) for c in cols for r in rows)


class Circle(object):
    type = GL_FLOAT
    stride = 2 * 4
    position_offset = 0
    position_size = 2

    def __init__(self, r, segs, shader):
        self.vertex_count = segs
        buffer = segs * 2 * [0]
        delta = 2 * pi / segs
        for i in range(segs):
            theta = delta * i
            buffer[2*i:2*i+2] = [cos(theta) * r, sin(theta) * r]
        self.vbo = list_to_gl_buffer(buffer)

        self.vao = VAO()
        with self.vao:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            shader.vertex_attribute('a_position', self.position_size, self.type, GL_FALSE,
                                    self.stride, self.position_offset)
            glBindBuffer(GL_ARRAY_BUFFER, 0)


class Disk(object):
    type = GL_FLOAT
    stride = 3 * 4
    position_offset = 0
    position_size = 2
    u_offset = position_size * 4
    u_size = 1

    def __init__(self, rinner, router, segs):
        res = segs * 5
        delta = 2 * pi / res
        self.vertex_count = (res + 1) * 2
        # Need padding to make the last vertex render correctly... why?
        buffer = self.vertex_count * 3 * [0]
        for i in range(res):
            theta = delta * i
            x, y = cos(theta), sin(theta)
            buffer[6*i:6*i+6] = [rinner * x, rinner * y, 0, router * x, router * y, 1]
        buffer[6*res:6*res+6] = buffer[:6]
        self.vbo = list_to_gl_buffer(buffer)


class SimpleSphere(object):
    type = GL_FLOAT
    stride = 5 * 4
    direction_offset = 0
    direction_size = 3
    uv_offset = direction_size * 4
    uv_size = 2

    def __init__(self, lats, longs):
        tau = pi * 2
        phi_div = tau / longs
        theta_div = pi / lats

        self.vertex_count = (lats + 1) * (longs + 1) * 2
        buffer = self.vertex_count * 5 * [0]
        index = 0
        reverse = False
        for i in range(longs + 1):
            phi1, phi2 = i * phi_div, (i + 1) * phi_div
            if reverse:
                phi1, phi2 = phi2, phi1
            for j in range(lats + 1):
                theta = j * theta_div
                if reverse:
                    theta = pi - theta
                sine = sin(theta)
                dz = cos(theta)
                t = 1 - theta / pi
                buffer[index:index + 10] = [sine * cos(phi2), sine * sin(phi2), dz, phi2 / tau, t,
                                            sine * cos(phi1), sine * sin(phi1), dz, phi1 / tau, t]
                index += 10
            reverse ^= True

        self.vbo = list_to_gl_buffer(buffer)


class TangentSphere(object):
    type = GL_FLOAT
    stride = 7 * 4
    direction_offset = 0
    direction_size = 3
    tangent_offset = direction_size * 4
    tangent_size = 2
    uv_offset = tangent_offset + tangent_size * 4
    uv_size = 2

    def __init__(self, lats, longs):
        tau = pi * 2
        phi_div = tau / longs
        theta_div = pi / lats

        self.vertex_count = (lats + 1) * (longs + 1) * 2
        buffer = self.vertex_count * 8 * [0]
        index = 0
        reverse = False
        for i in range(longs + 1):
            phi1, phi2 = i * phi_div, (i + 1) * phi_div
            if reverse:
                phi1, phi2 = phi2, phi1
            for j in range(lats + 1):
                theta = j * theta_div
                if reverse:
                    theta = pi - theta
                sine = sin(theta)
                dz = cos(theta)
                t = 1 - theta / pi
                sphi2, cphi2 = sin(phi2), cos(phi2)
                sphi1, cphi1 = sin(phi1), cos(phi1)
                buffer[index:index + 14] = [
                    sine * cphi2, sine * sphi2, dz, sine * -sphi2, sine * cphi2, phi2 / tau, t,
                    sine * cphi1, sine * sphi1, dz, sine * -sphi1, sine * cphi1, phi1 / tau, t,
                ]
                index += 14
            reverse ^= True
        self.vbo = list_to_gl_buffer(buffer)


class Cube(object):
    type = GL_SHORT
    stride = 3 * 2
    direction_offset = 0
    direction_size = 3
    vertex_count = 36

    def __init__(self):
        self.vbo = list_to_gl_buffer([
            -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1,
            -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, -1, -1, 1, -1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, -1, 1, 1, -1, 1, 1, 1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, -1,
            -1, -1, 1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, -1, 1
        ], 'h')


class OrbitVBO(object):
    type = GL_FLOAT
    stride = 3 * 4
    position_offset = 0
    position_size = 3
    vertex_count = 360

    def __init__(self, orbit):
        buffer = 360 * 3 * [0]
        for theta in range(360):
            x, z, y = orbit.orbit(theta)
            buffer[3*theta:3*theta+3] = [x, y, z]

        self.vbo = list_to_gl_buffer(buffer)

    def close(self):
        if self.vbo is not None:
            vbo = c_uint(self.vbo)
            glDeleteBuffers(1, byref(vbo))
            self.vbo = None

    def __del__(self):
        self.close()


class FontEngine(object):
    type = GL_SHORT
    stride = 4 * 2
    position_offset = 0
    position_size = 2
    tex_offset = position_size * 2
    tex_size = 2

    def __init__(self, shader, max_length=256):
        self.storage = array('h', max_length * 24 * [0])
        vbo = GLuint()
        glGenBuffers(1, byref(vbo))
        self.vbo = vbo.value
        self.vertex_count = None

        self.vao = VAO()
        with self.vao:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            shader.vertex_attribute('a_rc', self.position_size, self.type, GL_FALSE,
                                    self.stride, self.position_offset)
            shader.vertex_attribute('a_tex', self.tex_size, self.type, GL_FALSE,
                                    self.stride, self.tex_offset)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, string):
        index = 0
        row = 0
        col = 0
        for c in string:
            if c == '\n':
                row += 1
                col = 0
                continue
            o = ord(c)
            if 32 <= o < 128:
                self.storage[24*index:24*index+24] = array('h', [
                    row, col, o - 32, 1,
                    row + 1, col, o - 32, 0,
                    row + 1, col + 1, o - 31, 0,
                    row, col, o - 32, 1,
                    row + 1, col + 1, o - 31, 0,
                    row, col + 1, o - 31, 1,
                ])
                index += 1
                col += 1

        self.vertex_count = index * 6

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.storage.itemsize * len(self.storage),
                     array_to_ctypes(self.storage), GL_STREAM_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)


class BeltVBO(object):
    type = GL_FLOAT
    stride = 4 * 4
    location_offset = 0
    location_size = 3
    scale_offset = location_size * 4
    scale_size = 1

    def __init__(self, radius, cross, objects, count):
        arrays = [array('f') for i in range(objects)]

        for i in range(count):
            theta = TWOPI * random()
            r = gauss(radius, cross)
            x, y, z = cos(theta) * r, gauss(0, cross), sin(theta) * r
            scale = gauss(1, 0.5)
            if scale < 0:
                scale = 1
            choice(arrays).extend((x, y, z, scale))

        self.vbo = []
        self.sizes = []
        for a in arrays:
            self.vbo.append(array_to_gl_buffer(a))
            self.sizes.append(len(a) // 4)


class VAO(object):
    def __init__(self):
        buffer = GLuint()
        glGenVertexArrays(1, byref(buffer))
        self.vao = buffer

    def __enter__(self):
        glBindVertexArray(self.vao)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glBindVertexArray(0)
