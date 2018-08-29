#version 330 core

in vec2 v_uv;
in vec3 v_normal;
in vec3 v_position;
in vec3 v_camDirection;

out vec4 o_fragColor;

struct Material {
    bool hasDiffuse;
    sampler2D diffuseMap;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

struct Sun {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    vec3 position;
    float intensity;
};

uniform Sun u_sun;
uniform Material u_material;

void main() {
    vec3 incident = normalize(u_sun.position - v_position);
    vec3 reflected = normalize(reflect(-incident, v_normal));

    float diffuseIntensity = max(dot(v_normal, incident), 0.0);
    float shininess = pow(max(dot(normalize(v_camDirection), reflected), 0), u_material.shininess);

    vec3 diffuse = u_material.hasDiffuse ? texture2D(u_material.diffuseMap, v_uv).rgb : vec3(1);
    vec3 ambient = u_material.ambient * u_sun.ambient * diffuse;
    vec3 specular = u_material.specular * u_sun.specular * max(shininess, 0) * diffuseIntensity;
    diffuse *= u_material.diffuse * u_sun.diffuse * diffuseIntensity;

    o_fragColor = vec4((ambient + diffuse + specular) * u_sun.intensity, 1);
}
