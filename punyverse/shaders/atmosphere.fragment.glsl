#version 330 core

in float v_u;

out vec4 o_fragColor;

uniform vec3 u_color;
uniform sampler1D u_transparency;

void main() {
    o_fragColor = vec4(u_color, texture(u_transparency, v_u).r);
}
