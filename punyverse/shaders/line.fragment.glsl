#version 130

out vec4 o_fragColor;
uniform vec4 u_color;

void main() {
    o_fragColor = u_color;
}
