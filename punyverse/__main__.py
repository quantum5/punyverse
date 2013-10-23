#!/usr/bin/python
INITIAL_WIN_HEIGHT = 540
INITIAL_WIN_WIDTH = 700
WIN_TITLE = "Punyverse"

def main():
    import pyglet
    from punyverse.game import Applet

    pyglet.options['shadow_window'] = False

    Applet(width=INITIAL_WIN_WIDTH, height=INITIAL_WIN_HEIGHT, caption=WIN_TITLE, resizable=True, vsync=0)
    pyglet.app.run()


if __name__ == '__main__':
    main()