IF UNAME_SYSNAME == "Windows":
    cdef extern from "windows.h":
        pass

cdef extern from "GL/gl.h":
    ctypedef unsigned int   GLenum
    ctypedef unsigned char  GLboolean
    ctypedef unsigned int   GLbitfield
    ctypedef void           GLvoid
    ctypedef signed char    GLbyte
    ctypedef short          GLshort
    ctypedef int            GLint
    ctypedef unsigned char  GLubyte
    ctypedef unsigned short GLushort
    ctypedef unsigned int   GLuint
    ctypedef int            GLsizei
    ctypedef float          GLfloat
    ctypedef float          GLclampf
    ctypedef double         GLdouble
    ctypedef double         GLclampd

    # Miscellaneous 
    void glClearIndex(GLfloat c)
    void glClearColor(GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
    void glClear(GLbitfield mask)
    void glIndexMask(GLuint mask)
    void glColorMask(GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha)
    void glAlphaFunc(GLenum func, GLclampf ref)
    void glBlendFunc(GLenum sfactor, GLenum dfactor)
    void glLogicOp(GLenum opcode)
    void glCullFace(GLenum mode)
    void glFrontFace(GLenum mode)
    void glPointSize(GLfloat size)
    void glLineWidth(GLfloat width)
    void glLineStipple(GLint factor, GLushort pattern)
    void glPolygonMode(GLenum face, GLenum mode)
    void glPolygonOffset(GLfloat factor, GLfloat units)
    void glPolygonStipple(GLubyte *mask)
    void glGetPolygonStipple(GLubyte *mask)
    void glEdgeFlag(GLboolean flag)
    void glEdgeFlagv(GLboolean *flag)
    void glScissor(GLint x, GLint y, GLsizei width, GLsizei height)
    void glClipPlane(GLenum plane, GLdouble *equation)
    void glGetClipPlane(GLenum plane, GLdouble *equation)
    void glDrawBuffer(GLenum mode)
    void glReadBuffer(GLenum mode)
    void glEnable(GLenum cap)
    void glDisable(GLenum cap)
    GLboolean glIsEnabled(GLenum cap)
    void glEnableClientState(GLenum cap)  # 1.1 
    void glDisableClientState(GLenum cap)  # 1.1 
    void glGetBooleanv(GLenum pname, GLboolean *params)
    void glGetDoublev(GLenum pname, GLdouble *params)
    void glGetFloatv(GLenum pname, GLfloat *params)
    void glGetIntegerv(GLenum pname, GLint *params)
    void glPushAttrib(GLbitfield mask)
    void glPopAttrib()
    void glPushClientAttrib(GLbitfield mask)  # 1.1 
    void glPopClientAttrib()  # 1.1 
    GLint glRenderMode(GLenum mode)
    GLenum glGetError()
    GLubyte* glGetString(GLenum name)
    void glFinish()
    void glFlush()
    void glHint(GLenum target, GLenum mode)

    # Depth Buffer 
    void glClearDepth(GLclampd depth)
    void glDepthFunc(GLenum func)
    void glDepthMask(GLboolean flag)
    void glDepthRange(GLclampd near_val, GLclampd far_val)

    # Accumulation Buffer 
    void glClearAccum(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
    void glAccum(GLenum op, GLfloat value)

    # Transformation 
    void glMatrixMode(GLenum mode)
    void glOrtho(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top, GLdouble near_val, GLdouble far_val)
    void glFrustum(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top, GLdouble near_val, GLdouble far_val)
    void glViewport(GLint x, GLint y, GLsizei width, GLsizei height)
    void glPushMatrix()
    void glPopMatrix()
    void glLoadIdentity()
    void glLoadMatrixd(GLdouble *m)
    void glLoadMatrixf(GLfloat *m)
    void glMultMatrixd(GLdouble *m)
    void glMultMatrixf(GLfloat *m)
    void glRotated(GLdouble angle, GLdouble x, GLdouble y, GLdouble z)
    void glRotatef(GLfloat angle, GLfloat x, GLfloat y, GLfloat z)
    void glScaled(GLdouble x, GLdouble y, GLdouble z)
    void glScalef(GLfloat x, GLfloat y, GLfloat z)
    void glTranslated(GLdouble x, GLdouble y, GLdouble z)
    void glTranslatef(GLfloat x, GLfloat y, GLfloat z)

    # Display Lists 
    GLboolean glIsList(GLuint list)
    void glDeleteLists(GLuint list, GLsizei range)
    GLuint glGenLists(GLsizei range)
    void glNewList(GLuint list, GLenum mode)
    void glEndList()
    void glCallList(GLuint list)
    void glCallLists(GLsizei n, GLenum type, GLvoid *lists)
    void glListBase(GLuint base)

    # Drawing Functions 
    void glBegin(GLenum mode)
    void glEnd()
    void glVertex2d(GLdouble x, GLdouble y)
    void glVertex2f(GLfloat x, GLfloat y)
    void glVertex2i(GLint x, GLint y)
    void glVertex2s(GLshort x, GLshort y)
    void glVertex3d(GLdouble x, GLdouble y, GLdouble z)
    void glVertex3f(GLfloat x, GLfloat y, GLfloat z)
    void glVertex3i(GLint x, GLint y, GLint z)
    void glVertex3s(GLshort x, GLshort y, GLshort z)
    void glVertex4d(GLdouble x, GLdouble y, GLdouble z, GLdouble w)
    void glVertex4f(GLfloat x, GLfloat y, GLfloat z, GLfloat w)
    void glVertex4i(GLint x, GLint y, GLint z, GLint w)
    void glVertex4s(GLshort x, GLshort y, GLshort z, GLshort w)
    void glVertex2dv(GLdouble *v)
    void glVertex2fv(GLfloat *v)
    void glVertex2iv(GLint *v)
    void glVertex2sv(GLshort *v)
    void glVertex3dv(GLdouble *v)
    void glVertex3fv(GLfloat *v)
    void glVertex3iv(GLint *v)
    void glVertex3sv(GLshort *v)
    void glVertex4dv(GLdouble *v)
    void glVertex4fv(GLfloat *v)
    void glVertex4iv(GLint *v)
    void glVertex4sv(GLshort *v)
    void glNormal3b(GLbyte nx, GLbyte ny, GLbyte nz)
    void glNormal3d(GLdouble nx, GLdouble ny, GLdouble nz)
    void glNormal3f(GLfloat nx, GLfloat ny, GLfloat nz)
    void glNormal3i(GLint nx, GLint ny, GLint nz)
    void glNormal3s(GLshort nx, GLshort ny, GLshort nz)
    void glNormal3bv(GLbyte *v)
    void glNormal3dv(GLdouble *v)
    void glNormal3fv(GLfloat *v)
    void glNormal3iv(GLint *v)
    void glNormal3sv(GLshort *v)
    void glIndexd(GLdouble c)
    void glIndexf(GLfloat c)
    void glIndexi(GLint c)
    void glIndexs(GLshort c)
    void glIndexub(GLubyte c)  # 1.1 
    void glIndexdv(GLdouble *c)
    void glIndexfv(GLfloat *c)
    void glIndexiv(GLint *c)
    void glIndexsv(GLshort *c)
    void glIndexubv(GLubyte *c)  # 1.1 
    void glColor3b(GLbyte red, GLbyte green, GLbyte blue)
    void glColor3d(GLdouble red, GLdouble green, GLdouble blue)
    void glColor3f(GLfloat red, GLfloat green, GLfloat blue)
    void glColor3i(GLint red, GLint green, GLint blue)
    void glColor3s(GLshort red, GLshort green, GLshort blue)
    void glColor3ub(GLubyte red, GLubyte green, GLubyte blue)
    void glColor3ui(GLuint red, GLuint green, GLuint blue)
    void glColor3us(GLushort red, GLushort green, GLushort blue)
    void glColor4b(GLbyte red, GLbyte green, GLbyte blue, GLbyte alpha)
    void glColor4d(GLdouble red, GLdouble green, GLdouble blue, GLdouble alpha)
    void glColor4f(GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
    void glColor4i(GLint red, GLint green, GLint blue, GLint alpha)
    void glColor4s(GLshort red, GLshort green, GLshort blue, GLshort alpha)
    void glColor4ub(GLubyte red, GLubyte green, GLubyte blue, GLubyte alpha)
    void glColor4ui(GLuint red, GLuint green, GLuint blue, GLuint alpha)
    void glColor4us(GLushort red, GLushort green, GLushort blue, GLushort alpha)
    void glColor3bv(GLbyte *v)
    void glColor3dv(GLdouble *v)
    void glColor3fv(GLfloat *v)
    void glColor3iv(GLint *v)
    void glColor3sv(GLshort *v)
    void glColor3ubv(GLubyte *v)
    void glColor3uiv(GLuint *v)
    void glColor3usv(GLushort *v)
    void glColor4bv(GLbyte *v)
    void glColor4dv(GLdouble *v)
    void glColor4fv(GLfloat *v)
    void glColor4iv(GLint *v)
    void glColor4sv(GLshort *v)
    void glColor4ubv(GLubyte *v)
    void glColor4uiv(GLuint *v)
    void glColor4usv(GLushort *v)
    void glTexCoord1d(GLdouble s)
    void glTexCoord1f(GLfloat s)
    void glTexCoord1i(GLint s)
    void glTexCoord1s(GLshort s)
    void glTexCoord2d(GLdouble s, GLdouble t)
    void glTexCoord2f(GLfloat s, GLfloat t)
    void glTexCoord2i(GLint s, GLint t)
    void glTexCoord2s(GLshort s, GLshort t)
    void glTexCoord3d(GLdouble s, GLdouble t, GLdouble r)
    void glTexCoord3f(GLfloat s, GLfloat t, GLfloat r)
    void glTexCoord3i(GLint s, GLint t, GLint r)
    void glTexCoord3s(GLshort s, GLshort t, GLshort r)
    void glTexCoord4d(GLdouble s, GLdouble t, GLdouble r, GLdouble q)
    void glTexCoord4f(GLfloat s, GLfloat t, GLfloat r, GLfloat q)
    void glTexCoord4i(GLint s, GLint t, GLint r, GLint q)
    void glTexCoord4s(GLshort s, GLshort t, GLshort r, GLshort q)
    void glTexCoord1dv(GLdouble *v)
    void glTexCoord1fv(GLfloat *v)
    void glTexCoord1iv(GLint *v)
    void glTexCoord1sv(GLshort *v)
    void glTexCoord2dv(GLdouble *v)
    void glTexCoord2fv(GLfloat *v)
    void glTexCoord2iv(GLint *v)
    void glTexCoord2sv(GLshort *v)
    void glTexCoord3dv(GLdouble *v)
    void glTexCoord3fv(GLfloat *v)
    void glTexCoord3iv(GLint *v)
    void glTexCoord3sv(GLshort *v)
    void glTexCoord4dv(GLdouble *v)
    void glTexCoord4fv(GLfloat *v)
    void glTexCoord4iv(GLint *v)
    void glTexCoord4sv(GLshort *v)
    void glRasterPos2d(GLdouble x, GLdouble y)
    void glRasterPos2f(GLfloat x, GLfloat y)
    void glRasterPos2i(GLint x, GLint y)
    void glRasterPos2s(GLshort x, GLshort y)
    void glRasterPos3d(GLdouble x, GLdouble y, GLdouble z)
    void glRasterPos3f(GLfloat x, GLfloat y, GLfloat z)
    void glRasterPos3i(GLint x, GLint y, GLint z)
    void glRasterPos3s(GLshort x, GLshort y, GLshort z)
    void glRasterPos4d(GLdouble x, GLdouble y, GLdouble z, GLdouble w)
    void glRasterPos4f(GLfloat x, GLfloat y, GLfloat z, GLfloat w)
    void glRasterPos4i(GLint x, GLint y, GLint z, GLint w)
    void glRasterPos4s(GLshort x, GLshort y, GLshort z, GLshort w)
    void glRasterPos2dv(GLdouble *v)
    void glRasterPos2fv(GLfloat *v)
    void glRasterPos2iv(GLint *v)
    void glRasterPos2sv(GLshort *v)
    void glRasterPos3dv(GLdouble *v)
    void glRasterPos3fv(GLfloat *v)
    void glRasterPos3iv(GLint *v)
    void glRasterPos3sv(GLshort *v)
    void glRasterPos4dv(GLdouble *v)
    void glRasterPos4fv(GLfloat *v)
    void glRasterPos4iv(GLint *v)
    void glRasterPos4sv(GLshort *v)
    void glRectd(GLdouble x1, GLdouble y1, GLdouble x2, GLdouble y2)
    void glRectf(GLfloat x1, GLfloat y1, GLfloat x2, GLfloat y2)
    void glRecti(GLint x1, GLint y1, GLint x2, GLint y2)
    void glRects(GLshort x1, GLshort y1, GLshort x2, GLshort y2)
    void glRectdv(GLdouble *v1, GLdouble *v2)
    void glRectfv(GLfloat *v1, GLfloat *v2)
    void glRectiv(GLint *v1, GLint *v2)
    void glRectsv(GLshort *v1, GLshort *v2)

    # Lighting 
    void glShadeModel(GLenum mode)
    void glLightf(GLenum light, GLenum pname, GLfloat param)
    void glLighti(GLenum light, GLenum pname, GLint param)
    void glLightfv(GLenum light, GLenum pname, GLfloat *params)
    void glLightiv(GLenum light, GLenum pname, GLint *params)
    void glGetLightfv(GLenum light, GLenum pname, GLfloat *params)
    void glGetLightiv(GLenum light, GLenum pname, GLint *params)
    void glLightModelf(GLenum pname, GLfloat param)
    void glLightModeli(GLenum pname, GLint param)
    void glLightModelfv(GLenum pname, GLfloat *params)
    void glLightModeliv(GLenum pname, GLint *params)
    void glMaterialf(GLenum face, GLenum pname, GLfloat param)
    void glMateriali(GLenum face, GLenum pname, GLint param)
    void glMaterialfv(GLenum face, GLenum pname, GLfloat *params)
    void glMaterialiv(GLenum face, GLenum pname, GLint *params)
    void glGetMaterialfv(GLenum face, GLenum pname, GLfloat *params)
    void glGetMaterialiv(GLenum face, GLenum pname, GLint *params)
    void glColorMaterial(GLenum face, GLenum mode)

    # Raster functions 
    void glPixelZoom(GLfloat xfactor, GLfloat yfactor)
    void glPixelStoref(GLenum pname, GLfloat param)
    void glPixelStorei(GLenum pname, GLint param)
    void glPixelTransferf(GLenum pname, GLfloat param)
    void glPixelTransferi(GLenum pname, GLint param)
    void glPixelMapfv(GLenum map, GLint mapsize, GLfloat *values)
    void glPixelMapuiv(GLenum map, GLint mapsize, GLuint *values)
    void glPixelMapusv(GLenum map, GLint mapsize, GLushort *values)
    void glGetPixelMapfv(GLenum map, GLfloat *values)
    void glGetPixelMapuiv(GLenum map, GLuint *values)
    void glGetPixelMapusv(GLenum map, GLushort *values)
    void glBitmap(GLsizei width, GLsizei height, GLfloat xorig, GLfloat yorig, GLfloat xmove, GLfloat ymove, GLubyte *bitmap)
    void glReadPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels)
    void glDrawPixels(GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels)
    void glCopyPixels(GLint x, GLint y, GLsizei width, GLsizei height, GLenum type)

    # Stenciling 
    void glStencilFunc(GLenum func, GLint ref, GLuint mask)
    void glStencilMask(GLuint mask)
    void glStencilOp(GLenum fail, GLenum zfail, GLenum zpass)
    void glClearStencil(GLint s)

    # Texture mapping 
    void glTexGend(GLenum coord, GLenum pname, GLdouble param)
    void glTexGenf(GLenum coord, GLenum pname, GLfloat param)
    void glTexGeni(GLenum coord, GLenum pname, GLint param)
    void glTexGendv(GLenum coord, GLenum pname, GLdouble *params)
    void glTexGenfv(GLenum coord, GLenum pname, GLfloat *params)
    void glTexGeniv(GLenum coord, GLenum pname, GLint *params)
    void glGetTexGendv(GLenum coord, GLenum pname, GLdouble *params)
    void glGetTexGenfv(GLenum coord, GLenum pname, GLfloat *params)
    void glGetTexGeniv(GLenum coord, GLenum pname, GLint *params)
    void glTexEnvf(GLenum target, GLenum pname, GLfloat param)
    void glTexEnvi(GLenum target, GLenum pname, GLint param)
    void glTexEnvfv(GLenum target, GLenum pname, GLfloat *params)
    void glTexEnviv(GLenum target, GLenum pname, GLint *params)
    void glGetTexEnvfv(GLenum target, GLenum pname, GLfloat *params)
    void glGetTexEnviv(GLenum target, GLenum pname, GLint *params)
    void glTexParameterf(GLenum target, GLenum pname, GLfloat param)
    void glTexParameteri(GLenum target, GLenum pname, GLint param)
    void glTexParameterfv(GLenum target, GLenum pname, GLfloat *params)
    void glTexParameteriv(GLenum target, GLenum pname, GLint *params)
    void glGetTexParameterfv(GLenum target, GLenum pname, GLfloat *params)
    void glGetTexParameteriv(GLenum target, GLenum pname, GLint *params)
    void glGetTexLevelParameterfv(GLenum target, GLint level, GLenum pname, GLfloat *params)
    void glGetTexLevelParameteriv(GLenum target, GLint level, GLenum pname, GLint *params)
    void glTexImage1D(GLenum target, GLint level, GLint internalFormat, GLsizei width, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    void glTexImage2D(GLenum target, GLint level, GLint internalFormat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type, GLvoid *pixels)
    void glGetTexImage(GLenum target, GLint level, GLenum format, GLenum type, GLvoid *pixels)

    # Evaluators 
    void glMap1d(GLenum target, GLdouble u1, GLdouble u2, GLint stride, GLint order, GLdouble *points)
    void glMap1f(GLenum target, GLfloat u1, GLfloat u2, GLint stride, GLint order, GLfloat *points)
    void glMap2d(GLenum target, GLdouble u1, GLdouble u2, GLint ustride, GLint uorder, GLdouble v1, GLdouble v2, GLint vstride, GLint vorder, GLdouble *points)
    void glMap2f(GLenum target, GLfloat u1, GLfloat u2, GLint ustride, GLint uorder, GLfloat v1, GLfloat v2, GLint vstride, GLint vorder, GLfloat *points)
    void glGetMapdv(GLenum target, GLenum query, GLdouble *v)
    void glGetMapfv(GLenum target, GLenum query, GLfloat *v)
    void glGetMapiv(GLenum target, GLenum query, GLint *v)
    void glEvalCoord1d(GLdouble u)
    void glEvalCoord1f(GLfloat u)
    void glEvalCoord1dv(GLdouble *u)
    void glEvalCoord1fv(GLfloat *u)
    void glEvalCoord2d(GLdouble u, GLdouble v)
    void glEvalCoord2f(GLfloat u, GLfloat v)
    void glEvalCoord2dv(GLdouble *u)
    void glEvalCoord2fv(GLfloat *u)
    void glMapGrid1d(GLint un, GLdouble u1, GLdouble u2)
    void glMapGrid1f(GLint un, GLfloat u1, GLfloat u2)
    void glMapGrid2d(GLint un, GLdouble u1, GLdouble u2, GLint vn, GLdouble v1, GLdouble v2)
    void glMapGrid2f(GLint un, GLfloat u1, GLfloat u2, GLint vn, GLfloat v1, GLfloat v2)
    void glEvalPoint1(GLint i)
    void glEvalPoint2(GLint i, GLint j)
    void glEvalMesh1(GLenum mode, GLint i1, GLint i2)
    void glEvalMesh2(GLenum mode, GLint i1, GLint i2, GLint j1, GLint j2)

    # Fog 
    void glFogf(GLenum pname, GLfloat param)
    void glFogi(GLenum pname, GLint param)
    void glFogfv(GLenum pname, GLfloat *params)
    void glFogiv(GLenum pname, GLint *params)

    # Selection and Feedback 
    void glFeedbackBuffer(GLsizei size, GLenum type, GLfloat *buffer)
    void glPassThrough(GLfloat token)
    void glSelectBuffer(GLsizei size, GLuint *buffer)
    void glInitNames()
    void glLoadName(GLuint name)
    void glPushName(GLuint name)
    void glPopName()


    # 1.1 functions 
    # texture objects 
    void glGenTextures(GLsizei n, GLuint *textures)
    void glDeleteTextures(GLsizei n, GLuint *textures)
    void glBindTexture(GLenum target, GLuint texture)
    void glPrioritizeTextures(GLsizei n, GLuint *textures, GLclampf *priorities)
    GLboolean glAreTexturesResident(GLsizei n, GLuint *textures, GLboolean *residences)
    GLboolean glIsTexture(GLuint texture)
    # texture mapping 
    void glTexSubImage1D(GLenum target, GLint level, GLint xoffset, GLsizei width, GLenum format, GLenum type, GLvoid *pixels)
    void glTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid *pixels)
    void glCopyTexImage1D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLint border)
    void glCopyTexImage2D(GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border)
    void glCopyTexSubImage1D(GLenum target, GLint level, GLint xoffset, GLint x, GLint y, GLsizei width)
    void glCopyTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height)
    # vertex arrays 
    void glVertexPointer(GLint size, GLenum type, GLsizei stride, GLvoid *ptr)
    void glNormalPointer(GLenum type, GLsizei stride, GLvoid *ptr)
    void glColorPointer(GLint size, GLenum type, GLsizei stride, GLvoid *ptr)
    void glIndexPointer(GLenum type, GLsizei stride, GLvoid *ptr)
    void glTexCoordPointer(GLint size, GLenum type, GLsizei stride, GLvoid *ptr)
    void glEdgeFlagPointer(GLsizei stride, GLvoid *ptr)
    void glGetPointerv(GLenum pname, GLvoid **params)
    void glArrayElement(GLint i)
    void glDrawArrays(GLenum mode, GLint first, GLsizei count)
    void glDrawElements(GLenum mode, GLsizei count, GLenum type, GLvoid *indices)
    void glInterleavedArrays(GLenum format, GLsizei stride, GLvoid *pointer)

