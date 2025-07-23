import MetalKit

class SimpleMTKViewDelegate: NSObject, MTKViewDelegate {
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        print("MTKView size changed to: \(size)")
    }
    
    func draw(in view: MTKView) {
        print("MTKView draw called")
        guard let drawable = view.currentDrawable,
              let commandQueue = view.device?.makeCommandQueue(),
              let commandBuffer = commandQueue.makeCommandBuffer(),
              let descriptor = view.currentRenderPassDescriptor else {
            print("Failed to get Metal objects for drawing")
            return
        }
        let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor)!
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
        print("MTKView draw completed")
    }
} 