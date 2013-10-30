import pyglet
import json
import os
import sys
import uuid
import imp

def load_dll(dir, module):
    name = 'punyverse.' + module
    path = os.path.join(dir, 'punyverse', module + '.pyd')
    if not os.path.exists(path):
        path = os.path.join(dir, 'punyverse.%s.pyd' % module)
        if not os.path.exists(path):
            raise ImportError('No module named %s' % module)
    return imp.load_dynamic(name, path)

if __name__ == '__main__':
    try:
        dir = os.path.dirname(sys.executable)
        if sys.frozen == 'windows_exe':
            sys.stderr = open(os.path.join(dir, 'punyverse.log'), 'a')
    except AttributeError:
        sys.exit('This is only meant to be ran frozen.')

    sys.path.insert(0, dir)

    # Model indirectly depends on _glgeom to handle textures
    load_dll(dir, '_glgeom')

    # Model path needs special handling
    _model = load_dll(dir, '_model')
    _model.model_base = os.path.join(dir, 'punyverse', 'assets', 'models')

    with open('punyverse\__main__.py', 'r') as code:
        exec(code)
