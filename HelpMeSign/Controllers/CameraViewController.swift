//
//  CameraViewController.swift
//  HelpMeSign
//
//  Top 50%: 16:9 camera view, centered, with floating icon-only controls visible on hover
//  Middle 25%: empty; Bottom 25%: empty, visually distinct
//

import Cocoa
import MetalKit
import AVFoundation
import Vision

class HoverOverlayView: NSView {
    var onHoverChanged: ((Bool) -> Void)?
    override func updateTrackingAreas() {
        super.updateTrackingAreas()
        self.trackingAreas.forEach { self.removeTrackingArea($0) }
        let options: NSTrackingArea.Options = [.mouseEnteredAndExited, .activeInActiveApp, .inVisibleRect]
        let area = NSTrackingArea(rect: self.bounds, options: options, owner: self, userInfo: nil)
        self.addTrackingArea(area)
    }
    override func mouseEntered(with event: NSEvent) {
        onHoverChanged?(true)
    }
    override func mouseExited(with event: NSEvent) {
        onHoverChanged?(false)
    }
}

@objc class CameraViewController: NSViewController, AVCaptureVideoDataOutputSampleBufferDelegate, MTKViewDelegate {
    // MARK: - Camera & Metal Properties
    var captureSession: AVCaptureSession?
    var metalView: MTKView!
    var textureCache: CVMetalTextureCache?
    var currentTexture: MTLTexture?
    var pipelineState: MTLRenderPipelineState?

    // MARK: - UI State
    var isRecognizing = false
    var blurBackground = false
    var centerFrame = false

    // MARK: - UI Elements
    var camView: NSView!
    var overlay: HoverOverlayView!
    var startStopButton: NSButton!
    var blurButton: NSButton!
    var pulseLayer: CALayer?
    var languageLabel: NSTextField!
    var flagLabel: NSTextField!

