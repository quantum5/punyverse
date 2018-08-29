from __future__ import print_function

import os
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.extension import Library

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

if os.name == 'nt':
    gl_libs = ['opengl32']
else:
    gl_libs = ['GL']

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


if os.name == 'nt':
    class SimpleExecutable(Library, object):
        executable_names = set()

        def __init__(self, name, *args, **kwargs):
            super(SimpleExecutable, self).__init__(name, *args, **kwargs)
            self.executable_names.add(name)
            if '.' in name:
                self.executable_names.add(name.split('.')[-1])


    def link_shared_object(
            self, objects, output_libname, output_dir=None, libraries=None,
            library_dirs=None, runtime_library_dirs=None, export_symbols=None,
            debug=0, extra_preargs=None, extra_postargs=None, build_temp=None,
            target_lang=None):
        self.link(
            self.EXECUTABLE, objects, output_libname,
            output_dir, libraries, library_dirs, runtime_library_dirs,
            export_symbols, debug, extra_preargs, extra_postargs,
            build_temp, target_lang
        )

    def make_manifest_get_embed_info(old_func):
        def manifest_get_embed_info(self, target_desc, ld_args):
            temp_manifest, mfid = old_func(target_desc, ld_args)
            if not os.path.exists(temp_manifest):
                return None
            return temp_manifest, mfid
        return manifest_get_embed_info.__get__(old_func.__self__)


    class build_ext_exe(build_ext, object):
        def get_ext_filename(self, fullname):
            ext = self.ext_map[fullname]
            if isinstance(ext, SimpleExecutable):
                return fullname.replace('.', os.sep) + '.exe'
            return super(build_ext_exe, self).get_ext_filename(fullname)

        def get_export_symbols(self, ext):
            if isinstance(ext, SimpleExecutable):
                return ext.export_symbols
            return super(build_ext_exe, self).get_export_symbols(ext)

        def build_extension(self, ext):
            if isinstance(ext, SimpleExecutable):
                old = self.shlib_compiler.link_shared_object
                self.shlib_compiler.link_shared_object = link_shared_object.__get__(self.shlib_compiler)
                patched = False
                if hasattr(self.shlib_compiler, 'manifest_get_embed_info'):
                    self.shlib_compiler.manifest_get_embed_info = \
                        make_manifest_get_embed_info(self.shlib_compiler.manifest_get_embed_info)
                    patched = True
                super(build_ext_exe, self).build_extension(ext)
                self.shlib_compiler.link_shared_object = old
                if patched:
                    del self.shlib_compiler.manifest_get_embed_info
            else:
                super(build_ext_exe, self).build_extension(ext)

    extra_libs = [
        SimpleExecutable('punyverse.launcher', sources=['punyverse/launcher.c'], libraries=['shell32']),
        SimpleExecutable('punyverse.launcherw', sources=['punyverse/launcher.c'],
                         libraries=['shell32'], define_macros=[('GUI', 1)]),
    ]
    build_ext = build_ext_exe
else:
    extra_libs = []


setup(
    name='punyverse',
    version='1.1',
    packages=['punyverse'],
    package_data={
        'punyverse': [
            'world.json',
            'shaders/*.glsl',
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
        Extension('punyverse._glgeom', sources=[pyx_path('punyverse/_glgeom.pyx')], libraries=gl_libs),
    ]) + extra_libs,
    cmdclass={'build_ext': build_ext},

    entry_points={
        'console_scripts': [
            'punyverse = punyverse.main:main',
            'punyverse_make_launcher = punyverse.launcher:main',
            'punyverse_small_images = punyverse.small_images:main',
        ],
        'gui_scripts': [
            'punyversew = punyverse.main:main'
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
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Games/Entertainment :: Simulation',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
