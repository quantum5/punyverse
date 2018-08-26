#version 130

in vec2 v_uv;
uniform sampler2D u_emission;

void main() {
    gl_FragColor = vec4(texture(u_emission, v_uv).rgb, 1);
}
