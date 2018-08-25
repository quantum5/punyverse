import bz2
import gzip
import os
import zipfile
from uuid import uuid4

import six
from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range, zip

from punyverse.texture import load_texture


def zip_open(file):
    zip = zipfile.ZipFile(file)
    return zip.open(zip.namelist()[0])

openers = {
    'gz': gzip.open,
    'bz2': bz2.BZ2File,
    'zip': zip_open,
}


class Face(object):
    __slots__ = ('verts', 'norms', 'texs', 'size')

    def __init__(self, verts, norms, texs):
        self.verts = verts
        self.norms = norms
        self.texs = texs
        self.size = len(verts)


class Material(object):
    __slots__ = ('name', 'texture', 'Ka', 'Kd', 'Ks', 'shininess')

    def __init__(self, name, texture=None, Ka=(0, 0, 0), Kd=(0, 0, 0), Ks=(0, 0, 0), shininess=0.0):
        self.name = name
        self.texture = texture
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.shininess = shininess


class Group(object):
    __slots__ = ('name', 'material', 'faces')

    def __init__(self, name=None):
        if name is None:
            self.name = str(uuid4())
        else:
            self.name = name
        self.material = None
        self.faces = []


class WavefrontObject(object):
    def __init__(self, path):
        self.path = path
        self.root = os.path.abspath(os.path.dirname(path))
        self.vertices = []
        self.normals = []
        self.textures = []
        self.groups = []
        self.materials = {}

        self.perform_io(self.path)

    def new_material(self, words):
        name = words[1].decode('utf-8')
        material = Material(name)
        self.materials[name] = material
        self.current_material = material

    def Ka(self, words):
        self.current_material.Ka = (float(words[1]), float(words[2]), float(words[3]))

    def Kd(self, words):
        self.current_material.Kd = (float(words[1]), float(words[2]), float(words[3]))

    def Ks(self, words):
        self.current_material.Ks = (float(words[1]), float(words[2]), float(words[3]))

    def material_shininess(self, words):
        self.current_material.shininess = min(float(words[1]), 125)

    def material_texture(self, words):
        self.current_material.texture = words[-1].decode('utf-8')

    def vertex(self, words):
        self.vertices.append((float(words[1]), float(words[2]), float(words[3])))

    def normal(self, words):
        self.normals.append((float(words[1]), float(words[2]), float(words[3])))

    def texture(self, words):
        l = len(words)
        x, y, z = 0, 0, 0
        if l >= 2:
            x = float(words[1])
        if l >= 3:
            # OBJ origin is at upper left, OpenGL origin is at lower left
            y = 1 - float(words[2])
        if l >= 4:
            z = float(words[3])
        self.textures.append((x, y, z))

    def face(self, words):
        l = len(words)
        vertex_count = l - 1

        vindices = []
        nindices = []
        tindices = []

        for i in range(1, vertex_count + 1):
            raw_faces = words[i].split(b'/')
            l = len(raw_faces)

            vindices.append(int(raw_faces[0]) - 1)

            if l >= 2 and raw_faces[1]:
                tindices.append(int(raw_faces[1]) - 1)
            else:
                tindices.append(None)

            if l >= 3 and raw_faces[2]:
                nindices.append(int(raw_faces[2]) - 1)
            else:
                nindices.append(None)

        if self.current_group is None:
            self.current_group = group = Group()
            self.groups.append(group)
        else:
            group = self.current_group

        group.faces.append(Face(vindices, nindices, tindices))

    def material(self, words):
        self.perform_io(os.path.join(self.root, words[1].decode('utf-8')))

    def use_material(self, words):
        mat = words[1].decode('utf-8')
        try:
            self.current_group.material = self.materials[mat]
        except KeyError:
            print("Warning: material %s undefined, only %s defined." % (mat, self.materials))
        except AttributeError:
            print("Warning: no group")

    def group(self, words):
        group = Group(words[1].decode('utf-8'))
        self.groups.append(group)
        self.current_group = group

    def perform_io(self, file):
        ext = os.path.splitext(file)[1].lstrip('.')
        reader = openers.get(ext, lambda x: open(x, 'rb'))(file)

        dispatcher = {
            b'v': self.vertex,
            b'vn': self.normal,
            b'vt': self.texture,
            b'f': self.face,
            b'mtllib': self.material,
            b'usemtl': self.use_material,
            b'g': self.group,
            b'o': self.group,
            b'newmtl': self.new_material,
            b'Ka': self.Ka,
            b'Kd': self.Kd,
            b'Ks': self.Ks,
            b'Ns': self.material_shininess,
            b'map_Kd': self.material_texture,
        }
        default = lambda words: None

        with reader:
            for buf in reader:
                if not buf or buf.startswith((b'\r', b'\n', b'#')):
                    continue # Empty or comment
                words = buf.split()
                type = words[0]

                dispatcher.get(type, default)(words)
        return True


model_base = os.path.join(os.path.dirname(__file__), 'assets', 'models')


def load_model(path):
    if not os.path.isabs(path):
        path = os.path.join(model_base, path)
    if isinstance(path, six.binary_type):
        path = path.decode('mbcs' if os.name == 'nt' else 'utf8')
    return WavefrontObject(path)


def model_list(model, sx=1, sy=1, sz=1, rotation=(0, 0, 0)):
    for m, text in six.iteritems(model.materials):
        if text.texture:
            load_texture(os.path.join(model.root, text.texture))

    display = glGenLists(1)

    glNewList(display, GL_COMPILE)
    glPushMatrix()
    glPushAttrib(GL_CURRENT_BIT)

    pitch, yaw, roll = rotation
    glPushAttrib(GL_TRANSFORM_BIT)
    glRotatef(pitch, 1, 0, 0)
    glRotatef(yaw, 0, 1, 0)
    glRotatef(roll, 0, 0, 1)
    glPopAttrib()

    vertices = model.vertices
    textures = model.textures
    normals = model.normals

    for g in model.groups:
        material = g.material

        tex_id = load_texture(os.path.join(model.root, material.texture)) if (material and material.texture) else 0

        if tex_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
        else:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

        if material:
            fv4 = GLfloat * 4

            if material.Ka:
                kx, ky, kz = material.Ka
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, fv4(kx, ky, kz, 1))
            if material.Kd:
                kx, ky, kz = material.Kd
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, fv4(kx, ky, kz, 1))
            if material.Ks:
                kx, ky, kz = material.Ks
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(kx, ky, kz, 1))
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material.shininess)

        def point(f, n, max_texture=len(textures)):
            normal = f.norms[n]
            if normal is not None:
                glNormal3f(*normals[normal])
            texture = f.texs[n]
            if texture is not None and texture < max_texture:
                glTexCoord2f(*textures[texture][:2])
            x, y, z = vertices[f.verts[n]]
            glVertex3f(x * sx, y * sy, z * sz)

        glBegin(GL_TRIANGLES)
        for f in g.faces:
            for a, b in zip(range(1, f.size), range(2, f.size)):
                point(f, 0)
                point(f, a)
                point(f, b)
        glEnd()

        if tex_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    glPopAttrib()
    glPopMatrix()

    glEndList()
    return display
