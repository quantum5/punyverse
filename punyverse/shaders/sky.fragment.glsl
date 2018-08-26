#version 130

in vec2 v_uv;
uniform sampler2D u_skysphere;

void main() {
    gl_FragColor = vec4(texture(u_skysphere, v_uv).rgb, 1);
}
