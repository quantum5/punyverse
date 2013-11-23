from libc.string cimport strcmp, strlen
from libc.stdlib cimport malloc, free, atof
from libc.stdio cimport fopen, fclose, fgets, FILE
cimport cython

from punyverse.texture import load_texture
include "_cyopengl.pxi"
from uuid import uuid4
import os
import gzip
import bz2
import zipfile

def zip_open(file):
    zip = zipfile.ZipFile(file)
    return zip.open(zip.namelist()[0])

openers = {
    'gz': gzip.open,
    'bz2': bz2.BZ2File,
    'zip': zip_open,
}


cdef enum:
    FACE_TRIANGLES
    FACE_QUADS

cdef class Face(object):
    cdef public int type
    cdef public list verts, norms, texs, vertices, normals, textures
    
    def __init__(self, int type, list verts, list norms, list texs,
                 list vertices, list normals, list textures):
        self.type = type
        self.verts = verts
        self.norms = norms
        self.texs = texs
        self.vertices = vertices
        self.normals = normals
        self.textures = textures

cdef class Material(object):
    cdef public str name, texture
    cdef public tuple Ka, Kd, Ks
    cdef public double shininess
    
    def __init__(self, str name, str texture=None, tuple Ka=(0, 0, 0),
                 tuple Kd=(0, 0, 0), tuple Ks=(0, 0, 0), double shininess=0.0):
        self.name = name
        self.texture = texture
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.shininess = shininess

cdef class Group(object):
    cdef public str name
    cdef public tuple min
    cdef public Material material
    cdef public list faces, indices, vertices, normals, textures
    cdef public int idx_count
    
    def __init__(self, str name=None):
        if name is None:
            self.name = str(uuid4())
        else:
            self.name = name
        self.min = ()
        self.material = None
        self.faces = []
        self.indices = []
        self.vertices = []
        self.normals = []
        self.textures = []
        self.idx_count = 0

    def pack(self):
        min_x, min_y, min_z = 0, 0, 0
        for face in self.faces:
            for x, y, z in face.vertices:
                min_x = max(min_x, abs(x))
                min_y = max(min_y, abs(y))
                min_z = max(min_x, abs(z))
        self.min = (min_x, min_y, min_z)

cdef class WavefrontObject(object):
    cdef unicode root
    cdef public list vertices, normals, textures, groups
    cdef public dict materials
    cdef unicode path
    cdef Material current_material
    cdef Group current_group
    def __init__(self, unicode path):
        self.path = path
        self.root = os.path.abspath(os.path.dirname(path))
        self.vertices = []
        self.normals = []
        self.textures = []
        self.groups = []
        self.materials = {}

        self.perform_io(self.path)
    
    cdef void new_material(self, list words):
        material = Material(words[1])
        self.materials[words[1]] = material
        self.current_material = material
    
    cdef void Ka(self, list words):
        self.current_material.Ka = (float(words[1]), float(words[2]), float(words[3]))
    
    cdef void Kd(self, list words):
        self.current_material.Kd = (float(words[1]), float(words[2]), float(words[3]))
    
    cdef void Ks(self, list words):
        self.current_material.Ks = (float(words[1]), float(words[2]), float(words[3]))
    
    cdef void material_shininess(self, list words):
        self.current_material.shininess = min(float(words[1]), 125)
    
    cdef void material_texture(self, list words):
        self.current_material.texture = words[-1]
    
    @cython.nonecheck(False)
    cdef void vertex(self, list words):
        self.vertices.append((float(words[1]), float(words[2]), float(words[3])))
    
    @cython.nonecheck(False)
    cdef void normal(self, list words):
        self.normals.append((float(words[1]), float(words[2]), float(words[3])))
    
    cdef void texture(self, list words):
        cdef int l = len(words)
        cdef object x = 0, y = 0, z = 0
        if l >= 2:
            x = float(words[1])
        if l >= 3:
            # OBJ origin is at upper left, OpenGL origin is at lower left
            y = 1 - float(words[2])
        if l >= 4:
            z = float(words[3])
        self.textures.append((x, y, z))
    
    cdef void face(self, list words):
        cdef int l = len(words)
        cdef int type = -1
        cdef int vertex_count = l - 1
        cdef list face_vertices = [], face_normals = [], face_textures = []

        if vertex_count == 3:
            type = FACE_TRIANGLES
        else:
            type = FACE_QUADS

        cdef int current_value = -1, texture_len = len(self.textures)
        cdef list raw_faces, vindices = [], nindices = [], tindices = []

        for i in xrange(1, vertex_count + 1):
            raw_faces = words[i].split('/')
            l = len(raw_faces)

            current_value = int(raw_faces[0])
            vindices.append(current_value - 1)
            face_vertices.append(self.vertices[current_value - 1])

            if l == 1:
                continue
            if l >= 2 and raw_faces[1]:
                current_value = int(raw_faces[1])
                if current_value <= texture_len:
                    tindices.append(current_value - 1)
                    face_textures.append(self.textures[current_value - 1])
            if l >= 3 and raw_faces[2]:
                current_value = int(raw_faces[2])
                nindices.append(current_value - 1)
                face_normals.append(self.normals[current_value - 1])

        cdef Group group
        if self.current_group is None:
            self.current_group = group = Group()
            self.groups.append(group)
        else:
            group = self.current_group

        group.vertices += face_vertices
        group.normals += face_normals
        group.textures += face_textures
        idx_count = group.idx_count
        group.indices += (idx_count + 1, idx_count + 2, idx_count + 3)
        group.idx_count += 3

        group.faces.append(Face(type, vindices, nindices, tindices, face_vertices, face_normals, face_textures))

    cdef bint material(self, list words) except False:
        return self.perform_io(os.path.join(self.root, words[1]))
        
    cdef void use_material(self, list words):
        mat = words[1]
        try:
            self.current_group.material = self.materials[mat]
        except KeyError:
            print "Warning: material %s undefined, only %s defined." % (mat, self.materials)
        except AttributeError:
            print "Warning: no group"

    cdef void group(self, list words):
        name = words[1]
        group = Group(name)

        if self.groups:
            self.current_group.pack()
        self.groups.append(group)
        self.current_group = group

    cdef inline bint perform_io(self, unicode file) except False:
        cdef const char *type
        cdef list words
        cdef int hash, length

        ext = os.path.splitext(file)[1].lstrip('.')
        reader = openers.get(ext, open)(file)
        with reader:
            for buf in reader:
                if not buf or buf.startswith(('\r', '\n', '#')):
                    continue # Empty or comment
                words = buf.split()
                type = words[0]

                length = strlen(type)
                if not length:
                    continue
                elif length < 3:
                    hash = type[0] << 8 | type[1]
                    if hash == 0x7600:  # v\0
                        self.vertex(words)
                    elif hash == 0x766e: # vn
                        self.normal(words)
                    elif hash == 0x7674: # vt
                        self.texture(words)
                    elif hash == 0x6600: # f
                        self.face(words)
                    elif hash == 0x6700: # g
                        self.group(words)
                    elif hash == 0x6f00: # o
                        self.group(words)
                    elif hash == 0x4b61: # Ka
                        self.Ka(words)
                    elif hash == 0x4b64: # Kd
                        self.Kd(words)
                    elif hash == 0x4b73: # Ks
                        self.Ks(words)
                    elif hash == 0x4e73: # Ns
                        self.material_shininess(words)
                elif strcmp(type, b'mtllib') == 0:
                    self.material(words)
                elif strcmp(type, b'usemtl') == 0:
                    self.use_material(words)
                elif strcmp(type, b'newmtl') == 0:
                    self.new_material(words)
                elif strcmp(type, b'map_Kd') == 0:
                    self.material_texture(words)
        return True

