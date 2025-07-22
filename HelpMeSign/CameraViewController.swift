//
//  CameraViewController.swift
//  HelpMeSign
//
//  Created by Vivek Krishnan on 21/07/2025.
//

import Cocoa
import MetalKit
import AVFoundation

@objc class CameraViewController: NSViewController, AVCaptureVideoDataOutputSampleBufferDelegate, MTKViewDelegate {
    var captureSession: AVCaptureSession?
    var metalView: MTKView!
    var textureCache: CVMetalTextureCache?
    var currentTexture: MTLTexture?
    var pipelineState: MTLRenderPipelineState?
    var mtkDelegate: SimpleMTKViewDelegate? // Not used, but kept for reference

    override func loadView() {
        let width: CGFloat = 1024
        let height: CGFloat = 1024
        let topHeight = height * 0.5
        let midHeight = height * 0.25
        let botHeight = height * 0.25
        let container = NSView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        container.wantsLayer = true
        container.layer?.backgroundColor = NSColor.white.cgColor
        
        let heights = [topHeight, midHeight, botHeight]
        let colors: [NSColor] = [NSColor.systemRed, NSColor.systemGreen, NSColor.systemBlue]
        var y = height
        for i in 0..<3 {
            y -= heights[i]
            let section = NSView(frame: NSRect(x: 0, y: y, width: width, height: heights[i]))
            section.wantsLayer = true
            let color = colors[i]
            section.layer?.backgroundColor = color.withAlphaComponent(0.2).cgColor
            let label = NSTextField(labelWithString: "Section \(i+1)")
            label.font = NSFont.systemFont(ofSize: 32, weight: .bold)
            label.textColor = color
            label.sizeToFit()
            label.frame.origin = CGPoint(x: 40, y: heights[i]/2 - label.frame.height/2)
            section.addSubview(label)
            if i == 0 {
                // Add MTKView for camera feed
                let mtkView = MTKView(frame: NSRect(x: 200, y: 20, width: width-240, height: heights[0]-40))
                mtkView.device = MTLCreateSystemDefaultDevice()
                mtkView.delegate = self
                mtkView.clearColor = MTLClearColor(red: 0, green: 0, blue: 0, alpha: 1)
                mtkView.enableSetNeedsDisplay = true
                mtkView.isPaused = false
                mtkView.preferredFramesPerSecond = 60
                section.addSubview(mtkView)
                self.metalView = mtkView
            }
            container.addSubview(section)
        }
        self.view = container
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        print("CameraViewController loaded")
        guard let metalView = self.metalView else {
            print("MTKView not set up")
            return
        }
        CVMetalTextureCacheCreate(nil, nil, metalView.device!, nil, &textureCache)
        setupCamera()
        setupPipeline()
    }

    func setupCamera() {
        let session = AVCaptureSession()
        session.sessionPreset = .high
        guard let device = AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device) else {
            print("No camera device found or failed to create input")
            return
        }
        print("Camera device found: \(device.localizedName)")
        session.addInput(input)

        let output = AVCaptureVideoDataOutput()
        output.videoSettings = [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA
        ]
        output.setSampleBufferDelegate(self, queue: DispatchQueue(label: "camera.queue"))
        session.addOutput(output)

        session.startRunning()
        print("Camera session started")
        self.captureSession = session
    }

    func setupPipeline() {
        guard let device = metalView.device else { return }
        let library = device.makeDefaultLibrary()
        let pipelineDescriptor = MTLRenderPipelineDescriptor()
        pipelineDescriptor.vertexFunction = library?.makeFunction(name: "vertex_passthrough")
        pipelineDescriptor.fragmentFunction = library?.makeFunction(name: "camera_fragment")
        pipelineDescriptor.colorAttachments[0].pixelFormat = metalView.colorPixelFormat
        pipelineState = try? device.makeRenderPipelineState(descriptor: pipelineDescriptor)
    }

    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        print("Received camera frame")
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer),
              let textureCache = textureCache,
              let _ = metalView.device else { return }

        var texture: CVMetalTexture?
        let width = CVPixelBufferGetWidth(pixelBuffer)
        let height = CVPixelBufferGetHeight(pixelBuffer)
        let status = CVMetalTextureCacheCreateTextureFromImage(
            nil, textureCache, pixelBuffer, nil, .bgra8Unorm, width, height, 0, &texture)
        if status == kCVReturnSuccess, let texture = texture {
            self.currentTexture = CVMetalTextureGetTexture(texture)
            DispatchQueue.main.async {
                self.metalView.setNeedsDisplay(self.metalView.bounds)
            }
        }
    }

    func draw(in view: MTKView) {
        print("draw(in:) called")
        if currentTexture == nil {
            print("currentTexture is nil")
        } else {
            print("currentTexture is set")
        }

        guard let drawable = view.currentDrawable,
              let commandQueue = view.device?.makeCommandQueue(),
              let commandBuffer = commandQueue.makeCommandBuffer(),
              let descriptor = view.currentRenderPassDescriptor else { return }

        let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor)!
        if let pipelineState = pipelineState, let texture = currentTexture {
            encoder.setRenderPipelineState(pipelineState)
            encoder.setFragmentTexture(texture, index: 0)
            encoder.drawPrimitives(type: .triangleStrip, vertexStart: 0, vertexCount: 4)
        } else {
            // Just clear to green for debug
            print("No texture, filling with green")
        }
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}
}

