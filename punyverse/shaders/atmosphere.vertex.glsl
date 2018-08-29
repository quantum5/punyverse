#version 330 core

in vec2 a_position;
in float a_u;

out float v_u;

uniform mat4 u_mvpMatrix;

void main() {
    gl_Position = u_mvpMatrix * vec4(a_position, 0, 1);
    v_u = a_u;
}
