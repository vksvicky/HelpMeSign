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

fragment float4 camera_fragment(VertexOut in [[stage_in]], texture2d<float> cameraTexture [[texture(0)]]) {
    constexpr sampler s(address::clamp_to_edge);
    return cameraTexture.sample(s, in.texCoord);
}
