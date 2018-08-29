#version 330 core

in vec3 a_normal;
in vec2 a_uv;

out vec2 v_uv;
out vec3 v_normal;
out vec3 v_position;

uniform float u_radius;
uniform mat4 u_mvpMatrix;
uniform mat4 u_modelMatrix;

void main() {
    vec3 position = u_radius * a_normal;
    v_uv = a_uv;
    v_normal = (u_modelMatrix * vec4(a_normal, 0)).xyz;
    v_position = (u_modelMatrix * vec4(position, 1)).xyz;
    gl_Position = u_mvpMatrix * vec4(position, 1);
}
