#version 330 core

in vec2 a_rc;
in vec2 a_tex;

out vec2 v_uv;

uniform mat4 u_projMatrix;
uniform vec2 u_start;

void main() {
    gl_Position = u_projMatrix * vec4(a_rc.y * 8 + u_start.x, a_rc.x * 16 + u_start.y, 0, 1);
    v_uv = vec2(a_tex.x * 8 / 1024, a_tex.y);
}
