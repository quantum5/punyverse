from __future__ import print_function

import os.path
import struct
from ctypes import c_int, byref
from io import BytesIO

import six
from pyglet import image
from pyglet.gl import *
from six.moves import range

try:
    from ._glgeom import bgr_to_rgb, flip_vertical
except ImportError:
    import warnings
    warnings.warn('Compile _glgeom.c, or double the start up time.')


    def bgr_to_rgb(source, width, height, alpha=False):
        length = len(source)
        depth = length // (width * height)
        depth2 = depth - alpha
        result = bytearray(length)
        row = width * depth
        for y in range(height):
            for x in range(width):
                offset = y * row + x * depth
                for i in range(depth2):
                    result[offset + i] = source[offset + depth2 - i - 1]
                if alpha:
                    result[offset + depth2] = source[offset + depth2]
        return six.binary_type(result)


    def flip_vertical(source, width, height):
        length = len(source)
        row = length // height
        result = bytearray(length)
        for y1 in range(height):
            y2 = height - y1 - 1
            result[y1 * row:y1 * row + row] = source[y2 * row:y2 * row + row]
        return six.binary_type(result)

__all__ = ['load_texture', 'load_alpha_mask', 'load_image', 'get_best_texture', 'max_texture_size',
           'get_cube_map', 'load_texture_1d']

id = 0
cache = {}


def is_power2(num):
    return num != 0 and ((num & (num - 1)) == 0)


