from array import array
from ctypes import c_int, c_float, byref, cast, POINTER, c_uint
from math import *
from random import random, gauss, choice

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

TWOPI = pi * 2

__all__ = ['compile', 'ortho', 'frustrum', 'crosshair', 'circle', 'disk', 'Sphere', 'belt',
           'flare', 'glSection', 'glMatrix', 'glRestore', 'progress_bar']


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


class glMatrix(object):
    def __init__(self, location=None, rotation=None):
        self.location = location
        self.rotation = rotation

    def __enter__(self):
        glPushMatrix()

        if self.location:
            glTranslatef(*self.location)

        if self.rotation:
            pitch, yaw, roll = self.rotation
            glRotatef(pitch, 1, 0, 0)
            glRotatef(yaw, 0, 1, 0)
            glRotatef(roll, 0, 0, 1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopMatrix()


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


def disk(rinner, router, segs, tex):
    with glRestore(GL_ENABLE_BIT):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)
        glBindTexture(GL_TEXTURE_2D, tex)
        res = segs * 5

        with glSection(GL_TRIANGLE_STRIP):
            factor = TWOPI / res
            theta = 0
            for n in range(res + 1):
                theta += factor
                x = cos(theta)
                y = sin(theta)
                glTexCoord2f(0, 0)
                glVertex2f(rinner * x, rinner * y)
                glTexCoord2f(1, 0)
                glVertex2f(router * x, router * y)


def flare(rinner, router, res, prob, tex):
    with glRestore(GL_ENABLE_BIT):
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glBindTexture(GL_TEXTURE_2D, tex)
        last_x = 1
        last_y = 0
        last_theta = 0
        factor = TWOPI / res
        rdelta = (router - rinner)
        with glSection(GL_QUADS):
            for i in range(res + 1):
                theta = last_theta + factor
                x = cos(theta)
                y = sin(theta)
                if random() > prob:
                    distance = rinner + rdelta * random()
                    avg_theta = (last_theta + theta) / 2
                    x0, y0 = rinner * last_x, rinner * last_y
                    x1, y1 = rinner * x, rinner * y
                    x2, y2 = distance * cos(avg_theta), distance * sin(avg_theta)
                    glTexCoord2f(0, 0)
                    glVertex2f(x0, y0)
                    glTexCoord2f(0, 1)
                    glVertex2f(x1, y1)
                    glTexCoord2f(1, 0)
                    glVertex2f(x2, y2)
                    glTexCoord2f(1, 1)
                    glVertex2f(x2, y2)
                last_theta = theta
                last_x = x
                last_y = y


def array_to_ctypes(arr):
    return cast(arr.buffer_info()[0], POINTER({
        'f': c_float,
        'i': c_int,
        'I': c_uint,
    }[arr.typecode]))


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

        vbo = c_uint()
        glGenBuffers(1, byref(vbo))
        self.vbo = vbo.value
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        buffer = array('f', buffer)
        glBufferData(GL_ARRAY_BUFFER, buffer.itemsize * len(buffer), array_to_ctypes(buffer),  GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

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


def belt(radius, cross, object, count):
    for i in range(count):
        theta = TWOPI * random()
        r = gauss(radius, cross)
        x, y, z = cos(theta) * r, gauss(0, cross), sin(theta) * r

        with glMatrix():
            glTranslatef(x, y, z)
            scale = gauss(1, 0.5)
            if scale < 0:
                scale = 1
            glScalef(scale, scale, scale)
            glCallList(choice(object))


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
