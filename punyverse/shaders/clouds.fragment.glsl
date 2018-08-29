#version 330 core

in vec2 v_uv;
in vec3 v_normal;
in vec3 v_position;

out vec4 o_fragColor;

uniform vec3 u_ambient;
uniform vec3 u_diffuse;
uniform vec3 u_sun;
uniform sampler2D u_transparency;

void main() {
    vec3 incident = normalize(u_sun - v_position);
    vec3 diffuse = u_diffuse * clamp(dot(v_normal, incident) + 0.2, 0.0, 1.0);

    o_fragColor = vec4(u_ambient + diffuse, texture(u_transparency, v_uv).r);
}
