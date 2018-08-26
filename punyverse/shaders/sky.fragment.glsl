#version 130

in vec2 v_uv;
out vec4 o_fragColor;
uniform sampler2D u_skysphere;

void main() {
    o_fragColor = vec4(texture(u_skysphere, v_uv).rgb, 1);
}
