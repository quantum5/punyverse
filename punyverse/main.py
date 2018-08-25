import argparse

import pyglet

from punyverse.loader import LoaderWindow
from punyverse.ui import Punyverse

INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700


def main():
    parser = argparse.ArgumentParser(prog='punyverse', description='''
            Python simulator of a puny universe.
        ''')
    parser.add_argument('-d', '--high-depth', help='Use a larger depth buffer',
                        const=32, default=24, dest='depth', nargs='?', type=int)
    parser.add_argument('-m', '--multisample', help='Use multisampled image, optional samples',
                        const=2, default=0, nargs='?', type=int)
    parser.add_argument('-v', '--no-vsync', help='Disables vsync',
                        action='store_false', dest='vsync')
    parser.add_argument('-n', '--normal', help='Enables the use of normal maps',
                        action='store_true')
    args = parser.parse_args()

    pyglet.options['shadow_window'] = False
    loader = LoaderWindow(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT,
                          caption='Punyverse is loading...')

    template = pyglet.gl.Config(depth_size=args.depth, double_buffer=True,
                                sample_buffers=args.multisample > 1,
                                samples=args.multisample,
                                major_version=3)

    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screen = display.get_default_screen()
    try:
        config = screen.get_best_config(template)
    except pyglet.window.NoSuchConfigException:
        raise SystemExit('Graphics configuration not supported.')
    else:
        if hasattr(config, '_attribute_names'):
            print('OpenGL configuration:')
            for key in config._attribute_names:
                print('  %-22s %s' % (key + ':', getattr(config, key)))

    punyverse = Punyverse(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT,
                          caption='Punyverse', resizable=True, vsync=args.vsync,
                          config=config, visible=False)

    loader.set_main_context(punyverse.context)
    world = loader.load()
    punyverse.context.set_current()
    punyverse.initialize(world)
    loader.close()
    punyverse.set_visible(True)

    pyglet.app.run()


if __name__ == '__main__':
    main()