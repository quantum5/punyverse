#!/usr/bin/python
INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700
WIN_TITLE = 'Punyverse'


def main():
    try:
        import argparse
    except ImportError:
        args = False
    else:
        parser = argparse.ArgumentParser(prog='punyverse', description='Python simulator of a puny universe.')
        parser.add_argument('-t', '--ticks', help='Ticks per second for game, more means more responsive, but '
                            ' may run slower, default is 20.', default=20, type=int)
        args = parser.parse_args()

    import pyglet
    from punyverse import game
    pyglet.options['shadow_window'] = False
    if args:
        game.TICKS_PER_SECOND = args.ticks

    game.Applet(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT, caption=WIN_TITLE, resizable=True)
    pyglet.app.run()


if __name__ == '__main__':
    main()