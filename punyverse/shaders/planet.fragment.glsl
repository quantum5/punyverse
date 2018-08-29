#version 330 core

in vec2 v_uv;
in vec3 v_normal;
in vec3 v_position;
in vec3 v_camDirection;
in mat3 v_TBN;

out vec4 o_fragColor;

struct Surface {
    sampler2D diffuseMap;
    bool hasNormal;
    sampler2D normalMap;
    bool hasSpecular;
    sampler2D specularMap;
    bool hasEmission;
    sampler2D emissionMap;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    vec3 emission;
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
uniform Surface u_planet;

void main() {
    vec3 normal = u_planet.hasNormal ? normalize(v_TBN * texture2D(u_planet.normalMap, v_uv).rgb * 2 - 1) : v_normal;
    vec3 diffuse = texture2D(u_planet.diffuseMap, v_uv).rgb;
    vec3 specular = u_planet.hasSpecular ? texture2D(u_planet.specularMap, v_uv).rgb : vec3(1);
    vec3 emission = u_planet.hasEmission ? texture2D(u_planet.emissionMap, v_uv).rgb : vec3(1);

    vec3 incident = normalize(u_sun.position - v_position);
    vec3 reflected = normalize(reflect(-incident, normal));

    float diffuseIntensity = max(dot(normal, incident), 0.0);
    float shininess = pow(max(dot(normalize(v_camDirection), reflected), 0), u_planet.shininess);

    vec3 ambient = u_planet.ambient * u_sun.ambient * diffuse;
    diffuse *= u_planet.diffuse * u_sun.diffuse * diffuseIntensity;
    emission *= u_planet.emission * (1 - min(diffuseIntensity * 2, 1));
    specular *= u_planet.specular * u_sun.specular * max(shininess, 0) * diffuseIntensity;

    o_fragColor = vec4((ambient + diffuse + emission + specular) * u_sun.intensity, 1);
}
