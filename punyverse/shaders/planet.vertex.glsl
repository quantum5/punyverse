#version 330 core

in vec3 a_normal;
in vec2 a_tangent;
in vec2 a_uv;

out vec2 v_uv;
out vec3 v_normal;
out vec3 v_position;
out vec3 v_camDirection;
out mat3 v_TBN;

uniform float u_radius;
uniform mat4 u_mvpMatrix;
uniform mat4 u_mvMatrix;
uniform mat4 u_modelMatrix;

void main() {
    vec3 position = u_radius * a_normal;

    gl_Position = u_mvpMatrix * vec4(position, 1);

    v_normal = normalize(vec3(u_modelMatrix * vec4(a_normal, 0)));
    v_uv = a_uv;
    v_position = (u_modelMatrix * vec4(position, 1)).xyz;
    v_camDirection = (u_mvMatrix * vec4(position, 1)).xyz;

    vec3 tangent = normalize((u_modelMatrix * vec4(a_tangent, a_normal.z, 0)).xyz);
    v_TBN = mat3(tangent, cross(tangent, v_normal), v_normal);
}
