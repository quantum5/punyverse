from libc.string cimport memcpy

include "_cyopengl.pxi"
cdef float PI = 3.1415926535897932324626
cdef float TWOPI = PI * 2

cdef extern from "Python.h":
    object PyBytes_FromStringAndSize(const char *s, Py_ssize_t len)
    const char* PyBytes_AsString(bytes o)


cpdef bytes bgr_to_rgb(bytes buffer, int width, int height, bint alpha=0):
    cdef int length = len(buffer)
    cdef int depth = length / (width * height)
    cdef int depth2 = depth - alpha
    cdef object final = PyBytes_FromStringAndSize(NULL, length)
    cdef char *result = PyBytes_AsString(final)
    cdef const char *source = PyBytes_AsString(buffer)
    cdef int x, y, offset, i, row = width * depth
    for y in xrange(height):
        for x in xrange(width):
            offset = y * row + x * depth
            for i in xrange(depth2):
                result[offset+i] = source[offset+depth2-i-1]
            if alpha:
                result[offset+depth2] = source[offset+depth2]
    return final


cpdef bytes flip_vertical(bytes buffer, int width, int height):
    cdef int length = len(buffer)
    cdef object final = PyBytes_FromStringAndSize(NULL, length)
    cdef char *result = PyBytes_AsString(final)
    cdef const char *source = PyBytes_AsString(buffer)
    cdef int y1, y2, row = length / height
    for y1 in xrange(height):
        y2 = height - y1 - 1
        memcpy(result + y1 * row, source + y2 * row, row)
    return final
