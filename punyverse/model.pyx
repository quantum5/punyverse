from time import clock
import os.path

include "_cyopengl.pxi"

from space_torus.texture import load_texture

cdef enum:
    FACE_TRIANGLES
    FACE_QUADS

cdef inline point(Face f, list vertices, list normals, list textures, float sx, float sy, float sz, int n, int tex_id):
    if f.norms:
        normal = normals[f.norms[n]]
        glNormal3f(normal[0], normal[1], normal[2])
    if tex_id:
        tex = textures[f.texs[n]]
        glTexCoord2f(tex[0], tex[1])

    x, y, z = vertices[f.verts[n]]
    glVertex3f(x * sx, y * sy, z * sz)

cpdef model_list(WavefrontObject model, float sx=1, float sy=1, float sz=1, object rotation=(0, 0, 0)):
    for m, text in model.materials.iteritems():
        if text.texture:
            load_texture(os.path.join(model.root, text.texture))

    display = glGenLists(1)

    glNewList(display, GL_COMPILE)
    glPushMatrix()
    glPushAttrib(GL_CURRENT_BIT)

    cdef float pitch, yaw, roll
    cdef kx, ky, kz

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
            if material.Ka:
                kx, ky, kz = material.Ka
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [kx, ky, kz, 1])
            if material.Kd:
                kx, ky, kz = material.Kd
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [kx, ky, kz, 1])
            if material.Ks:
                kx, ky, kz = material.Ks
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [kx, ky, kz, 1])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, material.shininess)

        type = -1

        for f in g.faces:
            if type != f.type:
                if type != -1:
                    glEnd()
                glBegin(GL_TRIANGLES)
            type = f.type

            point(f, vertices, normals, textures, sx, sy, sz, 0, tex_id)
            point(f, vertices, normals, textures, sx, sy, sz, 1, tex_id)
            point(f, vertices, normals, textures, sx, sy, sz, 2, tex_id)

            if type == FACE_QUADS:
                point(f, vertices, normals, textures, sx, sy, sz, 2, tex_id)
                point(f, vertices, normals, textures, sx, sy, sz, 3, tex_id)
                point(f, vertices, normals, textures, sx, sy, sz, 0, tex_id)
    glEnd()

    glPopAttrib()
    glPopMatrix()

    glEndList()
    return display

def load_model(path):
    print "Loading model %s..." % path
    return WavefrontObject(os.path.join(os.path.dirname(__file__), 'assets', 'models', path))

cdef class WavefrontObject(object):
    cdef public str root
    cdef public list vertices, normals, textures, groups
    cdef public dict materials
    cdef Material current_material

    cdef inline dispatch(self, str p):
        with open(p, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line[0] == '#':
                    continue # Empty or comment
                words = line.split()
                type = words[0]
                if type == 'v':
                    self.v(words)
                elif type == 'vn':
                    self.vn(words)
                elif type == 'vt':
                    self.vt(words)
                elif type == 'f':
                    self.f(words)
                elif type == 'mtllib':
                    self.mtllib(words)
                elif type == 'usemtl':
                    self.usemtl(words)
                elif type == 'g' or type == 'o':
                    self.g(words)
                elif type == 'newmtl':
                    self.newmtl(words)
                elif type == 'Ka':
                    self.Ka(words)
                elif type == 'Kd':
                    self.Kd(words)
                elif type == 'Ks':
                    self.Ks(words)
                elif type == 'Ns':
                    self.Ns(words)
                elif type == 'map_Kd':
                    self.map_Kd(words)

    cdef inline newmtl(self, list words):
        material = Material(words[1])
        self.materials[words[1]] = material
        self.current_material = material

    cdef inline Ka(self, list words):
        self.current_material.Ka = (float(words[1]), float(words[2]), float(words[3]))

    cdef inline Kd(self, list words):
        self.current_material.Kd = (float(words[1]), float(words[2]), float(words[3]))

    cdef inline Ks(self, list words):
        self.current_material.Ks = (float(words[1]), float(words[2]), float(words[3]))

    cdef inline Ns(self, list words):
        self.current_material.shininess = min(float(words[1]), 125) # Seems to sometimes be > 125. TODO: find out why

    cdef inline map_Kd(self, list words):
        self.current_material.texture = words[-1]

    cdef inline v(self, list words):
        self.vertices.append((float(words[1]), float(words[2]), float(words[3])))

    cdef inline vn(self, list words):
        self.normals.append((float(words[1]), float(words[2]), float(words[3])))

    cdef inline vt(self, list words):
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

    cdef inline f(self, list words):
        l = len(words)
        type = -1
        cdef list face_vertices, face_normals, face_textures, raw_faces, vindices, nindices, tindicies
        cdef int current_value

        face_vertices = []
        face_normals = []
        face_textures = []

        vertex_count = l - 1
        if vertex_count == 3:
            type = FACE_TRIANGLES
        else:
            type = FACE_QUADS

        raw_faces = []
        current_value = -1
        vindices = []
        nindices = []
        tindices = []

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
                if current_value <= len(self.textures):
                    tindices.append(current_value - 1)
                    face_textures.append(self.textures[current_value - 1])
            if l >= 3 and raw_faces[2]:
                current_value = int(raw_faces[2])
                nindices.append(current_value - 1)
                face_normals.append(self.normals[current_value - 1])

        if not self.groups:
            group = Group()
            self.groups.append(group)
        else:
            group = self.groups[-1]
        group.vertices += face_vertices
        group.normals += face_normals
        group.textures += face_textures

        idx_count = group.idx_count
        group.indices += (idx_count + 1, idx_count + 2, idx_count + 3)
        group.idx_count += 3

        group.faces.append(Face(type, vindices, nindices, tindices, face_vertices, face_normals, face_textures))

    cdef inline mtllib(self, list words):
        self.dispatch(os.path.join(self.root, words[1]))

    cdef inline usemtl(self, list words):
        mat = words[1]
        if mat in self.materials:
            self.groups[-1].material = self.materials[mat]
        else:
            print "Warning: material %s undefined." % mat

    cdef inline g(self, list words):
        self.groups.append(Group(words[1]))

    def __init__(self, str path):
        self.root = os.path.dirname(path)
        self.vertices = []
        self.normals = []
        self.textures = []
        self.groups = []
        self.materials = {}
        self.dispatch(path)

cdef class Group(object):
    cdef public str name
    cdef public tuple min
    cdef public Material material
    cdef public list faces, indices, vertices, normals, textures
    cdef public int idx_count

    def __init__(self, str name=None):
        if not name:
            name = clock()
        self.name = name
        self.material = None
        self.faces = []
        self.indices = []
        self.vertices = []
        self.normals = []
        self.textures = []
        self.idx_count = 0

cdef class Face(object):
    cdef public int type
    cdef public list verts, norms, texs, vertices, normals, textures

    def __init__(self, int type, list verts, list norms, list texs, list vertices, list normals, list textures):
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

    def __init__(self, str name, str texture=None, tuple Ka=(0, 0, 0), tuple Kd=(0, 0, 0), tuple Ks=(0, 0, 0),
                 double shininess=0.0):
        self.name = name
        self.texture = texture
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.shininess = shininess