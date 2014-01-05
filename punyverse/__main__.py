#!/usr/bin/python
INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700
WIN_TITLE = 'Punyverse'


def main():
    import argparse
    parser = argparse.ArgumentParser(prog='punyverse', description='Python simulator of a puny universe.')
    parser.add_argument('-v', '--no-vsync', help='Disables vsync',
                        action='store_false', dest='vsync')
    args = parser.parse_args()

    import pyglet
    from punyverse import game
    pyglet.options['shadow_window'] = False

    game.Applet(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT,
                caption=WIN_TITLE, resizable=True, vsync=args.vsync)
    pyglet.app.run()


if __name__ == '__main__':
    main()