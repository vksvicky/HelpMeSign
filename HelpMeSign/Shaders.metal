#include <metal_stdlib>
using namespace metal;

struct VertexOut {
    float4 position [[position]];
    float2 texCoord;
};

vertex VertexOut vertex_passthrough(uint vertexID [[vertex_id]]) {
    float2 pos[4] = { {-1, -1}, {1, -1}, {-1, 1}, {1, 1} };
    float2 tex[4] = { {0, 1}, {1, 1}, {0, 0}, {1, 0} };
    VertexOut out;
    out.position = float4(pos[vertexID], 0, 1);
    out.texCoord = tex[vertexID];
    return out;
}

// Simple 9-tap horizontal gaussian blur
//float4 blur_sample(texture2d<float> tex, sampler s, float2 uv, float2 texel) {
//    float kernel[9] = {0.05, 0.09, 0.12, 0.15, 0.18, 0.15, 0.12, 0.09, 0.05};
//    float4 color = float4(0.0);
//    for (int i = -4; i <= 4; ++i) {
//        color += tex.sample(s, uv + float2(i,0)*texel) * kernel[i+4];
//    }
//    return color;
//}

float4 blur_sample(texture2d<float> tex, sampler s, float2 uv, float2 texel) {
    float4 color = float4(0.0);
    // Stronger blur effect - 15-tap gaussian blur
    for (int i = -7; i <= 7; ++i) {
        float weight;
        float x = abs(float(i)) / 7.0;
        weight = exp(-x * x * 2.0) / 2.5; // Gaussian weight
        color += tex.sample(s, uv + float2(i, 0) * texel * 1.5) * weight;
    }
    return color;
}

fragment float4 camera_fragment(VertexOut in [[stage_in]],
                               texture2d<float> cameraTexture [[texture(0)]],
                               constant bool &blurEnabled [[buffer(0)]]) {
    constexpr sampler s(address::clamp_to_edge);
    float2 texel = 1.0 / float2(cameraTexture.get_width(), cameraTexture.get_height());
    if (blurEnabled) {
        return blur_sample(cameraTexture, s, in.texCoord, texel);
    } else {
        return cameraTexture.sample(s, in.texCoord);
    }
}
