# punyverse [![Linux Build Status](https://img.shields.io/travis/quantum5/punyverse.svg?logo=linux)](https://travis-ci.org/quantum5/punyverse) [![Windows Build Status](https://img.shields.io/appveyor/ci/quantum5/punyverse.svg?logo=windows)](https://ci.appveyor.com/project/quantum5/punyverse) [![PyPI](https://img.shields.io/pypi/v/punyverse.svg)](https://pypi.org/project/punyverse/) [![PyPI - Format](https://img.shields.io/pypi/format/punyverse.svg)](https://pypi.org/project/punyverse/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/punyverse.svg)](https://pypi.org/project/punyverse/)

Python simulator of a puny universe. (How many words can I stick into one?)

![Punyverse Preview](https://guanzhong.ca/assets/projects/punyverse-1.0-7e302d32fb62574e7f7a04acaf9c54e8658821614654280e26e54fab4a840254.png)

## Installation

To install, run `pip install punyverse`.

If you are on Windows, run `punyverse_make_launcher`. This should create special launchers that runs `punyverse` on
your dedicated graphics card, should it exist.

Your graphics card might not support some of the larger textures used by `punyverse`, and so startup might fail.
To solve this problem, run `punyverse_small_images`. It will do nothing if your graphics card supports all the
textures, so when in doubt, run `punyverse_small_images` after installation.

Then, run `punyverse` to launch the simulator, or `punyversew` to launch without the console.

### Summary

```bash
pip install punyverse
punyverse_make_launcher
punyverse_small_images
# Installation finished. Run:
punyverse
```

## Troubleshooting

If `punyverse` does not work, try upgrading your graphics card drivers.

If your graphics card does not appear to support OpenGL 3.3, then you cannot run the latest version of `punyverse`.
You can try `pip install -U punyverse==0.5` to install the last version of `punyverse` to support legacy devices.
You can download the wheels manually from [the PyPI page](https://pypi.org/project/punyverse/0.5/).

If the problem is unrelated to your graphics card, and it persists, try running punyverse under debug mode. To do this,
run `punyverse` as `punyverse --debug`. Then paste the entirety of the output into a new GitHub issue
[here](https://github.com/quantum5/punyverse/issues/new).
