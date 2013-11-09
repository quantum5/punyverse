#!/usr/bin/python
from operator import attrgetter
from math import hypot, sqrt, atan2, degrees
from time import clock
import time
import random

from punyverse.camera import Camera
from punyverse.world import load_world
from punyverse.glgeom import *
from punyverse.entity import Asteroid
from punyverse import texture

try:
    from punyverse._model import model_list, load_model
except ImportError:
    from punyverse.model import model_list, load_model

from pyglet.gl import *
from pyglet.window import key, mouse

import pyglet


INITIAL_SPEED = 0        # The initial speed of the player
MOUSE_SENSITIVITY = 0.3  # Mouse sensitivity, 0..1, none...hyperspeed

MAX_DELTA = 5
SEED = int(time.time())


def entity_distance(x0, y0, z0):
    def distance(entity):
        x1, y1, z1 = entity.location
        return hypot(hypot(x1 - x0, y1 - y0), z1 - z0)

    return distance


class Applet(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Applet, self).__init__(*args, **kwargs)
        texture.init()

        start = clock()
        self.fps = 0
        self.world = load_world('world.json')
        print 'Initializing game...'
        self.speed = INITIAL_SPEED
        self.keys = set()
        self.info = True
        self.debug = False
        self.orbit = True
        self.running = True
        self.moving = True
        self.info_precise = False
        self.atmosphere = True
        self.cloud = not texture.badcard

        self.tick = self.world.tick_length
        self.ticks = [1, 2, 5, 10, 20, 40, 60,                # Second range
                      120, 300, 600, 1200, 1800, 2700, 3600,  # Minute range
                      7200, 14400, 21600, 43200, 86400,       # Hour range
                      172800, 432000, 604800,                 # 2, 5, 7 days
                      1209600, 2592000,                       # 2 week, 1 month
                      5270400, 7884000, 15768000, 31536000,   # 2, 3, 6, 12 months
                      63072000, 157680000, 315360000,         # 2, 5, 10 years
                      630720000, 1576800000, 3153600000,      # 20, 50, 100 years
        ]
        self.__time_per_second_cache = None
        self.__time_per_second_value = None
        self.__time_accumulate = 0
        pyglet.clock.schedule(self.update)

        def speed_incrementer(object, increment):
            def incrementer():
                object.speed += increment

            return incrementer

        def attribute_toggler(object, attribute):
            getter = attrgetter(attribute)

            def toggler():
                setattr(object, attribute, not getter(object))

            return toggler

        def increment_tick():
            index = self.ticks.index(self.tick) + 1
            if index < len(self.ticks):
                self.tick = self.ticks[index]

        def decrement_tick():
            index = self.ticks.index(self.tick) - 1
            if index >= 0:
                self.tick = self.ticks[index]

        self.key_handler = {
            key.ESCAPE: pyglet.app.exit,
            key.NUM_ADD: speed_incrementer(self, 1),
            key.NUM_SUBTRACT: speed_incrementer(self, -1),
            key.NUM_MULTIPLY: speed_incrementer(self, 10),
            key.NUM_DIVIDE: speed_incrementer(self, -10),
            key.PAGEUP: speed_incrementer(self, 100),
            key.PAGEDOWN: speed_incrementer(self, -100),
            key.HOME: speed_incrementer(self, 1000),
            key.END: speed_incrementer(self, -1000),
            key.R: lambda: setattr(self.cam, 'roll', 0),
            key.I: attribute_toggler(self, 'info'),
            key.D: attribute_toggler(self, 'debug'),
            key.O: attribute_toggler(self, 'orbit'),
            key.P: attribute_toggler(self, 'info_precise'),
            key.C: attribute_toggler(self, 'cloud'),
            key.X: attribute_toggler(self, 'atmosphere'),
            key.ENTER: attribute_toggler(self, 'running'),
            key.INSERT: increment_tick,
            key.DELETE: decrement_tick,
            key.SPACE: self.launch_meteor,
            key.E: lambda: self.set_exclusive_mouse(False),
            key.F: lambda: self.set_fullscreen(not self.fullscreen),
        }

        self.mouse_press_handler = {
            mouse.LEFT: self.launch_meteor,
            mouse.RIGHT: attribute_toggler(self, 'moving'),
        }

        self.label = pyglet.text.Label('', font_name='Consolas', font_size=12, x=10, y=self.height - 20,
                                       color=(255,) * 4, multiline=True, width=600)
        self.cam = Camera()

        self.exclusive = False

        glClearColor(0, 0, 0, 1)
        glClearDepth(1.0)

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

        print 'Loading asteroids...'
        self.asteroid_ids = [model_list(load_model(r'asteroids/01.obj'), 5, 5, 5, (0, 0, 0)),
                             model_list(load_model(r'asteroids/02.obj'), 5, 5, 5, (0, 0, 0)),
                             model_list(load_model(r'asteroids/03.obj'), 5, 5, 5, (0, 0, 0)),
        ]

        c = self.cam
        c.x, c.y, c.z = self.world.start
        c.pitch, c.yaw, c.roll = self.world.direction

        print 'Updating entities...'
        for entity in self.world.tracker:
            entity.update()

        print 'Loaded in %s seconds.' % (clock() - start)

    def set_exclusive_mouse(self, exclusive):
        super(Applet, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def launch_meteor(self):
        c = self.cam
        dx, dy, dz = c.direction()
        speed = abs(self.speed) * 1.1 + 5
        dx *= speed
        dy *= speed
        dz *= speed
        self.world.tracker.append(Asteroid(random.choice(self.asteroid_ids), (c.x, c.y - 3, c.z + 5),
                                           direction=(dx, dy, dz)))

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.exclusive:
            self.set_exclusive_mouse(True)
        else:
            if button in self.mouse_press_handler:
                self.mouse_press_handler[button]()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:  # Only handle camera movement if mouse is grabbed
            self.cam.mouse_move(dx * MOUSE_SENSITIVITY, dy * MOUSE_SENSITIVITY)

    def on_key_press(self, symbol, modifiers):
        if self.exclusive:  # Only handle keyboard input if mouse is grabbed
            if symbol in self.key_handler:
                self.key_handler[symbol]()
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

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.speed += scroll_y * 50 + scroll_x * 500

    def get_time_per_second(self):
        if self.__time_per_second_cache == self.tick:
            return self.__time_per_second_value
        time = self.tick + .0
        unit = 'seconds'
        for size, name in ((60, 'minutes'), (60, 'hours'), (24, 'days'), (365, 'years')):
            if time < size:
                break
            time /= size
            unit = name
        result = '%s %s' % (round(time, 1), unit)
        self.__time_per_second_cache = self.tick
        self.__time_per_second_value = result
        return result

    def update(self, dt):
        c = self.cam

        if self.exclusive:
            if key.A in self.keys:
                c.roll += 4 * dt * 10
            if key.S in self.keys:
                c.roll -= 4 * dt * 10
            if self.moving:
                c.move(self.speed * 10 * dt)

        if self.running:
            delta = self.tick * dt
            update = int(delta + self.__time_accumulate + 0.5)
            if update:
                self.__time_accumulate = 0
                self.world.tick += update
                for entity in self.world.tracker:
                    entity.update()
            else:
                self.__time_accumulate += delta

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
        world = self.world
        get_distance = entity_distance(x, y, z)
        if x != world.x or y != world.y or z != world.z:
            world.tracker.sort(key=get_distance, reverse=True)
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

            has_corona = hasattr(entity, 'corona') and entity.corona
            has_atmosphere = hasattr(entity, 'atmosphere') and entity.atmosphere
            if self.atmosphere and (has_corona or has_atmosphere):
                glPushMatrix()
                x0, y0, z0 = entity.location
                dx, dy, dz = x - x0, y - y0, z - z0

                distance = sqrt(dz * dz + dx * dx)
                pitch = (360 - degrees(atan2(dy, distance)))
                yaw = degrees(atan2(dx, dz))

                glTranslatef(x0, y0, z0)
                glRotatef(pitch, 1, 0, 0)
                glRotatef(yaw, 0, 1, 0)
                if has_atmosphere:
                    glCallList(entity.atmosphere)
                if has_corona:
                    x, y, z = c.direction()
                    glTranslatef(-x, -y, -z)
                    glCallList(entity.corona)
                glPopMatrix()

            if self.cloud and hasattr(entity, 'cloudmap') and entity.cloudmap:
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

            if self.orbit and hasattr(entity, 'get_orbit') and hasattr(entity, 'parent'):
                parent = entity.parent
                distance = get_distance(parent)
                if distance < parent.orbit_show:
                    glPushMatrix()
                    glTranslatef(*entity.parent.location)
                    glDisable(GL_LIGHTING)
                    glPushAttrib(GL_LINE_BIT | GL_CURRENT_BIT)
                    glColor4f(1, 1, 1, 1 if distance < parent.orbit_opaque else
                              (1 - (distance - parent.orbit_opaque) / parent.orbit_blend))
                    glLineWidth(1)
                    glCallList(entity.get_orbit())
                    glPopAttrib()
                    glEnable(GL_LIGHTING)
                    glPopMatrix()

        glColor4f(1, 1, 1, 1)
        glDisable(GL_TEXTURE_2D)

        width, height = self.get_size()

        if self.info:
            ortho(width, height)

            if self.info_precise:
                info = ('%d FPS @ (x=%.2f, y=%.2f, z=%.2f) @ %s, %s/s\n'
                        'Direction(pitch=%.2f, yaw=%.2f, roll=%.2f)\nTick: %d' %
                        (pyglet.clock.get_fps(), c.x, c.y, c.z, self.speed, self.get_time_per_second(),
                         c.pitch, c.yaw, c.roll, self.world.tick))
            else:
                info = ('%d FPS @ (x=%.2f, y=%.2f, z=%.2f) @ %s, %s/s\n' %
                        (pyglet.clock.get_fps(), c.x, c.y, c.z, self.speed, self.get_time_per_second()))
            self.label.text = info
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
