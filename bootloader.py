import pyglet
import json
import os
import sys
import uuid

def is_frozen():
    import imp
    return (hasattr(sys, 'frozen') or # new py2exe
            hasattr(sys, 'importers') # old py2exe
            or imp.is_frozen('__main__')) # tools/freeze

if __name__ == '__main__':
    if not is_frozen():
        sys.exit('This is only meant to be ran frozen.')

    sys.path.insert(0, os.path.dirname(sys.executable))

    import punyverse._model
    import punyverse._glgeom

    with open('punyverse\__main__.py', 'r') as f:
        code = f.read()
        exec(code)
