from array import array
from ctypes import c_int, c_float, byref, cast, POINTER, c_uint, c_short, c_ushort
from math import *
from random import random, gauss, choice

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

TWOPI = pi * 2

__all__ = ['compile', 'ortho', 'frustrum', 'crosshair', 'circle', 'Sphere', 'belt',
           'glSection', 'glRestore', 'progress_bar']


class glContext(object):
    def __init__(self, context):
        self.new_context = context

    def __enter__(self):
        self.old_context = get_current_context()
        self.new_context.set_current()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.old_context.set_current()


class glSection(object):
    def __init__(self, type):
        self.type = type

    def __enter__(self):
        glBegin(self.type)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glEnd()


class glRestore(object):
    def __init__(self, flags):
        self.flags = flags

    def __enter__(self):
        glPushAttrib(self.flags)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopAttrib()


class glRestoreClient(object):
    def __init__(self, flags):
        self.flags = flags

    def __enter__(self):
        glPushClientAttrib(self.flags)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopClientAttrib()


def array_to_ctypes(arr):
    return cast(arr.buffer_info()[0], POINTER({
        'f': c_float,
        'i': c_int,
        'I': c_uint,
        'h': c_short,
        'H': c_ushort,
    }[arr.typecode]))


def array_to_gl_buffer(buffer, array_type='f'):
    vbo = c_uint()
    glGenBuffers(1, byref(vbo))
    glBindBuffer(GL_ARRAY_BUFFER, vbo.value)
    buffer = array(array_type, buffer)
    glBufferData(GL_ARRAY_BUFFER, buffer.itemsize * len(buffer), array_to_ctypes(buffer), GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return vbo.value


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

    def as_gl(self):
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


def compile(pointer, *args, **kwargs):
    display = glGenLists(1)
    glNewList(display, GL_COMPILE)
    pointer(*args, **kwargs)
    glEndList()
    return display


def ortho(width, height):
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def frustrum():
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)


def crosshair(size, coords):
    cx, cy = coords
    with glSection(GL_LINES):
        glVertex2f(cx - size, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size)
        glVertex2f(cx, cy + size)


def circle(r, seg, coords):
    cx, cy = coords
    with glSection(GL_LINE_LOOP):
        for i in range(seg):
            theta = TWOPI * i / seg
            glVertex2f(cx + cos(theta) * r, cy + sin(theta) * r)


class Disk(object):
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
        self.vbo = array_to_gl_buffer(buffer)

    def draw(self):
        with glRestoreClient(GL_CLIENT_VERTEX_ARRAY_BIT):
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glVertexPointer(3, GL_FLOAT, 12, 0)
            glTexCoordPointer(1, GL_FLOAT, 12, 8)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)
            glBindBuffer(GL_ARRAY_BUFFER, 0)


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

        self.vbo = array_to_gl_buffer(buffer)


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
        self.vbo = array_to_gl_buffer(buffer)


class Sphere(object):
    def __init__(self, r, lats, longs):
        tau = pi * 2
        phi_div = tau / longs
        theta_div = pi / lats

        self.vertex_count = (lats + 1) * (longs + 1) * 2
        buffer = self.vertex_count * 8 * [0]
        index = 0
        for i in range(longs + 1):
            phi1, phi2 = i * phi_div, (i + 1) * phi_div
            for j in range(lats + 1):
                theta = j * theta_div
                sine = sin(theta)
                dz = cos(theta)
                t = 1 - theta / pi
                dx1 = sine * cos(phi2)
                dy1 = sine * sin(phi2)
                dx2 = sine * cos(phi1)
                dy2 = sine * sin(phi1)
                buffer[index:index + 16] = [r * dx1, r * dy1, r * dz, dx1, dy1, dz, phi2 / tau, t,
                                            r * dx2, r * dy2, r * dz, dx2, dy2, dz, phi1 / tau, t]
                index += 16

        self.vbo = array_to_gl_buffer(buffer)

    def draw(self):
        with glRestoreClient(GL_CLIENT_VERTEX_ARRAY_BIT):
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glVertexPointer(3, GL_FLOAT, 32, 0)
            glNormalPointer(GL_FLOAT, 32, 3 * 4)
            glTexCoordPointer(3, GL_FLOAT, 32, 6 * 4)
            glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)
            glBindBuffer(GL_ARRAY_BUFFER, 0)


class OrbitVBO(object):
    def __init__(self, orbit):
        buffer = 360 * 3 * [0]
        for theta in range(360):
            x, z, y = orbit.orbit(theta)
            buffer[3*theta:3*theta+3] = [x, y, z]

        self.vbo = array_to_gl_buffer(buffer)

    def draw(self):
        with glRestoreClient(GL_CLIENT_VERTEX_ARRAY_BIT):
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 12, 0)
            glDrawArrays(GL_LINE_LOOP, 0, 360)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def close(self):
        if self.vbo is not None:
            vbo = c_uint(self.vbo)
            glDeleteBuffers(1, byref(vbo))
            self.vbo = None

    def __del__(self):
        self.close()


def belt(radius, cross, object, count):
    for i in range(count):
        theta = TWOPI * random()
        r = gauss(radius, cross)
        x, y, z = cos(theta) * r, gauss(0, cross), sin(theta) * r

        glPushMatrix()
        glTranslatef(x, y, z)
        scale = gauss(1, 0.5)
        if scale < 0:
            scale = 1
        glScalef(scale, scale, scale)
        choice(object).draw()
        glPopMatrix()


def progress_bar(x, y, width, height, filled):
    with glRestore(GL_ENABLE_BIT):
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        x1 = x
        x2 = x + width
        y1 = y
        y2 = y - height
        y3 = 0.65 * y1 + 0.35 * y2
        y4 = 0.25 * y1 + 0.75 * y2

        glColor3f(0.6, 0.6, 0.6)
        with glSection(GL_LINE_LOOP):
            glVertex2f(x1, y1)
            glVertex2f(x1, y2)
            glVertex2f(x2, y2)
            glVertex2f(x2, y1)

        x1 += 1
        y1 -= 1
        x2 = x + width * filled - 1

        with glSection(GL_TRIANGLE_STRIP):
            glColor3f(0.81, 1, 0.82)
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
            glColor3f(0, 0.83, 0.16)
            glVertex2f(x1, y3)
            glVertex2f(x2, y3)
            glVertex2f(x1, y4)
            glVertex2f(x2, y4)
            glColor3f(0.37, 0.92, 0.43)
            glVertex2f(x1, y2)
            glVertex2f(x2, y2)