    override func loadView() {
        let width: CGFloat = 1024
        let height: CGFloat = 1024
        let topHeight = height * 0.5
        let midHeight = height * 0.25
        let botHeight = height * 0.25
        let container = NSView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        container.wantsLayer = true
        container.layer?.backgroundColor = NSColor(calibratedWhite: 0.97, alpha: 1.0).cgColor

        // --- Top Section: 16:9 Camera View, Centered ---
        let topSection = NSView(frame: NSRect(x: 0, y: height - topHeight, width: width, height: topHeight))
        topSection.wantsLayer = true
        topSection.layer?.backgroundColor = NSColor.white.cgColor
        // Camera view: 16:9, centered in top band
        let camMaxWidth: CGFloat = width * 0.8
        let camMaxHeight: CGFloat = topHeight * 0.9
        var camWidth = camMaxWidth
        var camHeight = camWidth * 9.0 / 16.0
        if camHeight > camMaxHeight {
            camHeight = camMaxHeight
            camWidth = camHeight * 16.0 / 9.0
        }
        let camX: CGFloat = (width - camWidth) / 2
        let camY: CGFloat = (topHeight - camHeight) / 2
        camView = NSView(frame: NSRect(x: camX, y: camY, width: camWidth, height: camHeight))
        camView.wantsLayer = true
        camView.layer?.backgroundColor = NSColor(calibratedWhite: 0.99, alpha: 1.0).cgColor
        camView.layer?.cornerRadius = 28
        camView.layer?.shadowColor = NSColor.black.cgColor
        camView.layer?.shadowOpacity = 0.13
        camView.layer?.shadowRadius = 18
        camView.layer?.shadowOffset = CGSize(width: 0, height: 8)
        camView.layer?.masksToBounds = false
        topSection.addSubview(camView)
        // Metal camera view (fills camView)
        metalView = MTKView(frame: NSRect(x: 0, y: 0, width: camWidth, height: camHeight))
        metalView.device = MTLCreateSystemDefaultDevice()
        metalView.delegate = self
        metalView.clearColor = MTLClearColor(red: 0, green: 0, blue: 0, alpha: 1)
        metalView.enableSetNeedsDisplay = true
        metalView.isPaused = false
        metalView.preferredFramesPerSecond = 60
        metalView.layer?.cornerRadius = 28
        metalView.layer?.masksToBounds = true
        camView.addSubview(metalView)
        // Language/flag overlay (top-right inside camera)
        let langContainer = NSView(frame: NSRect(x: camWidth - 110, y: camHeight - 46, width: 100, height: 40))
        langContainer.wantsLayer = true
        langContainer.layer?.backgroundColor = NSColor.black.withAlphaComponent(0.7).cgColor
        langContainer.layer?.cornerRadius = 8
        languageLabel = NSTextField(labelWithString: "ASL")
        languageLabel.font = NSFont.systemFont(ofSize: 16, weight: .semibold)
        languageLabel.textColor = .white
        languageLabel.sizeToFit()
        languageLabel.frame.origin = CGPoint(x: 10, y: 12)
        langContainer.addSubview(languageLabel)
        flagLabel = NSTextField(labelWithString: "🇺🇸")
        flagLabel.font = NSFont.systemFont(ofSize: 20)
        flagLabel.sizeToFit()
        flagLabel.frame.origin = CGPoint(x: 60, y: 8)
        langContainer.addSubview(flagLabel)
        camView.addSubview(langContainer)
        // --- Overlay Controls (icon-only, floating, visible on hover) ---
        let overlayHeight: CGFloat = 64
        let overlayWidth: CGFloat = camWidth * 0.7
        overlay = HoverOverlayView(frame: NSRect(x: (camWidth - overlayWidth)/2, y: 24, width: overlayWidth, height: overlayHeight))
        overlay.wantsLayer = true
        overlay.layer?.backgroundColor = NSColor.clear.cgColor
        overlay.alphaValue = 0.0
        overlay.onHoverChanged = { [weak self] hovering in
            NSAnimationContext.runAnimationGroup { ctx in
                ctx.duration = 0.18
                self?.overlay.animator().alphaValue = hovering ? 1.0 : 0.0
            }
        }
        // Feature button (left)
        let featureSize: CGFloat = 56
        blurButton = NSButton(title: "", target: self, action: #selector(toggleBlur))
        blurButton.bezelStyle = .regularSquare
        blurButton.setFrameSize(NSSize(width: featureSize, height: featureSize))
        blurButton.frame.origin = CGPoint(x: 0, y: (overlayHeight - featureSize)/2)
        blurButton.wantsLayer = true
        blurButton.layer?.cornerRadius = featureSize/2
        blurButton.layer?.backgroundColor = NSColor.clear.cgColor
        blurButton.layer?.borderWidth = 0
        let blurIcon = NSTextField(labelWithString: "💧")
        blurIcon.font = NSFont.systemFont(ofSize: 28)
        blurIcon.backgroundColor = .clear
        blurIcon.isBordered = false
        blurIcon.isEditable = false
        blurIcon.textColor = .systemGray // Start with gray to show it's off
        blurIcon.sizeToFit()
        blurIcon.frame.origin = CGPoint(x: (featureSize - blurIcon.frame.width)/2, y: (featureSize - blurIcon.frame.height)/2)
        blurButton.addSubview(blurIcon)
        blurButton.contentTintColor = .systemBlue
        blurButton.toolTip = "Blur Background (Click to toggle)"
        overlay.addSubview(blurButton)
        // Start/Stop button (center)
        let buttonWidth: CGFloat = 120
        let buttonHeight: CGFloat = 56
        startStopButton = NSButton(title: "", target: self, action: #selector(toggleRecognition))
        startStopButton.bezelStyle = .regularSquare
        startStopButton.setFrameSize(NSSize(width: buttonWidth, height: buttonHeight))
        startStopButton.frame.origin = CGPoint(x: (overlayWidth - buttonWidth)/2, y: (overlayHeight - buttonHeight)/2)
        startStopButton.wantsLayer = true
        startStopButton.layer?.backgroundColor = NSColor.clear.cgColor
        startStopButton.layer?.cornerRadius = buttonHeight/2
        startStopButton.layer?.borderWidth = 0
        let icon = NSTextField(labelWithString: "▶")
        icon.font = NSFont.systemFont(ofSize: 32, weight: .bold)
        icon.textColor = .systemGreen
        icon.backgroundColor = .clear
        icon.isBordered = false
        icon.isEditable = false
        icon.sizeToFit()
        icon.frame.origin = CGPoint(x: (buttonWidth - icon.frame.width)/2, y: (buttonHeight - icon.frame.height)/2)
        startStopButton.addSubview(icon)
        startStopButton.alignment = .center
        startStopButton.contentTintColor = .systemGreen
        startStopButton.toolTip = "Start/Stop Recognition"
        overlay.addSubview(startStopButton)
        camView.addSubview(overlay)
        container.addSubview(topSection)

        // --- Middle Section: Empty, visually distinct ---
        let midSection = NSView(frame: NSRect(x: 0, y: botHeight, width: width, height: midHeight))
        midSection.wantsLayer = true
        midSection.layer?.backgroundColor = NSColor(calibratedWhite: 0.99, alpha: 1.0).cgColor
        container.addSubview(midSection)

        // --- Bottom Section: Alphabet Bar ---
        let botSection = NSView(frame: NSRect(x: 0, y: 0, width: width, height: botHeight))
        botSection.wantsLayer = true
        botSection.layer?.backgroundColor = NSColor(calibratedWhite: 0.95, alpha: 1.0).cgColor
        
        // Add divider at the top
        let divider = NSView(frame: NSRect(x: width * 0.15, y: botHeight - 2, width: width * 0.7, height: 2))
        divider.wantsLayer = true
        divider.layer?.backgroundColor = NSColor.systemGray.withAlphaComponent(0.13).cgColor
        botSection.addSubview(divider)
        
        // Add alphabet bar inside the bottom section
        let alphabetBar = AlphabetBarView(frame: NSRect(x: 0, y: 0, width: width, height: botHeight))
        botSection.addSubview(alphabetBar)
        
        container.addSubview(botSection)

        self.view = container
    }

    // --- Start/Stop Recognition Handler ---
    @objc func toggleRecognition() {
        isRecognizing.toggle()
        if isRecognizing {
            if let icon = startStopButton.subviews.first as? NSTextField { icon.stringValue = "⏹" }
            startStopButton.contentTintColor = .systemRed
        } else {
            if let icon = startStopButton.subviews.first as? NSTextField { icon.stringValue = "▶" }
            startStopButton.contentTintColor = .systemGreen
        }
    }

    // --- Feature Button Handlers ---
    @objc func toggleBlur() {
        blurBackground.toggle()
        
        // Update button visual state
        if let blurIcon = blurButton.subviews.first as? NSTextField {
            blurIcon.stringValue = blurBackground ? "💧" : "💧"
            blurIcon.textColor = blurBackground ? .systemBlue : .systemGray
        }
        
        // Update button background and border
        if blurBackground {
            blurButton.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.2).cgColor
            blurButton.layer?.borderWidth = 2
            blurButton.layer?.borderColor = NSColor.systemBlue.cgColor
        } else {
            blurButton.layer?.backgroundColor = NSColor.clear.cgColor
            blurButton.layer?.borderWidth = 0
        }
        
        // Force Metal view to redraw with new blur setting
        metalView.setNeedsDisplay(metalView.bounds)
        
        // Print debug info
        print("Blur background: \(blurBackground)")
    }

    // --- Camera & Metal Setup ---
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
    // --- Camera Output Delegate ---
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
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
        }
    }
    // --- Metal Draw Delegate ---
    func draw(in view: MTKView) {
        guard let drawable = view.currentDrawable,
              let pipelineState = pipelineState,
              let commandQueue = view.device?.makeCommandQueue(),
              let commandBuffer = commandQueue.makeCommandBuffer(),
              let descriptor = view.currentRenderPassDescriptor,
              let texture = currentTexture else { return }
        let encoder = commandBuffer.makeRenderCommandEncoder(descriptor: descriptor)!
        encoder.setRenderPipelineState(pipelineState)
        encoder.setFragmentTexture(texture, index: 0)
        var blurFlag = blurBackground
        encoder.setFragmentBytes(&blurFlag, length: MemoryLayout<Bool>.size, index: 0)
        encoder.drawPrimitives(type: .triangleStrip, vertexStart: 0, vertexCount: 4)
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}
}