cdef extern from "stddef.h":
    ctypedef unsigned int wchar_t

cdef extern from "GL/glu.h":
    ctypedef struct GLUnurbs:
        pass
    ctypedef struct GLUquadric:
        pass
    ctypedef struct GLUtesselator:
        pass

    ctypedef GLUnurbs GLUnurbsObj
    ctypedef GLUquadric GLUquadricObj
    ctypedef GLUtesselator GLUtesselatorObj
    ctypedef GLUtesselator GLUtriangulatorObj

    void gluBeginCurve(GLUnurbs* nurb)
    void gluBeginPolygon(GLUtesselator* tess)
    void gluBeginSurface(GLUnurbs* nurb)
    void gluBeginTrim(GLUnurbs* nurb)
    GLint gluBuild1DMipmaps(GLenum target, GLint internalFormat, GLsizei width, GLenum format, GLenum type, void *data)
    GLint gluBuild2DMipmaps(GLenum target, GLint internalFormat, GLsizei width, GLsizei height, GLenum format, GLenum type, void *data)
    void gluCylinder(GLUquadric* quad, GLdouble base, GLdouble top, GLdouble height, GLint slices, GLint stacks)
    void gluDeleteNurbsRenderer(GLUnurbs* nurb)
    void gluDeleteQuadric(GLUquadric* quad)
    void gluDeleteTess(GLUtesselator* tess)
    void gluDisk(GLUquadric* quad, GLdouble inner, GLdouble outer, GLint slices, GLint loops)
    void gluEndCurve(GLUnurbs* nurb)
    void gluEndPolygon(GLUtesselator* tess)
    void gluEndSurface(GLUnurbs* nurb)
    void gluEndTrim(GLUnurbs* nurb)
    GLubyte * gluErrorString(GLenum error)
    wchar_t * gluErrorUnicodeStringEXT(GLenum error)
    void gluGetNurbsProperty(GLUnurbs* nurb, GLenum property, GLfloat* data)
    GLubyte * gluGetString(GLenum name)
    void gluGetTessProperty(GLUtesselator* tess, GLenum which, GLdouble* data)
    void gluLoadSamplingMatrices(GLUnurbs* nurb, GLfloat *model, GLfloat *perspective, GLint *view)
    void gluLookAt(GLdouble eyeX, GLdouble eyeY, GLdouble eyeZ, GLdouble centerX, GLdouble centerY, GLdouble centerZ, GLdouble upX, GLdouble upY, GLdouble upZ)
    GLUnurbs* gluNewNurbsRenderer()
    GLUquadric* gluNewQuadric()
    GLUtesselator* gluNewTess()
    void gluNextContour(GLUtesselator* tess, GLenum type)
    void gluNurbsCurve(GLUnurbs* nurb, GLint knotCount, GLfloat *knots, GLint stride, GLfloat *control, GLint order, GLenum type)
    void gluNurbsProperty(GLUnurbs* nurb, GLenum property, GLfloat value)
    void gluNurbsSurface(GLUnurbs* nurb, GLint sKnotCount, GLfloat* sKnots, GLint tKnotCount, GLfloat* tKnots, GLint sStride, GLint tStride, GLfloat* control, GLint sOrder, GLint tOrder, GLenum type)
    void gluOrtho2D(GLdouble left, GLdouble right, GLdouble bottom, GLdouble top)
    void gluPartialDisk(GLUquadric* quad, GLdouble inner, GLdouble outer, GLint slices, GLint loops, GLdouble start, GLdouble sweep)
    void gluPerspective(GLdouble fovy, GLdouble aspect, GLdouble zNear, GLdouble zFar)
    void gluPickMatrix(GLdouble x, GLdouble y, GLdouble delX, GLdouble delY, GLint *viewport)
    GLint gluProject(GLdouble objX, GLdouble objY, GLdouble objZ, GLdouble *model, GLdouble *proj, GLint *view, GLdouble* winX, GLdouble* winY, GLdouble* winZ)
    void gluPwlCurve(GLUnurbs* nurb, GLint count, GLfloat* data, GLint stride, GLenum type)
    void gluQuadricDrawStyle(GLUquadric* quad, GLenum draw)
    void gluQuadricNormals(GLUquadric* quad, GLenum normal)
    void gluQuadricOrientation(GLUquadric* quad, GLenum orientation)
    void gluQuadricTexture(GLUquadric* quad, GLboolean texture)
    GLint gluScaleImage(GLenum format, GLsizei wIn, GLsizei hIn, GLenum typeIn, void *dataIn, GLsizei wOut, GLsizei hOut, GLenum typeOut, GLvoid* dataOut)
    void gluSphere(GLUquadric* quad, GLdouble radius, GLint slices, GLint stacks)
    void gluTessBeginContour(GLUtesselator* tess)
    void gluTessBeginPolygon(GLUtesselator* tess, GLvoid* data)
    void gluTessEndContour(GLUtesselator* tess)
    void gluTessEndPolygon(GLUtesselator* tess)
    void gluTessNormal(GLUtesselator* tess, GLdouble valueX, GLdouble valueY, GLdouble valueZ)
    void gluTessProperty(GLUtesselator* tess, GLenum which, GLdouble data)
    void gluTessVertex(GLUtesselator* tess, GLdouble *location, GLvoid* data)
    GLint gluUnProject(GLdouble winX, GLdouble winY, GLdouble winZ, GLdouble *model, GLdouble *proj, GLint *view, GLdouble* objX, GLdouble* objY, GLdouble* objZ)
    GLint gluUnProject4(GLdouble winX, GLdouble winY, GLdouble winZ, GLdouble clipW, GLdouble *model, GLdouble *proj, GLint *view, GLdouble nearVal, GLdouble farVal, GLdouble* objX, GLdouble* objY, GLdouble* objZ, GLdouble* objW)


