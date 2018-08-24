import time

import pyglet
from pyglet.gl import *
from six.moves import zip_longest

from punyverse.glgeom import glContext, progress_bar
from punyverse.world import World


class LoaderWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(LoaderWindow, self).__init__(*args, **kwargs)

        self.loading_phase = pyglet.text.Label(
            font_name='Consolas', font_size=20, x=10, y=self.height - 50,
            color=(255, 255, 255, 255), width=self.width - 20, align='center',
            multiline=True, text='Punyverse is starting...'
        )
        self.loading_label = pyglet.text.Label(
            font_name='Consolas', font_size=16, x=10, y=self.height - 120,
            color=(255, 255, 255, 255), width=self.width - 20, align='center',
            multiline=True
        )
        self.info_label = pyglet.text.Label(
            font_name='Consolas', font_size=13, x=10, y=self.height - 220,
            color=(255, 255, 255, 255), width=self.width - 20,
            multiline=True
        )
        self.progress = 0

        self._main_context = None

    def set_main_context(self, context):
        self._main_context = context

        info = ['  %-22s %s' % (key + ':', value)
                for key, value in context.config.get_gl_attributes()]
        info = ['%-30s %-30s' % group for group in
                zip_longest(info[::2], info[1::2], fillvalue='')]

        with glContext(context):
            self.info_label.text = '\n'.join([
                'Graphics Vendor:   ' + gl_info.get_vendor(),
                'Graphics Version:  ' + gl_info.get_version(),
                'Graphics Renderer: ' + gl_info.get_renderer(),
            ]) + '\n\n' + 'OpenGL configuration:\n' + '\n'.join(info)

    def _load_callback(self, phase, message, progress):
        print(message)
        with glContext(self.context):
            self.loading_phase.text = phase
            self.loading_label.text = message
            self.progress = progress

            self.on_draw()
            self.flip()
            self.dispatch_events()

    def load(self):
        start = time.clock()
        with glContext(self._main_context):
            world = World('world.json', self._load_callback)
        print('Loaded in %s seconds.' % (time.clock() - start))
        return world

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        self.loading_phase.draw()
        self.loading_label.draw()
        progress_bar(10, self.height - 140, self.width - 20, 50, self.progress)
        self.info_label.draw()

    def main_is_initializing(self):
        self._load_callback('Loading main window...', '', 0)
