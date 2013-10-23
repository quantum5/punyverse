from math import *
from pyglet.gl import *
from pyglet.gl.glu import *

TWOPI = pi * 2


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
    glBegin(GL_LINES)
    glVertex2f(cx - size, cy)
    glVertex2f(cx + size, cy)
    glVertex2f(cx, cy - size)
    glVertex2f(cx, cy + size)
    glEnd()


def circle(r, seg, (cx, cy)):
    glBegin(GL_LINE_LOOP)
    for i in xrange(seg):
        theta = TWOPI * i / seg
        glVertex2f(cx + cos(theta) * r, cy + sin(theta) * r)
    glEnd()


def disk(rinner, router, segs, tex):
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glBindTexture(GL_TEXTURE_2D, tex)
    res = segs * 5

    glBegin(GL_TRIANGLE_STRIP)
    texture = 0
    factor = TWOPI / res
    theta = 0
    for n in xrange(res + 1):
        theta += factor
        x = cos(theta)
        y = sin(theta)
        glTexCoord2f(0, texture)
        glVertex2f(rinner * x, rinner * y)
        glTexCoord2f(1, texture)
        glVertex2f(router * x, router * y)
        texture ^= 1
    glEnd()
    glEnable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)


def sphere(r, lats, longs, tex, lighting=True, fv4=GLfloat * 4):
    '''
        Sphere function from the OpenGL red book.
    '''
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

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glEnable(GL_BLEND)
    gluDeleteQuadric(sphere)


def colourball(r, lats, longs, colour, fv4=GLfloat * 4):
    '''
        Sphere function from the OpenGL red book.
    '''
    sphere = gluNewQuadric()

    glDisable(GL_BLEND)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, fv4(*colour))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 125)

    gluSphere(sphere, r, lats, longs)

    glEnable(GL_BLEND)
    gluDeleteQuadric(sphere)


try:
    from _glgeom import torus
except ImportError:
    def torus(major_radius, minor_radius, n_major, n_minor, material, shininess=125, fv4=GLfloat * 4):
        '''
            Torus function from the OpenGL red book.
        '''
        glPushAttrib(GL_CURRENT_BIT)
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

            glBegin(GL_TRIANGLE_STRIP)

            for j in xrange(n_minor + 1):
                b = j * minor_s
                c = cos(b)
                r = minor_radius * c + major_radius
                z = minor_radius * sin(b)

                glNormal3f(*n(x0 * c, y0 * c, z / minor_radius))
                glVertex3f(x0 * r, y0 * r, z)

                glNormal3f(*n(x1 * c, y1 * c, z / minor_radius))
                glVertex3f(x1 * r, y1 * r, z)

            glEnd()
        glPopAttrib()