def image_info(data):
    data = six.binary_type(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if size >= 10 and data[:6] in (b'GIF87a', b'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack('<HH', data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif size >= 24 and data.startswith(b'\211PNG\r\n\032\n') and data[12:16] == b'IHDR':
        content_type = 'image/png'
        w, h = struct.unpack('>LL', data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif size >= 16 and data.startswith(b'\211PNG\r\n\032\n'):
        content_type = 'image/png'
        w, h = struct.unpack('>LL', data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif size >= 2 and data.startswith(b'\377\330'):
        content_type = 'image/jpeg'
        jpeg = BytesIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while b and ord(b) != 0xDA:
                while ord(b) != 0xFF:
                    b = jpeg.read(1)
                while ord(b) == 0xFF:
                    b = jpeg.read(1)
                if 0xC0 <= ord(b) <= 0xC3:
                    jpeg.read(3)
                    height, width = struct.unpack('>HH', jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack('>H', jpeg.read(2))[0]) - 2)
                b = jpeg.read(1)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


def glGetInteger(index):
    buf = c_int()
    glGetIntegerv(index, byref(buf))
    return buf.value


def max_texture_size():
    size = glGetInteger(GL_MAX_TEXTURE_SIZE)
    if gl_info.get_vendor() == 'Intel':
        # Intel can't seem to handle more than 4096
        size = min(size, 4096)
    return size


def check_size(width, height):
    max_texture = max_texture_size()

    if width > max_texture or height > max_texture:
        print('too large')
        raise ValueError('Texture too large')
    elif not gl_info.have_version(2) and not gl_info.have_extension('GL_ARB_texture_non_power_of_two'):
        if not is_power2(width) or not is_power2(height):
            print('not power of two')
            raise ValueError('Texture not power of two')


def load_image(file, path):
    print('Loading image %s...' % file, end=' ')

    try:
        file = open(path, 'rb')
    except IOError:
        print('does not exist')
        raise ValueError('Texture does not exist')

    type, width, height = image_info(file.read(65536))
    file.seek(0, 0)
    if type:
        check_size(width, height)

    try:
        raw = image.load(path, file=file)
    except Exception:
        print('cannot be loaded')
        raise ValueError('cannot be loaded')

    width, height = raw.width, raw.height
    check_size(width, height)
    print()

    mode = GL_RGBA if 'A' in raw.format else GL_RGB

    # Flip from BGR to RGB
    if raw.format in ('BGR', 'BGRA'):
        if gl_info.have_extension('GL_EXT_bgra'):
            mode = GL_BGRA if 'A' in raw.format else GL_BGR
            texture = raw.data
        else:
            texture = bgr_to_rgb(raw.data, width, height, 'A' in raw.format)
    elif raw.format in ('RGB', 'RGBA'):
        texture = raw.data
    else:
        texture = raw.get_data('RGBA', width * 4)

    return path, width, height, len(raw.format), mode, flip_vertical(texture, width, height)


def get_file_path(file):
    if os.path.isabs(file):
        path = file
        file = os.path.basename(path)
    else:
        path = os.path.join(os.path.dirname(__file__), 'assets', 'textures', file)
    return path, file


def create_texture():
    buffer = GLuint()
    glGenTextures(1, byref(buffer))
    id = buffer.value
    return id


def delete_texture(id):
    buffer = GLuint(id)
    glDeleteTextures(1, byref(buffer))


def get_internal_mode(mode):
    return {
        GL_RGB: GL_RGB8,
        GL_BGR: GL_RGB8,
        GL_RGBA: GL_RGBA8,
        GL_BGRA: GL_RGBA8,
    }[mode]


def load_texture(file, clamp=False):
    path, file = get_file_path(file)
    if path in cache:
        return cache[path]

    path, width, height, depth, mode, texture = load_image(file, path)

    id = create_texture()
    glBindTexture(GL_TEXTURE_2D, id)

    if gl_info.have_version(3) or gl_info.have_extension('GL_ARB_framebuffer_object'):
        glTexImage2D(GL_TEXTURE_2D, 0, get_internal_mode(mode), width, height, 0, mode, GL_UNSIGNED_BYTE, texture)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        gluBuild2DMipmaps(GL_TEXTURE_2D, depth, width, height, mode, GL_UNSIGNED_BYTE, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    if clamp:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    if gl_info.have_extension('GL_EXT_texture_filter_anisotropic'):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, glGetInteger(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT))

    cache[path] = id
    return id


def load_texture_1d(file, clamp=False):
    path, file = get_file_path(file)
    path, width, height, depth, mode, texture = load_image(file, path)

    id = create_texture()
    glBindTexture(GL_TEXTURE_1D, id)

    if gl_info.have_version(3) or gl_info.have_extension('GL_ARB_framebuffer_object'):
        glTexImage1D(GL_TEXTURE_1D, 0, get_internal_mode(mode), width, 0, mode, GL_UNSIGNED_BYTE, texture)
        glGenerateMipmap(GL_TEXTURE_1D)
    else:
        gluBuild1DMipmaps(GL_TEXTURE_1D, depth, width, mode, GL_UNSIGNED_BYTE, texture)

    if clamp:
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

    if gl_info.have_extension('GL_EXT_texture_filter_anisotropic'):
        glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAX_ANISOTROPY_EXT, glGetInteger(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT))

    return id


def load_alpha_mask(file, clamp=False):
    path, file = get_file_path(file)
    path, width, height, depth, mode, texture = load_image(file, path)

    if depth != 1:
        texture = texture[::depth]

    buffer = GLuint()
    glGenTextures(1, byref(buffer))
    id = buffer.value

    glBindTexture(GL_TEXTURE_2D, id)

    if gl_info.have_version(3) or gl_info.have_extension('GL_ARB_framebuffer_object'):
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R8, width, height, 0, GL_RED, GL_UNSIGNED_BYTE, texture)
        glGenerateMipmap(GL_TEXTURE_2D)
    else:
        gluBuild2DMipmaps(GL_TEXTURE_2D, 1, width, height, GL_RED, GL_UNSIGNED_BYTE, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    if clamp:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    if gl_info.have_extension('GL_EXT_texture_filter_anisotropic'):
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, glGetInteger(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT))

    return id


def get_cube_map(files, callback=None):
    assert len(files) == 6
    callback = callback or (lambda index, file: None)

    id = create_texture()

    glBindTexture(GL_TEXTURE_CUBE_MAP, id)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAX_LEVEL, 0)
    for index, (file, part) in enumerate(zip(files, [
        GL_TEXTURE_CUBE_MAP_POSITIVE_X,
        GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
        GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
        GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
        GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
        GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
    ])):
        try:
            path, file = get_file_path(file)
            callback(index, file)
            path, width, height, depth, mode, texture = load_image(file, path)
        except Exception:
            delete_texture(id)
            raise
        glTexImage2D(part, 0, get_internal_mode(mode), width, height, 0, mode, GL_UNSIGNED_BYTE, texture)

    return id


def get_best_texture(info, loader=load_texture, optional=False, **kwargs):
    if isinstance(info, list):
        for item in info:
            try:
                return loader(item, **kwargs)
            except ValueError:
                pass
    else:
        return loader(info, **kwargs)
    if not optional:
        raise ValueError('No texture found')
