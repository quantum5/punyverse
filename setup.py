from __future__ import print_function
import sys
import os

from setuptools import setup, Extension

has_pyx = os.path.exists(os.path.join(os.path.dirname(__file__), 'punyverse', '_glgeom.pyx'))

try:
    from Cython.Build import cythonize
except ImportError:
    if has_pyx:
        print('You need to install cython first before installing punyverse.', file=sys.stderr)
        print('Run: pip install cython', file=sys.stderr)
        print('Or if you do not have pip: easy_install cython', file=sys.stderr)
        sys.exit(1)
    cythonize = lambda x: x


if has_pyx:
    pyx_path = lambda x: x
else:
    pyx_path = lambda x: x.replace('.pyx', '.c')


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name='punyverse',
    version='0.3',
    packages=['punyverse'],
    package_data={
        'punyverse': [
            'world.json',
            'assets/textures.txt',
            'assets/textures/*.jpg',
            'assets/textures/*.png',
            'assets/textures/moons/*',
            'assets/models/asteroids/*',
            'assets/models/satellites/*.mtl',
            'assets/models/satellites/*.obj',
            'assets/models/satellites/*.jpg',
            'assets/models/satellites/*.png',
            'assets/models/satellites/cassini/*',
        ],
    },
    ext_modules=cythonize([
        Extension('punyverse._glgeom', sources=[pyx_path('punyverse/_glgeom.pyx')], libraries=['opengl32']),
        Extension('punyverse._model', sources=[pyx_path('punyverse/_model.pyx')], libraries=['opengl32']),
    ]),

    entry_points={
        'console_scripts': [
            'punyverse = punyverse.__main__:main',
            'punyverse_small_images = punyverse.small_images:main',
        ],
        'gui_scripts': [
            'punyversew = punyverse.__main__:main'
        ]

    },
    install_requires=['pyglet', 'Pillow', 'six'],

    author='quantum',
    author_email='quantum2048@gmail.com',
    url='https://github.com/quantum5/punyverse',
    description='Python simulator of a puny universe.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='universe simulator',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
