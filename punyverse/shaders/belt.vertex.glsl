#version 330 core

in vec3 a_position;
in vec3 a_normal;
in vec2 a_uv;
in vec3 a_translate;
in float a_scale;

out vec2 v_uv;
out vec3 v_normal;
out vec3 v_position;
out vec3 v_camDirection;

uniform mat4 u_mvpMatrix;
uniform mat4 u_mvMatrix;
uniform mat4 u_modelMatrix;

void main() {
    mat4 matrix = mat4(mat3(a_scale));
    matrix[3].xyz = a_translate;
    mat4 modelMatrix = u_modelMatrix * matrix;

    gl_Position = u_mvpMatrix * matrix * vec4(a_position, 1);
    v_normal = normalize(vec3(modelMatrix * vec4(a_normal, 0)));
    v_uv = a_uv;
    v_position = (modelMatrix * vec4(a_position, 1)).xyz;
    v_camDirection = (u_mvMatrix * matrix * vec4(a_position, 1)).xyz;
}
