#version 130

in vec2 v_uv;
out vec4 o_fragColor;
uniform sampler2D u_skysphere;

void main() {
    o_fragColor = vec4(texture(u_skysphere, vec2(1 - v_uv.s, v_uv.t)).rgb, 1);
}
