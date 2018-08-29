#version 330 core

in vec3 v_direction;
out vec4 o_fragColor;
uniform bool u_lines;
uniform samplerCube u_skysphere;
uniform samplerCube u_constellation;

void main() {
    o_fragColor = texture(u_skysphere, v_direction);
    if (u_lines)
        o_fragColor += texture(u_constellation, v_direction);
}
