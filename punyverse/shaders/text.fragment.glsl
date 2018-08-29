#version 330 core

in vec2 v_uv;

out vec4 o_fragColor;

uniform sampler2D u_alpha;
uniform vec3 u_color;

void main() {
    o_fragColor = vec4(u_color, texture(u_alpha, v_uv).r);
}
