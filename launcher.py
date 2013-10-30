from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import shutil

if len(sys.argv) < 2:
    sys.argv.append('py2exe')

parent = os.path.dirname(__file__)
join = os.path.join

setup(
    console=[{'dest_base': 'punyverse_debug', 'script': 'bootloader.py'}, 'small_images.py'],
    windows=[{'dest_base': 'punyverse', 'script': 'bootloader.py'}],
    options={'py2exe': {
                'unbuffered': True, 'optimize': 2,
                'excludes': [
                    '_ssl', 'unittest', 'doctest', 'PIL', 'email', 'distutils',
                    'pyglet.window.carbon', 'pyglet.window.xlib',
                    'pyglet.media.drivers.alsa',
                    'win32wnet', 'netbios', 'pgmagick'
                ],
                'includes': ['punyverse._model', 'punyverse._glgeom'],
                'dll_excludes': ['MPR.dll', 'w9xpopen.exe'],
              }
            }
)