cdef enum:
    GL_FALSE =                              0x0
    GL_TRUE =                               0x1

    # Data types 
    GL_BYTE =                               0x1400
    GL_UNSIGNED_BYTE =                      0x1401
    GL_SHORT =                              0x1402
    GL_UNSIGNED_SHORT =                     0x1403
    GL_INT =                                0x1404
    GL_UNSIGNED_INT =                       0x1405
    GL_FLOAT =                              0x1406
    GL_DOUBLE =                             0x140A
    GL_2_BYTES =                            0x1407
    GL_3_BYTES =                            0x1408
    GL_4_BYTES =                            0x1409

    # Primitives 
    GL_POINTS =                             0x0000
    GL_LINES =                              0x0001
    GL_LINE_LOOP =                          0x0002
    GL_LINE_STRIP =                         0x0003
    GL_TRIANGLES =                          0x0004
    GL_TRIANGLE_STRIP =                     0x0005
    GL_TRIANGLE_FAN =                       0x0006
    GL_QUADS =                              0x0007
    GL_QUAD_STRIP =                         0x0008
    GL_POLYGON =                            0x0009

    # Vertex Arrays 
    GL_VERTEX_ARRAY =                       0x8074
    GL_NORMAL_ARRAY =                       0x8075
    GL_COLOR_ARRAY =                        0x8076
    GL_INDEX_ARRAY =                        0x8077
    GL_TEXTURE_COORD_ARRAY =                0x8078
    GL_EDGE_FLAG_ARRAY =                    0x8079
    GL_VERTEX_ARRAY_SIZE =                  0x807A
    GL_VERTEX_ARRAY_TYPE =                  0x807B
    GL_VERTEX_ARRAY_STRIDE =                0x807C
    GL_NORMAL_ARRAY_TYPE =                  0x807E
    GL_NORMAL_ARRAY_STRIDE =                0x807F
    GL_COLOR_ARRAY_SIZE =                   0x8081
    GL_COLOR_ARRAY_TYPE =                   0x8082
    GL_COLOR_ARRAY_STRIDE =                 0x8083
    GL_INDEX_ARRAY_TYPE =                   0x8085
    GL_INDEX_ARRAY_STRIDE =                 0x8086
    GL_TEXTURE_COORD_ARRAY_SIZE =           0x8088
    GL_TEXTURE_COORD_ARRAY_TYPE =           0x8089
    GL_TEXTURE_COORD_ARRAY_STRIDE =         0x808A
    GL_EDGE_FLAG_ARRAY_STRIDE =             0x808C
    GL_VERTEX_ARRAY_POINTER =               0x808E
    GL_NORMAL_ARRAY_POINTER =               0x808F
    GL_COLOR_ARRAY_POINTER =                0x8090
    GL_INDEX_ARRAY_POINTER =                0x8091
    GL_TEXTURE_COORD_ARRAY_POINTER =        0x8092
    GL_EDGE_FLAG_ARRAY_POINTER =            0x8093
    GL_V2F =                                0x2A20
    GL_V3F =                                0x2A21
    GL_C4UB_V2F =                           0x2A22
    GL_C4UB_V3F =                           0x2A23
    GL_C3F_V3F =                            0x2A24
    GL_N3F_V3F =                            0x2A25
    GL_C4F_N3F_V3F =                        0x2A26
    GL_T2F_V3F =                            0x2A27
    GL_T4F_V4F =                            0x2A28
    GL_T2F_C4UB_V3F =                       0x2A29
    GL_T2F_C3F_V3F =                        0x2A2A
    GL_T2F_N3F_V3F =                        0x2A2B
    GL_T2F_C4F_N3F_V3F =                    0x2A2C
    GL_T4F_C4F_N3F_V4F =                    0x2A2D

    # Matrix Mode 
    GL_MATRIX_MODE =                        0x0BA0
    GL_MODELVIEW =                          0x1700
    GL_PROJECTION =                         0x1701
    GL_TEXTURE =                            0x1702

    # Points 
    GL_POINT_SMOOTH =                       0x0B10
    GL_POINT_SIZE =                         0x0B11
    GL_POINT_SIZE_GRANULARITY =             0x0B13
    GL_POINT_SIZE_RANGE =                   0x0B12

    # Lines 
    GL_LINE_SMOOTH =                        0x0B20
    GL_LINE_STIPPLE =                       0x0B24
    GL_LINE_STIPPLE_PATTERN =               0x0B25
    GL_LINE_STIPPLE_REPEAT =                0x0B26
    GL_LINE_WIDTH =                         0x0B21
    GL_LINE_WIDTH_GRANULARITY =             0x0B23
    GL_LINE_WIDTH_RANGE =                   0x0B22

    # Polygons 
    GL_POINT =                              0x1B00
    GL_LINE =                               0x1B01
    GL_FILL =                               0x1B02
    GL_CW =                                 0x0900
    GL_CCW =                                0x0901
    GL_FRONT =                              0x0404
    GL_BACK =                               0x0405
    GL_POLYGON_MODE =                       0x0B40
    GL_POLYGON_SMOOTH =                     0x0B41
    GL_POLYGON_STIPPLE =                    0x0B42
    GL_EDGE_FLAG =                          0x0B43
    GL_CULL_FACE =                          0x0B44
    GL_CULL_FACE_MODE =                     0x0B45
    GL_FRONT_FACE =                         0x0B46
    GL_POLYGON_OFFSET_FACTOR =              0x8038
    GL_POLYGON_OFFSET_UNITS =               0x2A00
    GL_POLYGON_OFFSET_POINT =               0x2A01
    GL_POLYGON_OFFSET_LINE =                0x2A02
    GL_POLYGON_OFFSET_FILL =                0x8037

    # Display Lists 
    GL_COMPILE =                            0x1300
    GL_COMPILE_AND_EXECUTE =                0x1301
    GL_LIST_BASE =                          0x0B32
    GL_LIST_INDEX =                         0x0B33
    GL_LIST_MODE =                          0x0B30

    # Depth buffer 
    GL_NEVER =                              0x0200
    GL_LESS =                               0x0201
    GL_EQUAL =                              0x0202
    GL_LEQUAL =                             0x0203
    GL_GREATER =                            0x0204
    GL_NOTEQUAL =                           0x0205
    GL_GEQUAL =                             0x0206
    GL_ALWAYS =                             0x0207
    GL_DEPTH_TEST =                         0x0B71
    GL_DEPTH_BITS =                         0x0D56
    GL_DEPTH_CLEAR_VALUE =                  0x0B73
    GL_DEPTH_FUNC =                         0x0B74
    GL_DEPTH_RANGE =                        0x0B70
    GL_DEPTH_WRITEMASK =                    0x0B72
    GL_DEPTH_COMPONENT =                    0x1902

    # Lighting 
    GL_LIGHTING =                           0x0B50
    GL_LIGHT0 =                             0x4000
    GL_LIGHT1 =                             0x4001
    GL_LIGHT2 =                             0x4002
    GL_LIGHT3 =                             0x4003
    GL_LIGHT4 =                             0x4004
    GL_LIGHT5 =                             0x4005
    GL_LIGHT6 =                             0x4006
    GL_LIGHT7 =                             0x4007
    GL_SPOT_EXPONENT =                      0x1205
    GL_SPOT_CUTOFF =                        0x1206
    GL_CONSTANT_ATTENUATION =               0x1207
    GL_LINEAR_ATTENUATION =                 0x1208
    GL_QUADRATIC_ATTENUATION =              0x1209
    GL_AMBIENT =                            0x1200
    GL_DIFFUSE =                            0x1201
    GL_SPECULAR =                           0x1202
    GL_SHININESS =                          0x1601
    GL_EMISSION =                           0x1600
    GL_POSITION =                           0x1203
    GL_SPOT_DIRECTION =                     0x1204
    GL_AMBIENT_AND_DIFFUSE =                0x1602
    GL_COLOR_INDEXES =                      0x1603
    GL_LIGHT_MODEL_TWO_SIDE =               0x0B52
    GL_LIGHT_MODEL_LOCAL_VIEWER =           0x0B51
    GL_LIGHT_MODEL_AMBIENT =                0x0B53
    GL_FRONT_AND_BACK =                     0x0408
    GL_SHADE_MODEL =                        0x0B54
    GL_FLAT =                               0x1D00
    GL_SMOOTH =                             0x1D01
    GL_COLOR_MATERIAL =                     0x0B57
    GL_COLOR_MATERIAL_FACE =                0x0B55
    GL_COLOR_MATERIAL_PARAMETER =           0x0B56
    GL_NORMALIZE =                          0x0BA1

    # User clipping planes 
    GL_CLIP_PLANE0 =                        0x3000
    GL_CLIP_PLANE1 =                        0x3001
    GL_CLIP_PLANE2 =                        0x3002
    GL_CLIP_PLANE3 =                        0x3003
    GL_CLIP_PLANE4 =                        0x3004
    GL_CLIP_PLANE5 =                        0x3005

    # Accumulation buffer 
    GL_ACCUM_RED_BITS =                     0x0D58
    GL_ACCUM_GREEN_BITS =                   0x0D59
    GL_ACCUM_BLUE_BITS =                    0x0D5A
    GL_ACCUM_ALPHA_BITS =                   0x0D5B
    GL_ACCUM_CLEAR_VALUE =                  0x0B80
    GL_ACCUM =                              0x0100
    GL_ADD =                                0x0104
    GL_LOAD =                               0x0101
    GL_MULT =                               0x0103
    GL_RETURN =                             0x0102

    # Alpha testing 
    GL_ALPHA_TEST =                         0x0BC0
    GL_ALPHA_TEST_REF =                     0x0BC2
    GL_ALPHA_TEST_FUNC =                    0x0BC1

    # Blending 
    GL_BLEND =                              0x0BE2
    GL_BLEND_SRC =                          0x0BE1
    GL_BLEND_DST =                          0x0BE0
    GL_ZERO =                               0x0
    GL_ONE =                                0x1
    GL_SRC_COLOR =                          0x0300
    GL_ONE_MINUS_SRC_COLOR =                0x0301
    GL_SRC_ALPHA =                          0x0302
    GL_ONE_MINUS_SRC_ALPHA =                0x0303
    GL_DST_ALPHA =                          0x0304
    GL_ONE_MINUS_DST_ALPHA =                0x0305
    GL_DST_COLOR =                          0x0306
    GL_ONE_MINUS_DST_COLOR =                0x0307
    GL_SRC_ALPHA_SATURATE =                 0x0308
    GL_CONSTANT_COLOR =                     0x8001
    GL_ONE_MINUS_CONSTANT_COLOR =           0x8002
    GL_CONSTANT_ALPHA =                     0x8003
    GL_ONE_MINUS_CONSTANT_ALPHA =           0x8004

    # Render Mode 
    GL_FEEDBACK =                           0x1C01
    GL_RENDER =                             0x1C00
    GL_SELECT =                             0x1C02

    # Feedback 
    GL_2D =                                 0x0600
    GL_3D =                                 0x0601
    GL_3D_COLOR =                           0x0602
    GL_3D_COLOR_TEXTURE =                   0x0603
    GL_4D_COLOR_TEXTURE =                   0x0604
    GL_POINT_TOKEN =                        0x0701
    GL_LINE_TOKEN =                         0x0702
    GL_LINE_RESET_TOKEN =                   0x0707
    GL_POLYGON_TOKEN =                      0x0703
    GL_BITMAP_TOKEN =                       0x0704
    GL_DRAW_PIXEL_TOKEN =                   0x0705
    GL_COPY_PIXEL_TOKEN =                   0x0706
    GL_PASS_THROUGH_TOKEN =                 0x0700
    GL_FEEDBACK_BUFFER_POINTER =            0x0DF0
    GL_FEEDBACK_BUFFER_SIZE =               0x0DF1
    GL_FEEDBACK_BUFFER_TYPE =               0x0DF2

    # Selection 
    GL_SELECTION_BUFFER_POINTER =           0x0DF3
    GL_SELECTION_BUFFER_SIZE =              0x0DF4

    # Fog 
    GL_FOG =                                0x0B60
    GL_FOG_MODE =                           0x0B65
    GL_FOG_DENSITY =                        0x0B62
    GL_FOG_COLOR =                          0x0B66
    GL_FOG_INDEX =                          0x0B61
    GL_FOG_START =                          0x0B63
    GL_FOG_END =                            0x0B64
    GL_LINEAR =                             0x2601
    GL_EXP =                                0x0800
    GL_EXP2 =                               0x0801

    # Logic Ops 
    GL_LOGIC_OP =                           0x0BF1
    GL_INDEX_LOGIC_OP =                     0x0BF1
    GL_COLOR_LOGIC_OP =                     0x0BF2
    GL_LOGIC_OP_MODE =                      0x0BF0
    GL_CLEAR =                              0x1500
    GL_SET =                                0x150F
    GL_COPY =                               0x1503
    GL_COPY_INVERTED =                      0x150C
    GL_NOOP =                               0x1505
    GL_INVERT =                             0x150A
    GL_AND =                                0x1501
    GL_NAND =                               0x150E
    GL_OR =                                 0x1507
    GL_NOR =                                0x1508
    GL_XOR =                                0x1506
    GL_EQUIV =                              0x1509
    GL_AND_REVERSE =                        0x1502
    GL_AND_INVERTED =                       0x1504
    GL_OR_REVERSE =                         0x150B
    GL_OR_INVERTED =                        0x150D

    # Stencil 
    GL_STENCIL_TEST =                       0x0B90
    GL_STENCIL_WRITEMASK =                  0x0B98
    GL_STENCIL_BITS =                       0x0D57
    GL_STENCIL_FUNC =                       0x0B92
    GL_STENCIL_VALUE_MASK =                 0x0B93
    GL_STENCIL_REF =                        0x0B97
    GL_STENCIL_FAIL =                       0x0B94
    GL_STENCIL_PASS_DEPTH_PASS =            0x0B96
    GL_STENCIL_PASS_DEPTH_FAIL =            0x0B95
    GL_STENCIL_CLEAR_VALUE =                0x0B91
    GL_STENCIL_INDEX =                      0x1901
    GL_KEEP =                               0x1E00
    GL_REPLACE =                            0x1E01
    GL_INCR =                               0x1E02
    GL_DECR =                               0x1E03

    # Buffers, Pixel Drawing/Reading 
    GL_NONE =                               0x0
    GL_LEFT =                               0x0406
    GL_RIGHT =                              0x0407
    #GL_FRONT                               0x0404 
    #GL_BACK                                0x0405 
    #GL_FRONT_AND_BACK                      0x0408 
    GL_FRONT_LEFT =                         0x0400
    GL_FRONT_RIGHT =                        0x0401
    GL_BACK_LEFT =                          0x0402
    GL_BACK_RIGHT =                         0x0403
    GL_AUX0 =                               0x0409
    GL_AUX1 =                               0x040A
    GL_AUX2 =                               0x040B
    GL_AUX3 =                               0x040C
    GL_COLOR_INDEX =                        0x1900
    GL_RED =                                0x1903
    GL_GREEN =                              0x1904
    GL_BLUE =                               0x1905
    GL_ALPHA =                              0x1906
    GL_LUMINANCE =                          0x1909
    GL_LUMINANCE_ALPHA =                    0x190A
    GL_ALPHA_BITS =                         0x0D55
    GL_RED_BITS =                           0x0D52
    GL_GREEN_BITS =                         0x0D53
    GL_BLUE_BITS =                          0x0D54
    GL_INDEX_BITS =                         0x0D51
    GL_SUBPIXEL_BITS =                      0x0D50
    GL_AUX_BUFFERS =                        0x0C00
    GL_READ_BUFFER =                        0x0C02
    GL_DRAW_BUFFER =                        0x0C01
    GL_DOUBLEBUFFER =                       0x0C32
    GL_STEREO =                             0x0C33
    GL_BITMAP =                             0x1A00
    GL_COLOR =                              0x1800
    GL_DEPTH =                              0x1801
    GL_STENCIL =                            0x1802
    GL_DITHER =                             0x0BD0
    GL_RGB =                                0x1907
    GL_RGBA =                               0x1908

    # Implementation limits 
    GL_MAX_LIST_NESTING =                   0x0B31
    GL_MAX_ATTRIB_STACK_DEPTH =             0x0D35
    GL_MAX_MODELVIEW_STACK_DEPTH =          0x0D36
    GL_MAX_NAME_STACK_DEPTH =               0x0D37
    GL_MAX_PROJECTION_STACK_DEPTH =         0x0D38
    GL_MAX_TEXTURE_STACK_DEPTH =            0x0D39
    GL_MAX_EVAL_ORDER =                     0x0D30
    GL_MAX_LIGHTS =                         0x0D31
    GL_MAX_CLIP_PLANES =                    0x0D32
    GL_MAX_TEXTURE_SIZE =                   0x0D33
    GL_MAX_PIXEL_MAP_TABLE =                0x0D34
    GL_MAX_VIEWPORT_DIMS =                  0x0D3A
    GL_MAX_CLIENT_ATTRIB_STACK_DEPTH =      0x0D3B

    # Gets 
    GL_ATTRIB_STACK_DEPTH =                 0x0BB0
    GL_CLIENT_ATTRIB_STACK_DEPTH =          0x0BB1
    GL_COLOR_CLEAR_VALUE =                  0x0C22
    GL_COLOR_WRITEMASK =                    0x0C23
    GL_CURRENT_INDEX =                      0x0B01
    GL_CURRENT_COLOR =                      0x0B00
    GL_CURRENT_NORMAL =                     0x0B02
    GL_CURRENT_RASTER_COLOR =               0x0B04
    GL_CURRENT_RASTER_DISTANCE =            0x0B09
    GL_CURRENT_RASTER_INDEX =               0x0B05
    GL_CURRENT_RASTER_POSITION =            0x0B07
    GL_CURRENT_RASTER_TEXTURE_COORDS =      0x0B06
    GL_CURRENT_RASTER_POSITION_VALID =      0x0B08
    GL_CURRENT_TEXTURE_COORDS =             0x0B03
    GL_INDEX_CLEAR_VALUE =                  0x0C20
    GL_INDEX_MODE =                         0x0C30
    GL_INDEX_WRITEMASK =                    0x0C21
    GL_MODELVIEW_MATRIX =                   0x0BA6
    GL_MODELVIEW_STACK_DEPTH =              0x0BA3
    GL_NAME_STACK_DEPTH =                   0x0D70
    GL_PROJECTION_MATRIX =                  0x0BA7
    GL_PROJECTION_STACK_DEPTH =             0x0BA4
    GL_RENDER_MODE =                        0x0C40
    GL_RGBA_MODE =                          0x0C31
    GL_TEXTURE_MATRIX =                     0x0BA8
    GL_TEXTURE_STACK_DEPTH =                0x0BA5
    GL_VIEWPORT =                           0x0BA2

    # Evaluators 
    GL_AUTO_NORMAL =                        0x0D80
    GL_MAP1_COLOR_4 =                       0x0D90
    GL_MAP1_GRID_DOMAIN =                   0x0DD0
    GL_MAP1_GRID_SEGMENTS =                 0x0DD1
    GL_MAP1_INDEX =                         0x0D91
    GL_MAP1_NORMAL =                        0x0D92
    GL_MAP1_TEXTURE_COORD_1 =               0x0D93
    GL_MAP1_TEXTURE_COORD_2 =               0x0D94
    GL_MAP1_TEXTURE_COORD_3 =               0x0D95
    GL_MAP1_TEXTURE_COORD_4 =               0x0D96
    GL_MAP1_VERTEX_3 =                      0x0D97
    GL_MAP1_VERTEX_4 =                      0x0D98
    GL_MAP2_COLOR_4 =                       0x0DB0
    GL_MAP2_GRID_DOMAIN =                   0x0DD2
    GL_MAP2_GRID_SEGMENTS =                 0x0DD3
    GL_MAP2_INDEX =                         0x0DB1
    GL_MAP2_NORMAL =                        0x0DB2
    GL_MAP2_TEXTURE_COORD_1 =               0x0DB3
    GL_MAP2_TEXTURE_COORD_2 =               0x0DB4
    GL_MAP2_TEXTURE_COORD_3 =               0x0DB5
    GL_MAP2_TEXTURE_COORD_4 =               0x0DB6
    GL_MAP2_VERTEX_3 =                      0x0DB7
    GL_MAP2_VERTEX_4 =                      0x0DB8
    GL_COEFF =                              0x0A00
    GL_DOMAIN =                             0x0A02
    GL_ORDER =                              0x0A01

    # Hints 
    GL_FOG_HINT =                           0x0C54
    GL_LINE_SMOOTH_HINT =                   0x0C52
    GL_PERSPECTIVE_CORRECTION_HINT =        0x0C50
    GL_POINT_SMOOTH_HINT =                  0x0C51
    GL_POLYGON_SMOOTH_HINT =                0x0C53
    GL_DONT_CARE =                          0x1100
    GL_FASTEST =                            0x1101
    GL_NICEST =                             0x1102

    # Scissor box 
    GL_SCISSOR_TEST =                       0x0C11
    GL_SCISSOR_BOX =                        0x0C10

    # Pixel Mode / Transfer 
    GL_MAP_COLOR =                          0x0D10
    GL_MAP_STENCIL =                        0x0D11
    GL_INDEX_SHIFT =                        0x0D12
    GL_INDEX_OFFSET =                       0x0D13
    GL_RED_SCALE =                          0x0D14
    GL_RED_BIAS =                           0x0D15
    GL_GREEN_SCALE =                        0x0D18
    GL_GREEN_BIAS =                         0x0D19
    GL_BLUE_SCALE =                         0x0D1A
    GL_BLUE_BIAS =                          0x0D1B
    GL_ALPHA_SCALE =                        0x0D1C
    GL_ALPHA_BIAS =                         0x0D1D
    GL_DEPTH_SCALE =                        0x0D1E
    GL_DEPTH_BIAS =                         0x0D1F
    GL_PIXEL_MAP_S_TO_S_SIZE =              0x0CB1
    GL_PIXEL_MAP_I_TO_I_SIZE =              0x0CB0
    GL_PIXEL_MAP_I_TO_R_SIZE =              0x0CB2
    GL_PIXEL_MAP_I_TO_G_SIZE =              0x0CB3
    GL_PIXEL_MAP_I_TO_B_SIZE =              0x0CB4
    GL_PIXEL_MAP_I_TO_A_SIZE =              0x0CB5
    GL_PIXEL_MAP_R_TO_R_SIZE =              0x0CB6
    GL_PIXEL_MAP_G_TO_G_SIZE =              0x0CB7
    GL_PIXEL_MAP_B_TO_B_SIZE =              0x0CB8
    GL_PIXEL_MAP_A_TO_A_SIZE =              0x0CB9
    GL_PIXEL_MAP_S_TO_S =                   0x0C71
    GL_PIXEL_MAP_I_TO_I =                   0x0C70
    GL_PIXEL_MAP_I_TO_R =                   0x0C72
    GL_PIXEL_MAP_I_TO_G =                   0x0C73
    GL_PIXEL_MAP_I_TO_B =                   0x0C74
    GL_PIXEL_MAP_I_TO_A =                   0x0C75
    GL_PIXEL_MAP_R_TO_R =                   0x0C76
    GL_PIXEL_MAP_G_TO_G =                   0x0C77
    GL_PIXEL_MAP_B_TO_B =                   0x0C78
    GL_PIXEL_MAP_A_TO_A =                   0x0C79
    GL_PACK_ALIGNMENT =                     0x0D05
    GL_PACK_LSB_FIRST =                     0x0D01
    GL_PACK_ROW_LENGTH =                    0x0D02
    GL_PACK_SKIP_PIXELS =                   0x0D04
    GL_PACK_SKIP_ROWS =                     0x0D03
    GL_PACK_SWAP_BYTES =                    0x0D00
    GL_UNPACK_ALIGNMENT =                   0x0CF5
    GL_UNPACK_LSB_FIRST =                   0x0CF1
    GL_UNPACK_ROW_LENGTH =                  0x0CF2
    GL_UNPACK_SKIP_PIXELS =                 0x0CF4
    GL_UNPACK_SKIP_ROWS =                   0x0CF3
    GL_UNPACK_SWAP_BYTES =                  0x0CF0
    GL_ZOOM_X =                             0x0D16
    GL_ZOOM_Y =                             0x0D17

    # Texture mapping 
    GL_TEXTURE_ENV =                        0x2300
    GL_TEXTURE_ENV_MODE =                   0x2200
    GL_TEXTURE_1D =                         0x0DE0
    GL_TEXTURE_2D =                         0x0DE1
    GL_TEXTURE_WRAP_S =                     0x2802
    GL_TEXTURE_WRAP_T =                     0x2803
    GL_TEXTURE_MAG_FILTER =                 0x2800
    GL_TEXTURE_MIN_FILTER =                 0x2801
    GL_TEXTURE_ENV_COLOR =                  0x2201
    GL_TEXTURE_GEN_S =                      0x0C60
    GL_TEXTURE_GEN_T =                      0x0C61
    GL_TEXTURE_GEN_MODE =                   0x2500
    GL_TEXTURE_BORDER_COLOR =               0x1004
    GL_TEXTURE_WIDTH =                      0x1000
    GL_TEXTURE_HEIGHT =                     0x1001
    GL_TEXTURE_BORDER =                     0x1005
    GL_TEXTURE_COMPONENTS =                 0x1003
    GL_TEXTURE_RED_SIZE =                   0x805C
    GL_TEXTURE_GREEN_SIZE =                 0x805D
    GL_TEXTURE_BLUE_SIZE =                  0x805E
    GL_TEXTURE_ALPHA_SIZE =                 0x805F
    GL_TEXTURE_LUMINANCE_SIZE =             0x8060
    GL_TEXTURE_INTENSITY_SIZE =             0x8061
    GL_NEAREST_MIPMAP_NEAREST =             0x2700
    GL_NEAREST_MIPMAP_LINEAR =              0x2702
    GL_LINEAR_MIPMAP_NEAREST =              0x2701
    GL_LINEAR_MIPMAP_LINEAR =               0x2703
    GL_OBJECT_LINEAR =                      0x2401
    GL_OBJECT_PLANE =                       0x2501
    GL_EYE_LINEAR =                         0x2400
    GL_EYE_PLANE =                          0x2502
    GL_SPHERE_MAP =                         0x2402
    GL_DECAL =                              0x2101
    GL_MODULATE =                           0x2100
    GL_NEAREST =                            0x2600
    GL_REPEAT =                             0x2901
    GL_CLAMP =                              0x2900
    GL_S =                                  0x2000
    GL_T =                                  0x2001
    GL_R =                                  0x2002
    GL_Q =                                  0x2003
    GL_TEXTURE_GEN_R =                      0x0C62
    GL_TEXTURE_GEN_Q =                      0x0C63

    # Utility 
    GL_VENDOR =                             0x1F00
    GL_RENDERER =                           0x1F01
    GL_VERSION =                            0x1F02
    GL_EXTENSIONS =                         0x1F03

    # Errors 
    GL_NO_ERROR =                           0x0
    GL_INVALID_VALUE =                      0x0501
    GL_INVALID_ENUM =                       0x0500
    GL_INVALID_OPERATION =                  0x0502
    GL_STACK_OVERFLOW =                     0x0503
    GL_STACK_UNDERFLOW =                    0x0504
    GL_OUT_OF_MEMORY =                      0x0505

    # glPush/PopAttrib bits 
    GL_CURRENT_BIT =                        0x00000001
    GL_POINT_BIT =                          0x00000002
    GL_LINE_BIT =                           0x00000004
    GL_POLYGON_BIT =                        0x00000008
    GL_POLYGON_STIPPLE_BIT =                0x00000010
    GL_PIXEL_MODE_BIT =                     0x00000020
    GL_LIGHTING_BIT =                       0x00000040
    GL_FOG_BIT =                            0x00000080
    GL_DEPTH_BUFFER_BIT =                   0x00000100
    GL_ACCUM_BUFFER_BIT =                   0x00000200
    GL_STENCIL_BUFFER_BIT =                 0x00000400
    GL_VIEWPORT_BIT =                       0x00000800
    GL_TRANSFORM_BIT =                      0x00001000
    GL_ENABLE_BIT =                         0x00002000
    GL_COLOR_BUFFER_BIT =                   0x00004000
    GL_HINT_BIT =                           0x00008000
    GL_EVAL_BIT =                           0x00010000
    GL_LIST_BIT =                           0x00020000
    GL_TEXTURE_BIT =                        0x00040000
    GL_SCISSOR_BIT =                        0x00080000
    GL_ALL_ATTRIB_BITS =                    0x000FFFFF


    # OpenGL 1.1 
    GL_PROXY_TEXTURE_1D =                   0x8063
    GL_PROXY_TEXTURE_2D =                   0x8064
    GL_TEXTURE_PRIORITY =                   0x8066
    GL_TEXTURE_RESIDENT =                   0x8067
    GL_TEXTURE_BINDING_1D =                 0x8068
    GL_TEXTURE_BINDING_2D =                 0x8069
    GL_TEXTURE_INTERNAL_FORMAT =            0x1003
    GL_ALPHA4 =                             0x803B
    GL_ALPHA8 =                             0x803C
    GL_ALPHA12 =                            0x803D
    GL_ALPHA16 =                            0x803E
    GL_LUMINANCE4 =                         0x803F
    GL_LUMINANCE8 =                         0x8040
    GL_LUMINANCE12 =                        0x8041
    GL_LUMINANCE16 =                        0x8042
    GL_LUMINANCE4_ALPHA4 =                  0x8043
    GL_LUMINANCE6_ALPHA2 =                  0x8044
    GL_LUMINANCE8_ALPHA8 =                  0x8045
    GL_LUMINANCE12_ALPHA4 =                 0x8046
    GL_LUMINANCE12_ALPHA12 =                0x8047
    GL_LUMINANCE16_ALPHA16 =                0x8048
    GL_INTENSITY =                          0x8049
    GL_INTENSITY4 =                         0x804A
    GL_INTENSITY8 =                         0x804B
    GL_INTENSITY12 =                        0x804C
    GL_INTENSITY16 =                        0x804D
    GL_R3_G3_B2 =                           0x2A10
    GL_RGB4 =                               0x804F
    GL_RGB5 =                               0x8050
    GL_RGB8 =                               0x8051
    GL_RGB10 =                              0x8052
    GL_RGB12 =                              0x8053
    GL_RGB16 =                              0x8054
    GL_RGBA2 =                              0x8055
    GL_RGBA4 =                              0x8056
    GL_RGB5_A1 =                            0x8057
    GL_RGBA8 =                              0x8058
    GL_RGB10_A2 =                           0x8059
    GL_RGBA12 =                             0x805A
    GL_RGBA16 =                             0x805B
    GL_CLIENT_PIXEL_STORE_BIT =             0x00000001
    GL_CLIENT_VERTEX_ARRAY_BIT =            0x00000002
    GL_ALL_CLIENT_ATTRIB_BITS =             0xFFFFFFFF
    GL_CLIENT_ALL_ATTRIB_BITS =             0xFFFFFFFF

    # Boolean
    GLU_FALSE =                        0
    GLU_TRUE =                         1

    # StringName
    GLU_VERSION =                      100800
    GLU_EXTENSIONS =                   100801

    # ErrorCode
    GLU_INVALID_ENUM =                 100900
    GLU_INVALID_VALUE =                100901
    GLU_OUT_OF_MEMORY =                100902
    GLU_INVALID_OPERATION =            100904

    # NurbsDisplay
    #      GLU_FILL
    GLU_OUTLINE_POLYGON =              100240
    GLU_OUTLINE_PATCH =                100241

    # NurbsError
    GLU_NURBS_ERROR1 =                 100251
    GLU_NURBS_ERROR2 =                 100252
    GLU_NURBS_ERROR3 =                 100253
    GLU_NURBS_ERROR4 =                 100254
    GLU_NURBS_ERROR5 =                 100255
    GLU_NURBS_ERROR6 =                 100256
    GLU_NURBS_ERROR7 =                 100257
    GLU_NURBS_ERROR8 =                 100258
    GLU_NURBS_ERROR9 =                 100259
    GLU_NURBS_ERROR10 =                100260
    GLU_NURBS_ERROR11 =                100261
    GLU_NURBS_ERROR12 =                100262
    GLU_NURBS_ERROR13 =                100263
    GLU_NURBS_ERROR14 =                100264
    GLU_NURBS_ERROR15 =                100265
    GLU_NURBS_ERROR16 =                100266
    GLU_NURBS_ERROR17 =                100267
    GLU_NURBS_ERROR18 =                100268
    GLU_NURBS_ERROR19 =                100269
    GLU_NURBS_ERROR20 =                100270
    GLU_NURBS_ERROR21 =                100271
    GLU_NURBS_ERROR22 =                100272
    GLU_NURBS_ERROR23 =                100273
    GLU_NURBS_ERROR24 =                100274
    GLU_NURBS_ERROR25 =                100275
    GLU_NURBS_ERROR26 =                100276
    GLU_NURBS_ERROR27 =                100277
    GLU_NURBS_ERROR28 =                100278
    GLU_NURBS_ERROR29 =                100279
    GLU_NURBS_ERROR30 =                100280
    GLU_NURBS_ERROR31 =                100281
    GLU_NURBS_ERROR32 =                100282
    GLU_NURBS_ERROR33 =                100283
    GLU_NURBS_ERROR34 =                100284
    GLU_NURBS_ERROR35 =                100285
    GLU_NURBS_ERROR36 =                100286
    GLU_NURBS_ERROR37 =                100287

    # NurbsProperty
    GLU_AUTO_LOAD_MATRIX =             100200
    GLU_CULLING =                      100201
    GLU_SAMPLING_TOLERANCE =           100203
    GLU_DISPLAY_MODE =                 100204
    GLU_PARAMETRIC_TOLERANCE =         100202
    GLU_SAMPLING_METHOD =              100205
    GLU_U_STEP =                       100206
    GLU_V_STEP =                       100207

    # NurbsSampling
    GLU_PATH_LENGTH =                  100215
    GLU_PARAMETRIC_ERROR =             100216
    GLU_DOMAIN_DISTANCE =              100217

    # NurbsTrim
    GLU_MAP1_TRIM_2 =                  100210
    GLU_MAP1_TRIM_3 =                  100211

    # QuadricDrawStyle
    GLU_POINT =                        100010
    GLU_LINE =                         100011
    GLU_FILL =                         100012
    GLU_SILHOUETTE =                   100013

    # QuadricCallback
    GLU_ERROR =                        100103

    # QuadricNormal
    GLU_SMOOTH =                       100000
    GLU_FLAT =                         100001
    GLU_NONE =                         100002

    # QuadricOrientation
    GLU_OUTSIDE =                      100020
    GLU_INSIDE =                       100021

    # TessCallback
    GLU_TESS_BEGIN =                   100100
    GLU_BEGIN =                        100100
    GLU_TESS_VERTEX =                  100101
    GLU_VERTEX =                       100101
    GLU_TESS_END =                     100102
    GLU_END =                          100102
    GLU_TESS_ERROR =                   100103
    GLU_TESS_EDGE_FLAG =               100104
    GLU_EDGE_FLAG =                    100104
    GLU_TESS_COMBINE =                 100105
    GLU_TESS_BEGIN_DATA =              100106
    GLU_TESS_VERTEX_DATA =             100107
    GLU_TESS_END_DATA =                100108
    GLU_TESS_ERROR_DATA =              100109
    GLU_TESS_EDGE_FLAG_DATA =          100110
    GLU_TESS_COMBINE_DATA =            100111

    # TessContour
    GLU_CW =                           100120
    GLU_CCW =                          100121
    GLU_INTERIOR =                     100122
    GLU_EXTERIOR =                     100123
    GLU_UNKNOWN =                      100124

    # TessProperty
    GLU_TESS_WINDING_RULE =            100140
    GLU_TESS_BOUNDARY_ONLY =           100141
    GLU_TESS_TOLERANCE =               100142

    # TessError
    GLU_TESS_ERROR1 =                  100151
    GLU_TESS_ERROR2 =                  100152
    GLU_TESS_ERROR3 =                  100153
    GLU_TESS_ERROR4 =                  100154
    GLU_TESS_ERROR5 =                  100155
    GLU_TESS_ERROR6 =                  100156
    GLU_TESS_ERROR7 =                  100157
    GLU_TESS_ERROR8 =                  100158
    GLU_TESS_MISSING_BEGIN_POLYGON =   100151
    GLU_TESS_MISSING_BEGIN_CONTOUR =   100152
    GLU_TESS_MISSING_END_POLYGON =     100153
    GLU_TESS_MISSING_END_CONTOUR =     100154
    GLU_TESS_COORD_TOO_LARGE =         100155
    GLU_TESS_NEED_COMBINE_CALLBACK =   100156

    # TessWinding
    GLU_TESS_WINDING_ODD =             100130
    GLU_TESS_WINDING_NONZERO =         100131
    GLU_TESS_WINDING_POSITIVE =        100132
    GLU_TESS_WINDING_NEGATIVE =        100133
    GLU_TESS_WINDING_ABS_GEQ_TWO =     100134

cdef float GLU_TESS_MAX_COORD = 1.0e150