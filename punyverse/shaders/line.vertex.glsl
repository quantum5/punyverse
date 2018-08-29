#version 130

in vec3 a_position;
uniform mat4 u_mvpMatrix;

void main() {
    gl_Position = u_mvpMatrix * vec4(a_position, 1);
}
