import bz2
import gzip
import os
import zipfile
from collections import defaultdict

import six
from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range, zip

from punyverse.glgeom import array_to_gl_buffer, glRestoreClient, glMatrix, glRestore
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
    __slots__ = ('material', 'faces')

    def __init__(self, material=None, faces=None):
        self.material = material
        self.faces = faces or []


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
        u, v = 0, 0
        if l >= 2:
            u = float(words[1])
        if l >= 3:
            # OBJ origin is at upper left, OpenGL origin is at lower left
            v = 1 - float(words[2])
        self.textures.append((u, v))

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
        group = Group()
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


class ModelVBO(object):
    __slots__ = ('has_normal', 'has_texture', 'data_buf', 'index_buf', 'offset_type', 'vertex_count')

    def draw(self):
        with glRestoreClient(GL_CLIENT_VERTEX_ARRAY_BIT):
            stride = (3 + self.has_normal * 3 + self.has_texture * 2) * 4

            glBindBuffer(GL_ARRAY_BUFFER, self.data_buf)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buf)

            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, stride, 0)
            if self.has_normal:
                glEnableClientState(GL_NORMAL_ARRAY)
                glNormalPointer(GL_FLOAT, stride, 3 * 4)
            if self.has_texture:
                glEnableClientState(GL_TEXTURE_COORD_ARRAY)
                glTexCoordPointer(3, GL_FLOAT, stride, (6 if self.has_normal else 3) * 4)

            glDrawElements(GL_TRIANGLES, self.vertex_count, self.offset_type, 0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)


class WavefrontVBO(object):
    def __init__(self, model, sx=1, sy=1, sz=1, rotation=(0, 0, 0)):
        self._tex_cache = {}
        self.vbos = []
        self.rotation = rotation
        self.scale = (sx, sy, sz)

        for m, material in six.iteritems(model.materials):
            if material.texture and material.texture not in self._tex_cache:
                self._tex_cache[material.texture] = load_texture(os.path.join(model.root, material.texture))

        vertices = model.vertices
        textures = model.textures
        normals = model.normals

        for group in self.merge_groups(model):
            self.vbos.append((group.material, self.process_group(group, vertices, normals, textures)))

    def draw(self, fv4=GLfloat * 4):
        with glMatrix(rotation=self.rotation), glRestore(GL_TEXTURE_BIT | GL_ENABLE_BIT):
            for mat, vbo in self.vbos:
                tex_id = self._tex_cache[mat.texture] if mat and mat.texture else 0

                if tex_id:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, tex_id)
                else:
                    glBindTexture(GL_TEXTURE_2D, 0)
                    glDisable(GL_TEXTURE_2D)

                if mat:
                    if mat.Ka:
                        kx, ky, kz = mat.Ka
                        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, fv4(kx, ky, kz, 1))
                    if mat.Kd:
                        kx, ky, kz = mat.Kd
                        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, fv4(kx, ky, kz, 1))
                    if mat.Ks:
                        kx, ky, kz = mat.Ks
                        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, fv4(kx, ky, kz, 1))
                    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, mat.shininess)

                vbo.draw()

    def merge_groups(self, model):
        by_mat = defaultdict(list)
        for g in model.groups:
            if g.faces:
                by_mat[g.material].append(g)

        groups = []
        for mat, gs in six.iteritems(by_mat):
            faces = []
            for g in gs:
                faces += g.faces
            groups.append(Group(mat, faces))
        return groups

    def process_group(self, group, vertices, normals, textures):
        sx, sy, sz = self.scale
        max_texture = len(textures)
        has_texture = bool(textures) and any(any(n is not None for n in f.texs) for f in group.faces)
        has_normal = bool(normals) and any(any(n is not None for n in f.norms) for f in group.faces)
        buffer = []
        indices = []
        offsets = {}

        for f in group.faces:
            verts = []
            for v, n, t in zip(f.verts, f.norms, f.texs):
                # Blender defines texture coordinates on faces even without textures.
                if t is not None and t >= max_texture:
                    t = None
                if (v, n, t) in offsets:
                    verts.append(offsets[v, n, t])
                else:
                    index = len(offsets)
                    verts.append(index)
                    x, y, z = vertices[v]
                    item = [sx * x, sy * y, sz * z]
                    if has_normal:
                        item += [0, 0, 0] if n is None else list(normals[n])
                    if has_texture:
                        item += [0, 0] if t is None else list(textures[t])
                    offsets[v, n, t] = index
                    buffer += item

            for a, b in zip(verts[1:], verts[2:]):
                indices += [verts[0], a, b]

        result = ModelVBO()
        result.has_normal = has_normal
        result.has_texture = has_texture
        result.offset_type = GL_UNSIGNED_SHORT if len(offsets) < 65536 else GL_UNSIGNED_INT
        result.data_buf = array_to_gl_buffer(buffer, 'f')
        result.index_buf = array_to_gl_buffer(indices, {
            GL_UNSIGNED_SHORT: 'H',
            GL_UNSIGNED_INT: 'I',
        }[result.offset_type])
        result.vertex_count = len(indices)
        return result
