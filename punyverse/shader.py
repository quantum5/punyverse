from __future__ import print_function

import os
import sys
from ctypes import pointer, byref, create_string_buffer, POINTER, cast

from pyglet.gl import *
# noinspection PyUnresolvedReferences
from six.moves import range

SHADERS_DIR = os.path.join(os.path.dirname(__file__), 'shaders')


class CompileError(ValueError):
    pass


class glShader(object):
    def __init__(self, type):
        self.type = type

    def __enter__(self):
        self.shader = glCreateShader(self.type)
        return self.shader

    def __exit__(self, exc_type, exc_val, exc_tb):
        glDeleteShader(self.shader)


class Program(object):
    @classmethod
    def load_file(cls, file):
        with open(os.path.join(SHADERS_DIR, file), 'rb') as f:
            return f.read()

    @classmethod
    def compile_shader(cls, shader, source):
        buffer = create_string_buffer(source)
        glShaderSource(shader, 1, cast(pointer(pointer(buffer)), POINTER(POINTER(GLchar))), None)
        glCompileShader(shader)

        succeeded = GLint()
        log_length = GLint()
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(succeeded))
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(log_length))
        buffer = create_string_buffer(log_length.value + 1)
        glGetShaderInfoLog(shader, log_length.value, None, buffer)

        if not succeeded:
            raise CompileError(buffer.value.decode('utf-8'))
        elif log_length.value:
            print('Warning:', file=sys.stderr)
            print(buffer.value.decode('utf-8'), file=sys.stderr)

    def __init__(self, vertex_file, fragment_file):
        with glShader(GL_VERTEX_SHADER) as vertex_shader, glShader(GL_FRAGMENT_SHADER) as fragment_shader:
            self.compile_shader(vertex_shader, self.load_file(vertex_file))
            self.compile_shader(fragment_shader, self.load_file(fragment_file))

            program = glCreateProgram()
            glAttachShader(program, vertex_shader)
            glAttachShader(program, fragment_shader)
            glLinkProgram(program)

            succeeded = GLint()
            log_length = GLint()
            glGetProgramiv(program, GL_LINK_STATUS, byref(succeeded))
            if not succeeded:
                glGetProgramiv(program, GL_INFO_LOG_LENGTH, byref(log_length))
                buffer = create_string_buffer(log_length.value + 1)
                glGetProgramInfoLog(program, log_length.value, None, buffer)
                glDeleteProgram(program)
                raise CompileError(buffer.value)

            glDetachShader(program, vertex_shader)
            glDetachShader(program, fragment_shader)

        self.program = program
        self.attributes = self._variable_locations(GL_ACTIVE_ATTRIBUTES, glGetActiveAttrib, glGetAttribLocation)
        self.uniforms = self._variable_locations(GL_ACTIVE_UNIFORMS, glGetActiveUniform, glGetUniformLocation)

    def vertex_attribute(self, name, size, type, normalized, stride, offset, divisor=None):
        location = self.attributes[name]
        glVertexAttribPointer(location, size, type, normalized, stride, offset)
        glEnableVertexAttribArray(location)
        if divisor:
            glVertexAttribDivisor(location, divisor)

    def vertex_attribute_vec2(self, name, a, b):
        glVertexAttrib2f(self.attributes[name], a, b)

    def vertex_attribute_vec3(self, name, a, b, c):
        glVertexAttrib3f(self.attributes[name], a, b, c)

    def uniform_mat4(self, name, matrix):
        glUniformMatrix4fv(self.uniforms[name], 1, GL_FALSE, matrix)

    def uniform_texture(self, name, index):
        glUniform1i(self.uniforms[name], index)

    def uniform_float(self, name, value):
        glUniform1f(self.uniforms[name], value)

    def uniform_bool(self, name, value):
        glUniform1i(self.uniforms[name], bool(value))

    def uniform_vec2(self, name, a, b):
        glUniform2f(self.uniforms[name], a, b)

    def uniform_vec3(self, name, a, b, c):
        glUniform3f(self.uniforms[name], a, b, c)

    def uniform_vec4(self, name, a, b, c, d):
        glUniform4f(self.uniforms[name], a, b, c, d)

    def _variable_locations(self, count_type, get_func, loc_func):
        variables = {}
        count = GLint()
        glGetProgramiv(self.program, count_type, byref(count))
        buffer = create_string_buffer(256)
        size = GLint()
        type = GLenum()

        for index in range(count.value):
            get_func(self.program, index, 256, None, byref(size), byref(type), buffer)
            variables[buffer.value.decode('ascii')] = loc_func(self.program, buffer)
        return variables
