#version 130

in vec3 v_position;
in float v_u;

out vec4 o_fragColor;

uniform vec3 u_sun;
uniform vec3 u_planet;
uniform float u_planetRadius;
uniform float u_ambient;
uniform sampler2D u_texture;

void main() {
    vec3 incident = v_position - u_sun;
    vec3 plane_normal = u_planet - u_sun;
    vec3 plane_intersect = dot(plane_normal, plane_normal) / dot(incident, plane_normal) * incident;
    o_fragColor = texture(u_texture, vec2(v_u, 0));
    if (length(plane_intersect) < length(incident) &&
        distance(plane_intersect, plane_normal) <= u_planetRadius)
            o_fragColor.rgb *= u_ambient;
}
