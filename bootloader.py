import pyglet
import json
import os
import sys
import uuid

if __name__ == '__main__':
    try:
        dir = os.path.dirname(sys.executable)
        if sys.frozen == 'windows_exe':
            sys.stdout = open(os.path.join(dir, 'punyverse.log'), 'a')
    except AttributeError:
        sys.exit('This is only meant to be ran frozen.')

    sys.path.insert(0, dir)

    import punyverse._model
    import punyverse._glgeom

    with open('punyverse\__main__.py', 'r') as code:
        exec(code)
