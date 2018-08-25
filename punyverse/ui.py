#!/usr/bin/python
import os
import time
from math import hypot
from operator import attrgetter

import pyglet
import six
from pyglet.gl import *
from pyglet.window import key, mouse

from punyverse.glgeom import *

try:
    from punyverse._model import model_list, load_model
except ImportError:
    from punyverse.model import model_list, load_model

MOUSE_SENSITIVITY = 0.3  # Mouse sensitivity, 0..1, none...hyperspeed

MAX_DELTA = 5
SEED = int(time.time())


def entity_distance(x0, y0, z0):
    def distance(entity):
        x1, y1, z1 = entity.location
        return hypot(hypot(x1 - x0, y1 - y0), z1 - z0)

    return distance


class Punyverse(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(Punyverse, self).__init__(*args, **kwargs)

        self.fps = 0
        self.info = True
        self.debug = False
        self.orbit = True
        self.running = True
        self.moving = True
        self.info_precise = False
        self.atmosphere = True
        self.cloud = True

        self.ticks = [
            1, 2, 5, 10, 20, 40, 60,  # Second range
            120, 300, 600, 1200, 1800, 2700, 3600,  # Minute range
            7200, 14400, 21600, 43200, 86400,  # Hour range
            172800, 432000, 604800,  # 2, 5, 7 days
            1209600, 2592000,  # 2 week, 1 month
            5270400, 7884000, 15768000, 31536000,  # 2, 3, 6, 12 months
            63072000, 157680000, 315360000,  # 2, 5, 10 years
            630720000, 1576800000, 3153600000,  # 20, 50, 100 years
        ]

        self.key_handler = {}
        self.mouse_press_handler = {}

        self.label = pyglet.text.Label('', font_name='Consolas', font_size=12, x=10, y=self.height - 20,
                                       color=(255,) * 4, multiline=True, width=600)
        self.exclusive = False
        self.modifiers = 0

        self.world = None

    def initialize(self, world):
        self.world = world

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
            index = self.ticks.index(self.world.tick_length) + 1
            if index < len(self.ticks):
                self.world.tick_length = self.ticks[index]

        def decrement_tick():
            index = self.ticks.index(self.world.tick_length) - 1
            if index >= 0:
                self.world.tick_length = self.ticks[index]

        self.key_handler = {
            key.ESCAPE: pyglet.app.exit,
            key.NUM_ADD: speed_incrementer(self.world.cam, 1),
            key.NUM_SUBTRACT: speed_incrementer(self.world.cam, -1),
            key.NUM_MULTIPLY: speed_incrementer(self.world.cam, 10),
            key.NUM_DIVIDE: speed_incrementer(self.world.cam, -10),
            key.PAGEUP: speed_incrementer(self.world.cam, 100),
            key.PAGEDOWN: speed_incrementer(self.world.cam, -100),
            key.HOME: speed_incrementer(self.world.cam, 1000),
            key.END: speed_incrementer(self.world.cam, -1000),
            key.R: self.world.cam.reset_roll,
            key.I: attribute_toggler(self, 'info'),
            key.D: attribute_toggler(self, 'debug'),
            key.O: attribute_toggler(self, 'orbit'),
            key.P: attribute_toggler(self, 'info_precise'),
            key.C: attribute_toggler(self, 'cloud'),
            key.X: attribute_toggler(self, 'atmosphere'),
            key.ENTER: attribute_toggler(self, 'running'),
            key.INSERT: increment_tick,
            key.DELETE: decrement_tick,
            key.SPACE: self.world.spawn_asteroid,
            key.E: lambda: self.set_exclusive_mouse(False),
            key.F: lambda: self.set_fullscreen(not self.fullscreen),
        }

        self.mouse_press_handler = {
            mouse.LEFT: self.world.spawn_asteroid,
            mouse.RIGHT: attribute_toggler(self, 'moving'),
        }

        glClearColor(0, 0, 0, 1)
        glClearDepth(1.0)

        glAlphaFunc(GL_GEQUAL, 0.2)
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

        pyglet.clock.schedule(self.update)
        self.on_resize(self.width, self.height)  # On resize handler does nothing unless it's loaded

    def screenshot(self):
        image = pyglet.image.get_buffer_manager().get_color_buffer()
        if hasattr(self, '_hwnd') and not self.modifiers & key.MOD_CTRL:
            from ctypes import windll
            from PIL import Image
            import tempfile
            CF_BITMAP = 2

            image = Image.frombytes(image.format, (image.width, image.height), image.get_image_data().data)
            image = image.convert('RGB').transpose(Image.FLIP_TOP_BOTTOM)
            fd, filename = tempfile.mkstemp('.bmp')
            try:
                with os.fdopen(fd, 'wb') as file:
                    image.save(file, 'BMP')
                if isinstance(filename, six.binary_type):
                    filename = filename.decode('mbcs' if os.name == 'nt' else 'utf8')
                image = windll.user32.LoadImageW(None, filename, 0, 0, 0, 0x10)
                windll.user32.OpenClipboard(self._hwnd)
                windll.user32.EmptyClipboard()
                windll.user32.SetClipboardData(CF_BITMAP, image)
                windll.user32.CloseClipboard()
            finally:
                os.remove(filename)
        else:
            image.save(os.path.expanduser('~/punyverse.png'))

    def set_exclusive_mouse(self, exclusive):
        super(Punyverse, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def on_mouse_press(self, x, y, button, modifiers):
        self.modifiers = modifiers

        if not self.exclusive:
            self.set_exclusive_mouse(True)
        else:
            if button in self.mouse_press_handler:
                self.mouse_press_handler[button]()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:  # Only handle camera movement if mouse is grabbed
            self.world.cam.mouse_move(dx * MOUSE_SENSITIVITY, dy * MOUSE_SENSITIVITY)

    def on_key_press(self, symbol, modifiers):
        self.modifiers = modifiers
        if symbol == key.Q:
            self.screenshot()

        if self.exclusive:  # Only handle keyboard input if mouse is grabbed
            if symbol in self.key_handler:
                self.key_handler[symbol]()
            elif symbol == key.A:
                self.world.cam.roll_left = True
            elif symbol == key.S:
                self.world.cam.roll_right = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.A:
            self.world.cam.roll_left = False
        elif symbol == key.S:
            self.world.cam.roll_right = False

    def on_resize(self, width, height):
        height = max(height, 1)  # Prevent / by 0
        self.label.y = height - 20
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # A field of view of 45
        gluPerspective(45.0, width / float(height), 1, 50000000.0)
        glMatrixMode(GL_MODELVIEW)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.world.cam.speed += scroll_y * 50 + scroll_x * 500

    def get_time_per_second(self):
        time = self.world.tick_length
        unit = 'seconds'
        for size, name in ((60, 'minutes'), (60, 'hours'), (24, 'days'), (365, 'years')):
            if time < size:
                break
            time /= size
            unit = name
        result = '%s %s' % (round(time, 1), unit)
        return result

    def update(self, dt):
        self.world.update(dt, move=self.exclusive and self.moving, tick=self.running)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        c = self.world.cam
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
            entity.draw(self)

        glColor4f(1, 1, 1, 1)
        glDisable(GL_TEXTURE_2D)

        width, height = self.get_size()

        if self.info:
            ortho(width, height)
            if self.info_precise:
                info = ('%d FPS @ (x=%.2f, y=%.2f, z=%.2f) @ %s, %s/s\n'
                        'Direction(pitch=%.2f, yaw=%.2f, roll=%.2f)\nTick: %d' %
                        (pyglet.clock.get_fps(), c.x, c.y, c.z, self.world.cam.speed, self.get_time_per_second(),
                         c.pitch, c.yaw, c.roll, self.world.tick))
            else:
                info = ('%d FPS @ (x=%.2f, y=%.2f, z=%.2f) @ %s, %s/s\n' %
                        (pyglet.clock.get_fps(), c.x, c.y, c.z, self.world.cam.speed, self.get_time_per_second()))
            self.label.text = info
            self.label.draw()
            with glRestore(GL_CURRENT_BIT | GL_LINE_BIT):
                glLineWidth(2)
                cx, cy = width / 2, height / 2
                glColor4f(0, 1, 0, 1)
                circle(10, 20, (cx, cy))
            frustrum()