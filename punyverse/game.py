#!/usr/bin/python
from operator import attrgetter
import sys

from camera import Camera
from widgets import *

try:
    from _model import *
except ImportError:
    from model import *
from world import *
import texture

try:
    from pyglet.gl import *
    from pyglet.gl.glu import *
    from pyglet.window import key, mouse
    import pyglet
except ImportError:
    print "Pyglet not installed correctly, or at all."
    sys.exit()

from punyverse.glgeom import *
from punyverse import framedata

from math import *
import time
import random
from time import clock

INITIAL_SPEED = 0       # The initial speed of the player
TICKS_PER_SECOND = 20   # How many times to update game per second
MOUSE_SENSITIVITY = 0.3 # Mouse sensitivity, 0..1, none...hyperspeed

MAX_DELTA = 5
SEED = int(time.time())


def entity_distance(x0, y0, z0):
    def distance(entity):
        x1, y1, z1 = entity.location
        return hypot(hypot(x1 - x0, y1 - y0), z1 - z0)

    return distance


class Applet(pyglet.window.Window):
    def update(self, dt):
        cam = self.cam
        if self.exclusive:
            if key.A in self.keys:
                cam.roll += 4
            if key.S in self.keys:
                cam.roll -= 4
            cam.move(0, 0, -self.speed * 128 * 0.003)

        framedata.tick += 1
        for entity in self.world.tracker:
            entity.update()

    def __init__(self, *args, **kwargs):
        super(Applet, self).__init__(*args, **kwargs)
        l = clock()
        self.fps = 0
        self.world = load_world("world.json")
        self.speed = INITIAL_SPEED
        self.keys = set()
        self.info = True
        self.debug = False

        self.label = pyglet.text.Label('', font_name='Consolas', font_size=12, x=10, y=self.height - 20,
                                       color=(255,) * 4, multiline=True, width=600)
        self.cam = Camera()

        self.exclusive = False
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SECOND)

        def update_fps(dt):
            self.fps = pyglet.clock.get_fps()

        pyglet.clock.schedule_interval(update_fps, 1)

        glClearColor(0, 0, 0, 1)
        glClearDepth(1.0)

        texture.init()
        if not texture.badcard:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_POLYGON_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        glAlphaFunc(GL_GEQUAL, 0.9)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)

        glEnable(GL_POLYGON_OFFSET_FILL)

        fv4 = GLfloat * 4

        glLightfv(GL_LIGHT0, GL_POSITION, fv4(.5, .5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, fv4(.5, .5, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, fv4(1, 1, 1, 1))
        glLightfv(GL_LIGHT1, GL_POSITION, fv4(1, 0, .5, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, fv4(.5, .5, .5, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, fv4(1, 1, 1, 1))

        self.asteroid_ids = [model_list(load_model(r"asteroids\01.obj"), 5, 5, 5, (0, 0, 0)),
                             model_list(load_model(r"asteroids\02.obj"), 5, 5, 5, (0, 0, 0)),
                             model_list(load_model(r"asteroids\03.obj"), 5, 5, 5, (0, 0, 0)),
                             model_list(load_model(r"asteroids\04.obj"), 5, 5, 5, (0, 0, 0)),
                             model_list(load_model(r"asteroids\05.obj"), 5, 5, 5, (0, 0, 0))]

        c = self.cam
        c.x, c.y, c.z = self.world.start
        c.pitch, c.yaw, c.roll = self.world.direction

        for entity in self.world.tracker:
            entity.update()

        print "Loaded in %s seconds." % (clock() - l)

    def set_exclusive_mouse(self, exclusive):
        super(Applet, self).set_exclusive_mouse(exclusive) # Pass to parent
        self.exclusive = exclusive # Toggle flag

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.exclusive:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive: # Only handle camera movement if mouse is grabbed
            self.cam.mouse_move(dx * MOUSE_SENSITIVITY, dy * MOUSE_SENSITIVITY)

    def on_key_press(self, symbol, modifiers):
        if self.exclusive: # Only handle keyboard input if mouse is grabbed
            if symbol == key.ESCAPE:
                pyglet.app.exit()
            elif symbol == key.E:
                self.set_exclusive_mouse(False) # Escape mouse
            elif symbol == key.F:
                self.set_fullscreen(not self.fullscreen)
            elif symbol == key.NUM_ADD:
                self.speed += 1
            elif symbol == key.NUM_SUBTRACT:
                self.speed -= 1
            elif symbol == key.NUM_MULTIPLY:
                self.speed += 10
            elif symbol == key.NUM_DIVIDE:
                self.speed -= 10
            elif symbol == key.PAGEUP:
                self.speed += 1000
            elif symbol == key.PAGEDOWN:
                self.speed -= 1000
            elif symbol == key.I:
                self.info = not self.info
            elif symbol == key.D:
                self.debug = not self.debug
            elif symbol == key.Q:
                c = self.cam
                dx, dy, dz = c.direction()
                speed = max(1, abs(self.speed) * 0.6)
                dx *= speed
                dy *= speed
                dz *= speed
                self.world.tracker.append(
                    Asteroid(random.choice(self.asteroid_ids), (c.x, c.y - 3, c.z + 5), direction=(dx, dy, dz)))
            else:
                self.keys.add(symbol)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys:
            self.keys.remove(symbol)

    def on_resize(self, width, height):
        height = max(height, 1) # Prevent / by 0
        self.label.y = height - 20
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # A field of view of 45
        gluPerspective(45.0, width / float(height), 0.1, 50000000.0)
        glMatrixMode(GL_MODELVIEW)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        c = self.cam
        x, y, z = c.x, c.y, c.z
        glRotatef(c.pitch, 1, 0, 0)
        glRotatef(c.yaw, 0, 1, 0)
        glRotatef(c.roll, 0, 0, 1)
        glTranslatef(-x, -y, -z)

        glEnable(GL_LIGHTING)
        glEnable(GL_BLEND)
        world = self.world
        if x != world.x or y != world.y or z != world.z:
            world.tracker.sort(key=entity_distance(x, y, z), reverse=True)
            world.tracker.sort(key=attrgetter('background'), reverse=True)
            world.x, world.y, world.z = x, y, z

        for entity in world.tracker:
            x, y, z = entity.location
            pitch, yaw, roll = entity.rotation

            glPushMatrix()
            glTranslatef(x, y, z)
            glRotatef(pitch, 1, 0, 0)
            glRotatef(yaw, 0, 1, 0)
            glRotatef(roll, 0, 0, 1)
            glPushAttrib(GL_CURRENT_BIT)
            glCallList(entity.id)
            if self.debug:
                glPushMatrix()
                glLineWidth(0.25)
                glPolygonOffset(1, 1)
                glDisable(GL_LIGHTING)
                glDisable(GL_TEXTURE_2D)
                glColor3f(0, 1, 0)
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glCallList(entity.id)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glEnable(GL_LIGHTING)
                glEnable(GL_TEXTURE_2D)
                glPopMatrix()
            glPopAttrib()
            glPopMatrix()

            if hasattr(entity, 'atmosphere') and entity.atmosphere:
                glPushMatrix()
                x0, y0, z0 = entity.location
                dx, dy, dz = x - x0, y - y0, z - z0

                distance = sqrt(dz * dz + dx * dx)
                pitch = (360 - degrees(atan2(dy, distance)))
                yaw = degrees(atan2(dx, dz))

                glTranslatef(x0, y0, z0)
                glRotatef(pitch, 1, 0, 0)
                glRotatef(yaw, 0, 1, 0)
                glCallList(entity.atmosphere)
                glPopMatrix()

            if hasattr(entity, "cloudmap") and entity.cloudmap:
                glPushMatrix()
                glEnable(GL_ALPHA_TEST)
                glTranslatef(*entity.location)
                pitch, yaw, roll = entity.rotation
                glRotatef(pitch, 1, 0, 0)
                glRotatef(yaw, 0, 1, 0)
                glRotatef(roll, 0, 0, 1)
                glCallList(entity.cloudmap)
                glDisable(GL_ALPHA_TEST)
                glPopMatrix()

        glColor4f(1, 1, 1, 1)
        glDisable(GL_TEXTURE_2D)

        width, height = self.get_size()

        if self.info:
            ortho(width, height)

            self.label.text = ('%d FPS @ (x=%.2f, y=%.2f, z=%.2f) @ %s\n'
                               'Direction(pitch=%.2f, yaw=%.2f, roll=%.2f)') % (
                self.fps, c.x, c.y, c.z, self.speed, c.pitch, c.yaw, c.roll)
            self.label.draw()

            glPushAttrib(GL_CURRENT_BIT | GL_LINE_BIT)

            glLineWidth(2)

            cx, cy = width / 2, height / 2

            glColor3f(0, 0, 1)
            crosshair(15, (cx, cy))
            glColor4f(0, 1, 0, 1)
            circle(20, 30, (cx, cy))
            glPopAttrib()

            frustrum()
