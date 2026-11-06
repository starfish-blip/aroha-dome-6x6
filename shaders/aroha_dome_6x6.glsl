#version 300 es
precision highp float;

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_uv;

layout(std140) uniform ArohaResonanceUBO {
    vec4 u_obs_y;
    vec4 u_thermal;
    vec4 u_emergence;
    vec4 u_weights[4];
    vec4 u_dome_meta;
};

uniform mat4 u_modelViewProjection;

out vec2 v_uv;
out vec2 v_cell_id;
out float v_chladni_amp;
out float v_emergence_mix;
out float v_validity;

const float PI = 3.14159265359;

void main() {
    v_uv = a_uv;
    vec2 grid_dims = u_dome_meta.xy;
    v_cell_id = floor(a_uv * grid_dims);
    vec2 cell_center = (v_cell_id + 0.5) / grid_dims;

    float acoustic_ratio = u_thermal.z / 261.63;
    float omega = 2.0 * PI * acoustic_ratio;
    float time_phase = u_emergence.w * omega + u_thermal.w;

    float m_A = 1.0 + abs(u_weights[0].x) * 3.0;
    float n_A = 1.0 + abs(u_weights[1].x) * 3.0;
    float wave_A = u_obs_y.x * cos(m_A * PI * a_uv.x + u_weights[0].y) *
                   cos(n_A * PI * a_uv.y + time_phase * 0.25) +
                   u_obs_y.y * sin(n_A * PI * a_uv.x) * sin(m_A * PI * a_uv.y);

    float m_B = 1.0 + abs(u_weights[2].x) * 3.0;
    float n_B = 1.0 + abs(u_weights[3].x) * 3.0;
    float wave_B = u_obs_y.z * cos(m_B * PI * a_uv.y + u_weights[2].y) *
                   cos(n_B * PI * a_uv.x - time_phase * 0.25) +
                   u_obs_y.w * sin(m_B * PI * a_uv.x) * sin(n_B * PI * a_uv.y);

    float s_norm = clamp(u_emergence.x / 2.0, 0.0, 1.0);
    float gamma_mean = 0.25 * (
        abs(u_weights[0].z) + abs(u_weights[1].z) +
        abs(u_weights[2].z) + abs(u_weights[3].z)
    );

    float separable_sum = 0.5 * (wave_A + wave_B);
    float emergent_product = wave_A * wave_B * cos(gamma_mean * PI + cell_center.x * PI);
    float combined_field = mix(separable_sum, emergent_product, s_norm);

    v_chladni_amp = combined_field;
    v_emergence_mix = s_norm;
    v_validity = u_emergence.y;

    vec3 normal = normalize(a_position);
    vec3 displaced_pos = a_position + normal * (combined_field * u_dome_meta.z);
    gl_Position = u_modelViewProjection * vec4(displaced_pos, 1.0);
}
