from __future__ import print_function, division

import os

from PIL import Image

from punyverse.texture import max_texture_size

max_texture = max_texture_size()


def resize(width, height, target):
    factor = target / max(width, height)
    return int(width * factor), int(height * factor)


def fits(width, height):
    return width <= max_texture and height <= max_texture


def make_name(image, suffix):
    name, ext = os.path.splitext(image)
    return '%s_%s%s' % (name, suffix, ext)


def shrink(file):
    image = Image.open(file)
    width, height = image.size

    if fits(width, height):
        print('no need')
        return

    for attempt, new_size in [(4096, 'large'), (2048, 'medium')]:
        width, height = resize(width, height, attempt)
        if fits(width, height):
            size = new_size
            break
    else:
        width, height = resize(width, height, 1024)  # 1024 is minimum
        size = 'small'

    print('size %s, %dx%d...' % (size, width, height), end=' ')
    name = make_name(file, size)
    if not os.path.exists(name):

        original_width, original_height = image.size
        if width * 3 < original_width and height * 3 < original_height:
            image = image.resize((width * 2, height * 2))
        image.resize((width, height), Image.ANTIALIAS).save(name)
        print('saved to:', os.path.basename(name))
    else:
        print('already there')


textures = [
    'mercury.jpg',
    'earth.jpg',
    'moon.jpg',
    'mars.jpg',
    'jupiter.jpg',
    'saturn.jpg',
    'moons/io.jpg',
    'moons/europa.jpg',
    'moons/ganymede.jpg',
    'moons/callisto.jpg',
    'moons/titan.jpg',
    'moons/rhea.jpg',
    'moons/iapetus.jpg',
    'moons/dione.jpg',
    'moons/tethys.jpg',
    'moons/enceladus.jpg',
    'moons/mimas.jpg',
]


def main():
    punyverse = os.path.dirname(__file__)
    try:
        with open(os.path.join(punyverse, 'assets', 'textures.txt')) as f:
            files = [i.strip() for i in f if not i.startswith('#') and i.strip()]
    except IOError:
        files = textures
    texture = os.path.join(punyverse, 'assets', 'textures')
    for file in files:
        print('Resizing %s:' % file, end=' ')
        file = os.path.join(texture, file.replace('/', os.sep))
        if os.path.exists(file):
            shrink(file)
        else:
            print('exists not')


if __name__ == '__main__':
    main()
