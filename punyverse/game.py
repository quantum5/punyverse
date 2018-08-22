#!/usr/bin/python
from operator import attrgetter
from math import hypot, sqrt, atan2, degrees
from time import clock
from itertools import izip_longest
import time
import random
import os

from punyverse.camera import Camera
from punyverse.world import World
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
        self.world_options = kwargs.pop('world_options', {})

        super(Applet, self).__init__(*args, **kwargs)
        texture.init()

        if hasattr(self.config, '_attribute_names'):
            info = ['  %-22s %s' % (key + ':', getattr(self.config, key))
                    for key in self.config._attribute_names]
            info = ['%-30s %-30s' % group for group in
                    izip_longest(info[::2], info[1::2], fillvalue='')]
            info = 'OpenGL configuration:\n' + '\n'.join(info)
        else:
            info = 'Unknown OpenGL configuration'

        self.loaded = False
        self.__load_started = False
        self._loading_phase = pyglet.text.Label(
            font_name='Consolas', font_size=20, x=10, y=self.height - 80,
            color=(255, 255, 255, 255), width=self.width - 20, align='center',
            multiline=True, text='Punyverse is starting...'
        )
        self._loading_label = pyglet.text.Label(
            font_name='Consolas', font_size=16, x=10, y=self.height - 150,
            color=(255, 255, 255, 255), width=self.width - 20, align='center',
            multiline=True
        )
        self._info_label = pyglet.text.Label(
            font_name='Consolas', font_size=13, x=10, y=self.height - 250,
            color=(255, 255, 255, 255), width=self.width - 20,
            multiline=True, text=info
        )
        pyglet.clock.schedule_once(self.load, 0)

    def load(self, *args, **kwargs):
        if self.loaded or self.__load_started:
            return

        self.__load_started = True

        def callback(phase, message, progress):
            self.draw_loading(phase, message, progress)
            self.flip()
            self.dispatch_events()

        start = clock()
        self.fps = 0
        self.world = World('world.json', callback, self.world_options)
        phase = 'Initializing game...'
        print phase
        callback(phase, '', 0)
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
            #key.Q: self.screenshot,
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
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  fv4(1, 1, 1, 1))
        glLightfv(GL_LIGHT1, GL_POSITION, fv4(1, 0, .5, 0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  fv4(.5, .5, .5, 1))
        glLightfv(GL_LIGHT1, GL_SPECULAR, fv4(1, 1, 1, 1))

        phase = 'Loading asteroids...'
        print phase

        def load_asteroids(files):
            for id, file in enumerate(files):
                callback(phase, 'Loading %s...' % file, float(id) / len(files))
                yield model_list(load_model(file), 5, 5, 5, (0, 0, 0))

        self.asteroid_ids = list(load_asteroids([r'asteroids/01.obj', r'asteroids/02.obj', r'asteroids/03.obj']))

        c = self.cam
        c.x, c.y, c.z = self.world.start
        c.pitch, c.yaw, c.roll = self.world.direction

        phase = 'Updating entities...'
        print phase
        callback(phase, '', 0)
        for entity in self.world.tracker:
            entity.update()

        print 'Loaded in %s seconds.' % (clock() - start)
        self.loaded = True
        pyglet.clock.schedule(self.update)
        self.on_resize(self.width, self.height)  # On resize handler does nothing unless it's loaded

    def screenshot(self):
        image = pyglet.image.get_buffer_manager().get_color_buffer()
        if hasattr(self, '_hwnd') and not self.modifiers & key.MOD_CTRL:
            from ctypes import windll, cdll
            from PIL import Image
            import tempfile
            CF_BITMAP = 2
            
            image = Image.fromstring(image.format, (image.width, image.height), image.get_image_data().data)
            image = image.convert('RGB').transpose(Image.FLIP_TOP_BOTTOM)
            fd, filename = tempfile.mkstemp('.bmp')
            try:
                with os.fdopen(fd, 'w') as file:
                    image.save(file, 'BMP')
                if not isinstance(filename, unicode):
                    filename = filename.decode('mbcs')
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
        self.world.tracker.append(Asteroid(random.choice(self.asteroid_ids), (c.x, c.y - 3, c.z + 5),
                                           direction=(dx, dy, dz)))

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

        height = max(height, 1) # Prevent / by 0
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
            progress_bar(10, self.height - 170, self.width - 20, 50, progress)
        self._info_label.draw()

    def on_draw(self, glMatrixBuffer=GLfloat * 16):
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
            x, y, z = entity.location
            pitch, yaw, roll = entity.rotation

            with glMatrix(), glRestore(GL_CURRENT_BIT):
                if entity.background:
                    glTranslatef(c.x, c.y, c.z)
                else:
                    glTranslatef(x, y, z)
                glRotatef(pitch, 1, 0, 0)
                glRotatef(yaw, 0, 1, 0)
                glRotatef(roll, 0, 0, 1)
                glCallList(entity.id)
                if self.debug:
                    with glMatrix(), glRestore(GL_ENABLE_BIT | GL_POLYGON_BIT | GL_LINE_BIT):
                        glLineWidth(0.25)
                        glPolygonOffset(1, 1)
                        glDisable(GL_LIGHTING)
                        glDisable(GL_TEXTURE_2D)
                        glColor3f(0, 1, 0)
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                        glCallList(entity.id)

            has_corona = hasattr(entity, 'corona') and entity.corona
            has_atmosphere = hasattr(entity, 'atmosphere') and entity.atmosphere
            if self.atmosphere and (has_corona or has_atmosphere):
                with glMatrix(), glRestore(GL_ENABLE_BIT):
                    x0, y0, z0 = entity.location
                    glTranslatef(x0, y0, z0)
                    matrix = glMatrixBuffer()
                    glGetFloatv(GL_MODELVIEW_MATRIX, matrix)
                    matrix[0: 3] = [1, 0, 0]
                    matrix[4: 7] = [0, 1, 0]
                    matrix[8:11] = [0, 0, 1]
                    glLoadMatrixf(matrix)
                    glEnable(GL_BLEND)
                    if has_atmosphere:
                        glCallList(entity.atmosphere)
                    if has_corona:
                        x, y, z = c.direction()
                        glTranslatef(-x, -y, -z)
                        glCallList(entity.corona)

            if self.cloud and hasattr(entity, 'cloudmap') and entity.cloudmap:
                with glMatrix(), glRestore(GL_ENABLE_BIT):
                    glEnable(GL_BLEND)
                    glEnable(GL_ALPHA_TEST)
                    glTranslatef(*entity.location)
                    pitch, yaw, roll = entity.rotation
                    glRotatef(pitch, 1, 0, 0)
                    glRotatef(yaw, 0, 1, 0)
                    glRotatef(roll, 0, 0, 1)
                    glCallList(entity.cloudmap)

            if self.orbit and hasattr(entity, 'get_orbit') and hasattr(entity, 'parent'):
                parent = entity.parent
                distance = get_distance(parent)
                if distance < parent.orbit_show:
                    with glMatrix(), glRestore(GL_ENABLE_BIT | GL_LINE_BIT | GL_CURRENT_BIT):
                        glTranslatef(*entity.parent.location)
                        glDisable(GL_LIGHTING)
                        solid = distance < parent.orbit_opaque
                        glColor4f(1, 1, 1, 1 if solid else
                                  (1 - (distance - parent.orbit_opaque) / parent.orbit_blend))
                        if not solid:
                            glEnable(GL_BLEND)
                        glLineWidth(1)
                        glCallList(entity.get_orbit())

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
