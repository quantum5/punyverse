from libc.math cimport sin, cos, sqrt
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
cimport cython

include "_cyopengl.pxi"
cdef float PI = 3.1415926535897932324626
cdef float TWOPI = PI * 2

cdef extern from "Python.h":
    object PyBytes_FromStringAndSize(const char *s, Py_ssize_t len)
    const char* PyBytes_AsString(bytes o)


@cython.cdivision(True)
cpdef torus(float major_radius, float minor_radius, int n_major, int n_minor, tuple material, int shininess=125):
    """
        Torus function from the OpenGL red book.
    """
    glPushAttrib(GL_CURRENT_BIT)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [material[0], material[1], material[2], material[3]])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 1, 1, 1])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

    assert n_major > 0 and n_minor > 0
    assert minor_radius > 0 and major_radius > 0

    cdef float major_s, minor_s
    cdef float a0, a1, x0, y0, x1, y1, b, c, r, z, m, x, y, z2
    cdef int i, j

    with nogil:
        major_s = TWOPI / n_major
        minor_s = TWOPI / n_minor

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

                x = x0 * c
                y = y0 * c
                z2 = z / minor_radius
                m = 1.0 / sqrt(x * x + y * y + z2 * z2)
                glNormal3f(x * m, y * z, z2 * m)
                glVertex3f(x0 * r, y0 * r, z)

                x = x1 * c
                y = y1 * c
                m = 1.0 / sqrt(x * x + y * y + z2 * z2)
                glNormal3f(x * m, y * z, z2 * m)
                glVertex3f(x1 * r, y1 * r, z)

            glEnd()
        glPopAttrib()


@cython.cdivision(True)
cpdef normal_sphere(double r, int divide, GLuint tex, normal, bint lighting=True):
    from texture import pil_load
    print 'Loading normal map: %s...' % normal,
    normal_map = pil_load(normal)
    normal = normal_map.load()
    print 'Loaded'

    cdef int width, height
    width, height = normal_map.size
    cdef bint gray_scale = len(normal[0, 0]) == 1

    glEnable(GL_TEXTURE_2D)
    if lighting:
        glDisable(GL_BLEND)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1, 1, 1, 0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1, 1, 1, 0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 125)
    else:
        glDisable(GL_LIGHTING)
    glBindTexture(GL_TEXTURE_2D, tex)

    cdef double twopi_divide, pi_divide
    cdef int i, j
    cdef double phi1, phi2
    cdef double theta, s, t
    cdef int u, v
    cdef double x, y, z
    cdef double dx, dy, xz
    cdef double nx, ny, nz
    twopi_divide = TWOPI / divide
    pi_divide = PI / divide
    glBegin(GL_TRIANGLE_STRIP)
    for j in xrange(divide + 1):
        phi1 = j * twopi_divide
        phi2 = (j + 1) * twopi_divide

        for i in xrange(divide + 1):
            theta = i * pi_divide

            s = phi2 / TWOPI
            u = min(<int>(s * width), width - 1)
            t = theta / PI
            v = min(<int>(t * height), height - 1)
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
            u = min(<int>(s * width), width - 1)
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
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glEnable(GL_BLEND)


cpdef bytes bgr_to_rgb(bytes buffer, int width, int height, bint alpha=0, bint bottom_up=1):
    cdef int length = len(buffer)
    cdef int depth = length / (width * height)
    cdef int depth2 = depth - alpha
    cdef object final = PyBytes_FromStringAndSize(NULL, length)
    cdef char *result = PyBytes_AsString(final)
    cdef const char *source = PyBytes_AsString(buffer)
    cdef int x, y, ioffset, ooffset, i, row = width * depth
    for y in xrange(height):
        for x in xrange(width):
            ioffset = y * width * depth + x * depth
            ooffset = (height - y - 1 if bottom_up else y) * row + x * depth
            for i in xrange(depth2):
                result[ooffset+i] = source[ioffset+depth2-i-1]
            if alpha:
                result[ooffset+depth2] = source[ioffset+depth2]
    return final
