from math import *
from pyglet.gl import *
from random import random, gauss, choice

TWOPI = pi * 2

__all__ = ['compile', 'ortho', 'frustrum', 'crosshair', 'circle', 'disk', 'sphere', 'colourball', 'torus', 'belt',
           'flare', 'normal_sphere', 'glSection', 'glMatrix', 'glRestore', 'progress_bar']


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


class glMatrix(object):
    def __enter__(self):
        glPushMatrix()

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


def crosshair(size, (cx, cy)):
    with glSection(GL_LINES):
        glVertex2f(cx - size, cy)
        glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size)
        glVertex2f(cx, cy + size)


def circle(r, seg, (cx, cy)):
    with glSection(GL_LINE_LOOP):
        for i in xrange(seg):
            theta = TWOPI * i / seg
            glVertex2f(cx + cos(theta) * r, cy + sin(theta) * r)


def disk(rinner, router, segs, tex):
    with glRestore(GL_ENABLE_BIT):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glDisable(GL_LIGHTING)
        glBindTexture(GL_TEXTURE_2D, tex)
        res = segs * 5

        with glSection(GL_TRIANGLE_STRIP):
            factor = TWOPI / res
            theta = 0
            for n in xrange(res + 1):
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
        glDisable(GL_LIGHTING)
        glBindTexture(GL_TEXTURE_2D, tex)
        last_x = 1
        last_y = 0
        last_theta = 0
        factor = TWOPI / res
        rdelta = (router - rinner)
        with glSection(GL_QUADS):
            for i in xrange(res + 1):
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


def sphere(r, lats, longs, tex, lighting=True, fv4=GLfloat * 4):
    """
        Sphere function from the OpenGL red book.
    """
    with glRestore(GL_ENABLE_BIT | GL_TEXTURE_BIT):
        sphere = gluNewQuadric()
        gluQuadricDrawStyle(sphere, GLU_FILL)
        gluQuadricTexture(sphere, True)
        if lighting:
            gluQuadricNormals(sphere, GLU_SMOOTH)

        glEnable(GL_TEXTURE_2D)
        if lighting:
            glDisable(GL_BLEND)
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, fv4(1, 1, 1, 0))
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(1, 1, 1, 0))
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 125)
        else:
            glDisable(GL_LIGHTING)
        glBindTexture(GL_TEXTURE_2D, tex)

        gluSphere(sphere, r, lats, longs)

        gluDeleteQuadric(sphere)


def colourball(r, lats, longs, colour, fv4=GLfloat * 4):
    """
        Sphere function from the OpenGL red book.
    """
    with glRestore(GL_ENABLE_BIT):
        sphere = gluNewQuadric()

        glDisable(GL_BLEND)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, fv4(*colour))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 125)

        gluSphere(sphere, r, lats, longs)

        glEnable(GL_BLEND)
        gluDeleteQuadric(sphere)


try:
    from _glgeom import normal_sphere
except ImportError:
    import warnings
    warnings.warn('Large sphere drawing in Python is slow')

    def normal_sphere(r, divide, tex, normal, lighting=True, fv4=GLfloat * 4):
        from texture import pil_load
        print 'Loading normal map: %s...' % normal,
        normal_map = pil_load(normal)
        normal = normal_map.load()
        print
        width, height = normal_map.size
        gray_scale = len(normal[0, 0]) == 1

        with glRestore(GL_ENABLE_BIT | GL_TEXTURE_BIT):
            glEnable(GL_TEXTURE_2D)
            if lighting:
                glDisable(GL_BLEND)
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, fv4(1, 1, 1, 0))
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(1, 1, 1, 0))
                glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 125)
            else:
                glDisable(GL_LIGHTING)
            glBindTexture(GL_TEXTURE_2D, tex)

            twopi_divide = TWOPI / divide
            pi_divide = pi / divide
            with glSection(GL_TRIANGLE_STRIP):
                for j in xrange(divide + 1):
                    phi1 = j * twopi_divide
                    phi2 = (j + 1) * twopi_divide

                    for i in xrange(divide + 1):
                        theta = i * pi_divide

                        s = phi2 / TWOPI
                        u = min(int(s * width), width - 1)
                        t = theta / pi
                        v = min(int(t * height), height - 1)
                        if gray_scale:
                            x = y = z = normal[u, v]
                        else:
                            x, y, z = normal[u, v]
                        dx, dy, dz = sin(theta) * cos(phi2), sin(theta) * sin(phi2), cos(theta)
                        nx, ny, nz = x / 127.5 - 1, y / 127.5 - 1, z / 127.5 - 1  # Make into [-1, 1]
                        nx, nz = cos(theta) * nx + sin(theta) * nz, -sin(theta) * nx + cos(theta) * nz
                        nx, ny = cos(phi2)  * nx - sin(phi2)  * ny,  sin(phi2)  * nx + cos(phi2)  * ny
                        glNormal3f(nx, ny, nz)
                        glTexCoord2f(s, 1 - t)  # GL is bottom up
                        glVertex3f(r * dx, r * dy, r * dz)

                        s = phi1 / TWOPI    # x
                        u = min(int(s * width), width - 1)
                        if gray_scale:
                            x = y = z = normal[u, v]
                        else:
                            x, y, z = normal[u, v]
                        dx, dy = sin(theta) * cos(phi1), sin(theta) * sin(phi1)
                        nx, ny, nz = x / 127.5 - 1, y / 127.5 - 1, z / 127.5 - 1
                        nx, nz = cos(theta) * nx + sin(theta) * nz, -sin(theta) * nx + cos(theta) * nz
                        nx, ny = cos(phi1)  * nx - sin(phi1)  * ny,  sin(phi1)  * nx + cos(phi1)  * ny
                        glNormal3f(nx, ny, nz)
                        glTexCoord2f(s, 1 - t)
                        glVertex3f(r * dx, r * dy, r * dz)


def belt(radius, cross, object, count):
    for i in xrange(count):
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


try:
    from _glgeom import torus
except ImportError:
    def torus(major_radius, minor_radius, n_major, n_minor, material, shininess=125, fv4=GLfloat * 4):
        """
            Torus function from the OpenGL red book.
        """
        with glRestore(GL_CURRENT_BIT):
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, fv4(*material))
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(1, 1, 1, 1))
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

            major_s = TWOPI / n_major
            minor_s = TWOPI / n_minor

            def n(x, y, z):
                m = 1.0 / sqrt(x * x + y * y + z * z)
                return x * m, y * m, z * m

            for i in xrange(n_major):
                a0 = i * major_s
                a1 = a0 + major_s
                x0 = cos(a0)
                y0 = sin(a0)
                x1 = cos(a1)
                y1 = sin(a1)

                with glSection(GL_TRIANGLE_STRIP):
                    for j in xrange(n_minor + 1):
                        b = j * minor_s
                        c = cos(b)
                        r = minor_radius * c + major_radius
                        z = minor_radius * sin(b)

                        glNormal3f(*n(x0 * c, y0 * c, z / minor_radius))
                        glVertex3f(x0 * r, y0 * r, z)

                        glNormal3f(*n(x1 * c, y1 * c, z / minor_radius))
                        glVertex3f(x1 * r, y1 * r, z)


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
