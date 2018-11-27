import argparse
import sys

import pyglet

INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700
DEBUG = False


def main():
    macos = sys.platform == 'darwin'

    parser = argparse.ArgumentParser(prog='punyverse', description='''
            Python simulator of a puny universe.
        ''')
    parser.set_defaults(sky=not macos)
    parser.add_argument('-D', '--debug', help='Enable pyglet OpenGL debugging', action='store_true')
    parser.add_argument('-d', '--high-depth', help='Use a larger depth buffer',
                        const=32, default=24, dest='depth', nargs='?', type=int)
    parser.add_argument('-m', '--multisample', help='Use multisampled image, optional samples',
                        const=2, default=0, nargs='?', type=int)
    parser.add_argument('-v', '--no-vsync', help='Disables vsync',
                        action='store_false', dest='vsync')
    parser.add_argument('-n', '--normal', help='Enables the use of normal maps',
                        action='store_true')
    parser.add_argument('-s', '--sky', help='Enables the sky', dest='sky',
                        action='store_true')
    parser.add_argument('-S', '--no-sky', help='Disables the sky', dest='sky',
                        action='store_false')
    args = parser.parse_args()

    versioning = dict(major_version=3, minor_version=3)
    pyglet.options['debug_gl'] = args.debug
    if macos:
        pyglet.options['shadow_window'] = False
        versioning = dict(major_version=4, minor_version=1, forward_compatible=True)

    template = pyglet.gl.Config(depth_size=args.depth, double_buffer=True,
                                sample_buffers=args.multisample > 1,
                                samples=args.multisample, **versioning)

    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screen = display.get_default_screen()
    try:
        config = screen.get_best_config(template)
    except pyglet.window.NoSuchConfigException:
        raise SystemExit('Graphics configuration not supported.')

    create_args = dict(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT,
                       caption='Punyverse', resizable=True, vsync=args.vsync, visible=False)

    from pyglet.gl import gl_info

    from punyverse.loader import LoaderWindow, LoaderConsole
    from punyverse.ui import Punyverse

    if pyglet.compat_platform in ('win32', 'cygwin') and gl_info.get_vendor() == 'Intel':
        # pyglet has some code that tries to create without ARB on Intel.
        # Of course, all that achieves is the message that you can't create OpenGL 3 contexts.
        # So we force create an ARB context.
        from pyglet.gl.win32 import Win32ARBContext
        context = Win32ARBContext(config, None)

        # We use the console loader since using the GUI loader makes all sorts of wonderful things happen on Intel:
        # Access violations, mouse events going nowhere, you name it.
        loader = LoaderConsole()
        punyverse = Punyverse(context=context, **create_args)
    else:
        context = config.create_context(None)
        loader = LoaderWindow(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT,
                              caption='Punyverse is loading...')
        punyverse = Punyverse(context=context, **create_args)
        loader.context.set_current()

    loader.set_main_context(punyverse.context)
    world = loader.load(sky=args.sky)
    punyverse.context.set_current()
    punyverse.initialize(world)
    loader.close()
    punyverse.set_visible(True)
    pyglet.app.run()


if __name__ == '__main__':
    main()
