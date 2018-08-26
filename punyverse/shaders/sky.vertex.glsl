#version 130

in vec3 a_direction;
in vec2 a_uv;
out vec2 v_uv;
uniform mat4 u_mvpMatrix;

void main() {
    gl_Position = (u_mvpMatrix * vec4(a_direction, 1)).xyww;
    v_uv = a_uv;
}
