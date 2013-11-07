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

You can run `small_images.exe` (or `small_images.py`, if you have python) to generate smaller versions of
shipped textures, which requires either `PIL` or `pgmagick` to process the images.

### Advanced Install

If you wish to use your own python installation, to run `punyverse`, you can clone the code.
Here are the things you need:

* Python 2.7, I have no Python 2.6 install to test this.
* a C compiler to compile `_model.c` and `_glgeom.c`
  * requires OpenGL headers and libraries.
  * not really necessary, but it runs way faster with these.
* install `pyglet`

After getting the dependencies done, you can now run the `punyverse` module using `python -mpunyverse`.

See above if you run into texture issues.
