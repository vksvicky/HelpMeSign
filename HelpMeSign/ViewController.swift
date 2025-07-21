import Cocoa
import MetalKit

class ViewController: NSViewController, MTKViewDelegate {
    @IBOutlet weak var metalView: MTKView!
    var commandQueue: MTLCommandQueue?

    override func viewDidLoad() {
        super.viewDidLoad()
        print("metalView is \(metalView == nil ? "nil" : "not nil")")
        guard let device = MTLCreateSystemDefaultDevice() else {
            fatalError("Metal is not supported on this device")
        }
        metalView.device = device
        metalView.clearColor = MTLClearColor(red: 0.2, green: 0.2, blue: 0.25, alpha: 1.0)
        metalView.delegate = self
        commandQueue = device.makeCommandQueue()
    }

    func draw(in view: MTKView) {
        guard let drawable = view.currentDrawable,
              let descriptor = view.currentRenderPassDescriptor,
              let commandBuffer = commandQueue?.makeCommandBuffer(),
              let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor) else {
            return
        }
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        // Handle view size changes if needed
    }
} 