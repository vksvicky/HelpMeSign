import MetalKit

class SimpleMTKViewDelegate: NSObject, MTKViewDelegate {
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
    }
    
    func draw(in view: MTKView) {
        guard let drawable = view.currentDrawable,
              let commandQueue = view.device?.makeCommandQueue(),
              let commandBuffer = commandQueue.makeCommandBuffer(),
              let descriptor = view.currentRenderPassDescriptor else {
            return
        }
        let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor)!
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
} 