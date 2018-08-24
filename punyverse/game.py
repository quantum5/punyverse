#!/usr/bin/python
import os
import time
from math import hypot
from operator import attrgetter
from time import clock

import six

from punyverse import texture
from punyverse.camera import Camera
from punyverse.entity import Asteroid
from punyverse.glgeom import *
from punyverse.world import World

try:
    from punyverse._model import model_list, load_model
except ImportError:
    from punyverse.model import model_list, load_model

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from pyglet.gl import *
from pyglet.window import key, mouse

import pyglet

INITIAL_SPEED = 0  # The initial speed of the player
MOUSE_SENSITIVITY = 0.3  # Mouse sensitivity, 0..1, none...hyperspeed

MAX_DELTA = 5
SEED = int(time.time())


def entity_distance(x0, y0, z0):
    def distance(entity):
        x1, y1, z1 = entity.location
        return hypot(hypot(x1 - x0, y1 - y0), z1 - z0)

    return distance


class Applet(pyglet.window.Window):
    asteroids = ['asteroids/01.obj', 'asteroids/02.obj', 'asteroids/03.obj']

    def __init__(self, *args, **kwargs):
        super(Applet, self).__init__(*args, **kwargs)
        texture.init()

        if hasattr(self.config, '_attribute_names'):
            info = ['  %-22s %s' % (key + ':', value)
                    for key, value in self.config.get_gl_attributes()]
            info = ['%-30s %-30s' % group for group in
                    zip_longest(info[::2], info[1::2], fillvalue='')]
            info = 'OpenGL configuration:\n' + '\n'.join(info)
        else:
            info = 'Unknown OpenGL configuration'

        info = '\n'.join([
            'Graphics Vendor:   ' + gl_info.get_vendor(),
            'Graphics Version:  ' + gl_info.get_version(),
            'Graphics Renderer: ' + gl_info.get_renderer(),
            ]) + '\n\n' + info

        self.loaded = False
        self._loading_phase = pyglet.text.Label(
            font_name='Consolas', font_size=20, x=10, y=self.height - 50,
            color=(255, 255, 255, 255), width=self.width - 20, align='center',
            multiline=True, text='Punyverse is starting...'
        )
        self._loading_label = pyglet.text.Label(
            font_name='Consolas', font_size=16, x=10, y=self.height - 120,
            color=(255, 255, 255, 255), width=self.width - 20, align='center',
            multiline=True
        )
        self._info_label = pyglet.text.Label(
            font_name='Consolas', font_size=13, x=10, y=self.height - 220,
            color=(255, 255, 255, 255), width=self.width - 20,
            multiline=True, text=info
        )
        pyglet.clock.schedule_once(self.load, 0)

    def _load_callback(self, phase, message, progress):
        print(message)
        self.draw_loading(phase, message, progress)
        self.flip()
        self.dispatch_events()

    def load(self, *args, **kwargs):
        start = clock()
        self.fps = 0
        self.world = World('world.json', self._load_callback)
        self._load_callback('Initializing game...', '', 0)
        self.speed = INITIAL_SPEED
        self.keys = set()
        self.info = True
        self.debug = False
        self.orbit = True
        self.running = True
        self.moving = True
        self.info_precise = False
        self.atmosphere = True
        self.cloud = True

        self.tick = self.world.tick_length
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
        self.__time_per_second_cache = None
        self.__time_per_second_value = None
        self.__time_accumulate = 0

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

        for id, file in enumerate(self.asteroids):
            self._load_callback('Loading asteroids...', 'Loading %s...' % file, float(id) / len(self.asteroids))
            Asteroid.load_asteroid(file)

        c = self.cam
        c.x, c.y, c.z = self.world.start
        c.pitch, c.yaw, c.roll = self.world.direction

        self._load_callback('Updating entities...', '', 0)
        for entity in self.world.tracker:
            entity.update()

        print('Loaded in %s seconds.' % (clock() - start))
        self.loaded = True
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
        super(Applet, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def launch_meteor(self):
        c = self.cam
        dx, dy, dz = c.direction()
        speed = abs(self.speed) * 1.1 + 5
        dx *= speed
        dy *= speed
        dz *= speed
        self.world.tracker.append(Asteroid((c.x, c.y - 3, c.z + 5), (dx, dy, dz)))

    def on_mouse_press(self, x, y, button, modifiers):
        self.modifiers = modifiers
        if not self.loaded:
            return

        if not self.exclusive:
            self.set_exclusive_mouse(True)
        else:
            if button in self.mouse_press_handler:
                self.mouse_press_handler[button]()

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.loaded:
            return

        if self.exclusive:  # Only handle camera movement if mouse is grabbed
            self.cam.mouse_move(dx * MOUSE_SENSITIVITY, dy * MOUSE_SENSITIVITY)

    def on_key_press(self, symbol, modifiers):
        self.modifiers = modifiers
        if symbol == key.Q:
            self.screenshot()
        if not self.loaded:
            return
        if self.exclusive:  # Only handle keyboard input if mouse is grabbed
            if symbol in self.key_handler:
                self.key_handler[symbol]()
            else:
                self.keys.add(symbol)

    def on_key_release(self, symbol, modifiers):
        if not self.loaded:
            return

        if symbol in self.keys:
            self.keys.remove(symbol)

    def on_resize(self, width, height):
        if not self.loaded:
            return super(Applet, self).on_resize(width, height)

        height = max(height, 1)  # Prevent / by 0
        self.label.y = height - 20
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # A field of view of 45
        gluPerspective(45.0, width / float(height), 1, 50000000.0)
        glMatrixMode(GL_MODELVIEW)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.loaded:
            return

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
                    collision = entity.collides(c.x, c.y, c.z)
                    if collision:
                        self.speed *= -1
                        c.move(self.speed * 12 * dt)
            else:
                self.__time_accumulate += delta

    def draw_loading(self, phase=None, message=None, progress=None):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        if phase is not None:
            self._loading_phase.text = phase
        if message is not None:
            self._loading_label.text = message
        self._loading_phase.draw()
        self._loading_label.draw()
        if progress is not None:
            progress_bar(10, self.height - 140, self.width - 20, 50, progress)
        self._info_label.draw()

    def on_draw(self):
        if not self.loaded:
            return self.draw_loading()

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
            entity.draw(c, self)

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
            with glRestore(GL_CURRENT_BIT | GL_LINE_BIT):
                glLineWidth(2)
                cx, cy = width / 2, height / 2
                glColor4f(0, 1, 0, 1)
                circle(10, 20, (cx, cy))
            frustrum()
