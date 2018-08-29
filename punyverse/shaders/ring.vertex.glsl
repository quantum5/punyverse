#version 330 core

in vec2 a_position;
in float a_u;

out vec3 v_position;
out float v_u;

uniform mat4 u_mvpMatrix;
uniform mat4 u_modelMatrix;

void main() {
    gl_Position = u_mvpMatrix * vec4(a_position, 0, 1);
    v_position = (u_modelMatrix * vec4(a_position, 0, 1)).xyz;
    v_u = a_u;
}
