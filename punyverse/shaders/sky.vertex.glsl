#version 330 core

in vec3 a_direction;
out vec3 v_direction;
uniform mat4 u_mvpMatrix;

void main() {
    gl_Position = (u_mvpMatrix * vec4(a_direction, 1)).xyww;
    v_direction = a_direction;
}