model_base = None

def load_model(path):
    global model_base
    if model_base is None:
        import sys
        if hasattr(sys, 'frozen'):
            model_base = os.path.dirname(sys.executable)
        else:
            model_base = os.path.join(os.path.dirname(__file__), 'assets', 'models')
    if not os.path.isabs(path):
        path = os.path.join(model_base, path)
    if not isinstance(path, unicode):
        path = path.decode('mbcs')
    return WavefrontObject(path)

@cython.nonecheck(False)
cdef inline void point(Face f, WavefrontObject m, int tex_id, float sx, float sy, float sz, int n):
    cdef float x, y, z
    cdef tuple normal, texture
    if f.norms:
        normal = m.normals[f.norms[n]]
        glNormal3f(normal[0], normal[1], normal[2])
    if tex_id:
        texture = m.textures[f.texs[n]]
        glTexCoord2f(texture[0], texture[1])

    x, y, z = m.vertices[f.verts[n]]
    glVertex3f(x * sx, y * sy, z * sz)

cpdef int model_list(WavefrontObject model, float sx=1, float sy=1, float sz=1, object rotation=(0, 0, 0)):
    for m, text in model.materials.iteritems():
        if text.texture:
            load_texture(os.path.join(model.root, text.texture))

    cdef int display = glGenLists(1)

    glNewList(display, GL_COMPILE)
    glPushMatrix()
    glPushAttrib(GL_CURRENT_BIT)

    cdef float pitch, yaw, roll
    cdef float kx, ky, kz
    
    pitch, yaw, roll = rotation
    glPushAttrib(GL_TRANSFORM_BIT)
    glRotatef(pitch, 1, 0, 0)
    glRotatef(yaw, 0, 1, 0)
    glRotatef(roll, 0, 0, 1)
    glPopAttrib()

    cdef Face f
    cdef Group g
    cdef int tex_id

    for g in model.groups:
        tex_id = load_texture(os.path.join(model.root, g.material.texture)) if (g.material and g.material.texture) else 0

        if tex_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
        else:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

        if g.material is not None:
            if g.material.Ka:
                kx, ky, kz = g.material.Ka
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [kx, ky, kz, 1])
            if g.material.Kd:
                kx, ky, kz = g.material.Kd
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [kx, ky, kz, 1])
            if g.material.Ks:
                kx, ky, kz = g.material.Ks
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [kx, ky, kz, 1])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, g.material.shininess)

        glBegin(GL_TRIANGLES)
        for f in g.faces:
            point(f, model, tex_id, sx, sy, sz, 0)
            point(f, model, tex_id, sx, sy, sz, 1)
            point(f, model, tex_id, sx, sy, sz, 2)

            if f.type == FACE_QUADS:
                point(f, model, tex_id, sx, sy, sz, 2)
                point(f, model, tex_id, sx, sy, sz, 3)
                point(f, model, tex_id, sx, sy, sz, 0)
        glEnd()

        if tex_id:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    glPopAttrib()
    glPopMatrix()

    glEndList()
    return display
