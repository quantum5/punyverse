punyverse
=========

Python simulator of a puny universe. (How many words can i stick into one?)

Installation
------------

To install, simply clone this repository, or download a copy [here]
(https://github.com/xiaomao5/punyverse/archive/master.zip).

After that, download the [launcher](https://github.com/xiaomao5/punyverse/releases/download/launcher0.3/launcher.exe),
put it into the repository directory and let it unpack in your repository (or copy).

You may start playing any time by running `punyverse.exe`, or `punyverse_debug.exe` if you desire a console.

### A Note on Textures

If your graphics card doesn't support the massive texture sizes this module comes with, you can shrink them.

You can run `small_images.exe` (or `small_images.py`, which requires either `PIL` or `pgmagick`) to generate
smaller versions of shipped textures.

###Advanced Install

You need a C compiler to compile `_model.c` and `_glgeom.c`, both requiring OpenGL headers and libraries.

You will also need to install `pyglet`.

You can now run the `punyverse` module using `python -mpunyverse`.

See above if you run into texture issues.
