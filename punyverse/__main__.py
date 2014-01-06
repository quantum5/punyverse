#!/usr/bin/python
INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700
WIN_TITLE = 'Punyverse'


def main():
    import argparse
    parser = argparse.ArgumentParser(prog='punyverse', description='''
            Python simulator of a puny universe.
        ''')
    parser.add_argument('-d', '--high-depth', help='Use a larger depth buffer',
                        const=32, default=24, dest='depth', nargs='?', type=int)
    parser.add_argument('-m', '--multisample', help='Use multisampled image, '
                        'optional samples', const=2, default=0, nargs='?',
                        type=int)
    parser.add_argument('-v', '--no-vsync', help='Disables vsync',
                        action='store_false', dest='vsync')
    args = parser.parse_args()

    import pyglet
    pyglet.options['shadow_window'] = False

    template = pyglet.gl.Config(depth_size=args.depth, double_buffer=True,
                                sample_buffers=args.multisample > 1,
                                samples=args.multisample)

    platform = pyglet.window.get_platform()
    display = platform.get_default_display()
    screen = display.get_default_screen()
    try:
        config = screen.get_best_config(template)
    except pyglet.window.NoSuchConfigException:
        raise SystemExit('Graphics configuration not supported.')
    else:
        if hasattr(config, '_attribute_names'):
            print 'OpenGL configuration:'
            for key in config._attribute_names:
                print '  %-17s %s' % (key + ':', getattr(config, key))

    from punyverse import game
    game.Applet(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT,
                caption=WIN_TITLE, resizable=True, vsync=args.vsync,
                config=config)
    pyglet.app.run()


if __name__ == '__main__':
    main()