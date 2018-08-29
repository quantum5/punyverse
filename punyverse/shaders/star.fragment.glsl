#version 330 core

in vec2 v_uv;
out vec4 o_fragColor;
uniform sampler2D u_emission;

void main() {
    o_fragColor = vec4(texture(u_emission, v_uv).rgb, 1);
}
