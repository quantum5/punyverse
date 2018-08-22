import sys
import os

from pyglet.gl import GLint, glGetIntegerv, GL_MAX_TEXTURE_SIZE
from ctypes import byref

buf = GLint()
glGetIntegerv(GL_MAX_TEXTURE_SIZE, byref(buf))
max_texture = buf.value

del byref, GLint, glGetIntegerv, GL_MAX_TEXTURE_SIZE, buf

def resize(width, height, target):
    factor = (target + .0) / max(width, height)
    return int(width * factor), int(height * factor)

def fits(width, height):
    return width < max_texture and height < max_texture

def make_name(image, suffix):
    name, ext = os.path.splitext(image)
    return '%s_%s%s' % (name, suffix, ext)

try:
    import pgmagick
    
    def get_image(image):
        return pgmagick.Image(image)
    
    def get_size(image):
        size = image.size()
        return size.width(), size.height()
    
    def scale(image, width, height):
        image.filterType(pgmagick.FilterTypes.LanczosFilter)
        image.scale(pgmagick.Geometry(width, height))
        return image
    
    def save(image, file):
        image.write(file)
except ImportError:
    from PIL import Image

    def get_image(image):
        return Image.open(image)

    def get_size(image):
        return image.size

    def scale(image, width, height):
        original_width, original_height = image.size
        if width * 3 < original_width and height * 3 < original_height:
            image = image.resize((width * 2, height * 2))
        return image.resize((width, height), Image.ANTIALIAS)

    def save(image, file):
        image.save(file)

def shrink(file):
    image = get_image(file)
    width, height = get_size(image)
    if fits(width, height):
        print 'no need'
        return
    width, height = resize(width, height, 2048)
    if fits(width, height):
        size = 'medium'
    else:
        width, height = resize(width, height, 1024) # 1024 is minimum
        size = 'small'
    print 'size %s, %dx%d...' % (size, width, height),
    name = make_name(file, size)
    if not os.path.exists(name):
        image = scale(image, width, height)
        print 'saved to:', os.path.basename(name)
        save(image, name)
    else:
        print 'alrady there'

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
        print 'Resizing %s:' % file,
        file = os.path.join(texture, file.replace('/', os.sep))
        if os.path.exists(file):
            shrink(file)
        else:
            print 'exists not'

if __name__ == '__main__':
    main()
