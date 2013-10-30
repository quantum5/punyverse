from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import shutil

sys.argv.append('py2exe')

data = []

parent = os.path.dirname(__file__)
join = os.path.join

resources = [(r'punyverse\assets\textures', ['*.*']),
             (r'punyverse\assets\textures\moons', ['*.*']),
             (r'punyverse\assets\models\asteroids', ['*.obj', '*.mtl']),
             (r'punyverse\assets\models\satellites', ['*.jpg', '*.obj', '*.mtl']),
             (r'punyverse', ['*.py', '*.json', '*.pyx', '*.pxi', '*.pyd'])]

for res in resources:
    dir, patterns = res
    for pattern in patterns:
        for file in glob(join(dir, pattern)):
            data.append((dir, [join(parent, file)]))

setup(
    console=[{'dest_base': 'punyverse_debug', 'script': 'bootloader.py'}, 'small_images.py'],
    windows=[{'dest_base': 'punyverse', 'script': 'bootloader.py'}],
    data_files=data,
    options={'py2exe': {
                'unbuffered': True, 'optimize': 2,
                'excludes': [
                    '_ssl', 'unittest', 'doctest', 'PIL', 'email', 'distutils',
                    'pyglet.window.carbon', 'pyglet.window.xlib',
                    'pyglet.media.drivers.alsa',
                    'win32wnet', 'netbios', 'pgmagick'
                ],
                'dll_excludes': ['MPR.dll', 'w9xpopen.exe'],
              }
            }
)
