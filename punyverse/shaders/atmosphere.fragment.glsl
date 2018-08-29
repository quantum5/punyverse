#version 330 core

in float v_u;

out vec4 o_fragColor;
uniform sampler1D u_texture;

void main() {
    o_fragColor = texture(u_texture, v_u);
}
