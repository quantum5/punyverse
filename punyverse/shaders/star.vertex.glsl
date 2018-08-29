#version 330 core

in vec3 a_normal;
in vec2 a_uv;

out vec2 v_uv;

uniform float u_radius;
uniform mat4 u_mvpMatrix;

void main() {
    gl_Position = u_mvpMatrix * vec4(u_radius * a_normal, 1);
    v_uv = a_uv;
}
