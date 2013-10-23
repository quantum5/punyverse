from pyglet.gl import *

VERTICAL = 0
HORIZONTAL = 1


def _progress_bar_vertices(x, y, w, h):
    glColor3f(1, 1, 1)
    glVertex2f(x, y)
    glVertex2f(x + w, y)

    glColor3f(0, 0, 1)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)


def progress_bar(x, y, width, height, progress, min=0, max=100, type=HORIZONTAL):
    glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)

    glLineWidth(1)
    glBegin(GL_LINE_LOOP)
    if type == VERTICAL:
        _progress_bar_vertices(x, y, width, height * max)
    else:
        _progress_bar_vertices(x, y, width * max, height)
    glEnd()
    glBegin(GL_QUADS)
    if type == VERTICAL:
        _progress_bar_vertices(x, y, width, height * progress)
    else:
        _progress_bar_vertices(x, y, width * max, height)
    glEnd()
    glPopAttrib()