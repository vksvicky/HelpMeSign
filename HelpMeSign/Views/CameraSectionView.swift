import Cocoa
import MetalKit
import AVFoundation

class CameraSectionView: NSView {
    
    // MARK: - Camera & Metal Properties
    var captureSession: AVCaptureSession?
    var metalView: MTKView!
    var textureCache: CVMetalTextureCache?
    var currentTexture: MTLTexture?
    var pipelineState: MTLRenderPipelineState?
    
    // MARK: - UI Elements
    var camView: NSView!
    var overlay: HoverOverlayView!
    var startStopButton: NSButton!
    var languageLabel: NSTextField!
    var flagLabel: NSTextField!
    
    // MARK: - Callbacks
    var onStartStopTapped: (() -> Void)?
    var onHoverChanged: ((Bool) -> Void)?
    
    // MARK: - Initialization
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        setupView()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupView()
    }
    
    private func setupView() {
        wantsLayer = true
        layer?.backgroundColor = NSColor.clear.cgColor
        
        setupCameraView()
        setupLanguageOverlay()
        setupOverlayControls()
        setupCamera()
        setupPipeline()
    }
    
    // MARK: - Camera View Setup
    private func setupCameraView() {
        let width = bounds.width
        let height = bounds.height
        
        // Camera view: 16:9, centered in top band
        let camMaxWidth: CGFloat = width * 0.8
        let camMaxHeight: CGFloat = height * 0.9
        var camWidth = camMaxWidth
        var camHeight = camWidth * 9.0 / 16.0
        if camHeight > camMaxHeight {
            camHeight = camMaxHeight
            camWidth = camHeight * 16.0 / 9.0
        }
        let camX: CGFloat = (width - camWidth) / 2
        let camY: CGFloat = (height - camHeight) / 2
        
        camView = NSView(frame: NSRect(x: camX, y: camY, width: camWidth, height: camHeight))
        camView.wantsLayer = true
        camView.layer?.backgroundColor = NSColor(calibratedWhite: 0.99, alpha: 1.0).cgColor
        camView.layer?.cornerRadius = 28
        camView.layer?.shadowColor = NSColor.black.cgColor
        camView.layer?.shadowOpacity = 0.13
        camView.layer?.shadowRadius = 18
        camView.layer?.shadowOffset = CGSize(width: 0, height: 8)
        camView.layer?.masksToBounds = false
        addSubview(camView)
        
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
    }
    
    // MARK: - Language Overlay Setup
    private func setupLanguageOverlay() {
        let camWidth = camView.frame.width
        let camHeight = camView.frame.height
        
        // Language/flag overlay (top-right inside camera)
        let langContainer = NSView(frame: NSRect(x: camWidth - 110, y: camHeight - 46, width: 100, height: 40))
        langContainer.wantsLayer = true
        langContainer.layer?.backgroundColor = NSColor.black.withAlphaComponent(0.7).cgColor
        langContainer.layer?.cornerRadius = 8
        
        languageLabel = NSTextField(labelWithString: "BSL")
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
    }
    
    // MARK: - Overlay Controls Setup
    private func setupOverlayControls() {
        let camWidth = camView.frame.width
        
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
            self?.onHoverChanged?(hovering)
        }
        
        // Start/Stop button (center) - Innovative Floating Design
        let buttonSize: CGFloat = 64
        startStopButton = NSButton(title: "", target: self, action: #selector(toggleRecognition))
        startStopButton.bezelStyle = .regularSquare
        startStopButton.setFrameSize(NSSize(width: buttonSize, height: buttonSize))
        startStopButton.frame.origin = CGPoint(x: (overlayWidth - buttonSize)/2, y: (overlayHeight - buttonSize)/2)
        startStopButton.wantsLayer = true
        
        // Force remove any default styling
        startStopButton.isBordered = false
        startStopButton.title = ""
        startStopButton.alternateTitle = ""
        
        // Innovative floating button design
        startStopButton.layer?.backgroundColor = NSColor.systemGreen.withAlphaComponent(0.9).cgColor
        startStopButton.layer?.cornerRadius = buttonSize/2
        startStopButton.layer?.borderWidth = 0
        
        // Create floating shadow effect
        startStopButton.layer?.shadowColor = NSColor.black.cgColor
        startStopButton.layer?.shadowOffset = CGSize(width: 0, height: 8)
        startStopButton.layer?.shadowOpacity = 0.3
        startStopButton.layer?.shadowRadius = 12
        
        // Add inner glow effect
        startStopButton.layer?.masksToBounds = false
        startStopButton.layer?.shadowPath = CGPath(ellipseIn: CGRect(x: 0, y: 0, width: buttonSize, height: buttonSize), transform: nil)
        
        // Create icon container
        let iconContainer = NSView(frame: NSRect(x: 0, y: 0, width: buttonSize, height: buttonSize))
        iconContainer.wantsLayer = true
        iconContainer.layer?.backgroundColor = NSColor.clear.cgColor
        
        // Icon with innovative styling
        let icon = NSTextField(labelWithString: "▶")
        icon.font = NSFont.systemFont(ofSize: 28, weight: .bold)
        icon.textColor = .white
        icon.backgroundColor = .clear
        icon.isBordered = false
        icon.isEditable = false
        icon.alignment = .center
        icon.sizeToFit()
        
        // Center the icon with slight offset for visual balance
        let iconX = (buttonSize - icon.frame.width) / 2 + 1
        let iconY = (buttonSize - icon.frame.height) / 2
        icon.frame = NSRect(x: iconX, y: iconY, width: icon.frame.width, height: icon.frame.height)
        iconContainer.addSubview(icon)
        
        startStopButton.addSubview(iconContainer)
        startStopButton.alignment = .center
        startStopButton.contentTintColor = .white
        startStopButton.toolTip = "Start Sign Language Recognition"
        
        // Add innovative hover effect
        startStopButton.addTrackingArea(NSTrackingArea(rect: startStopButton.bounds, options: [.mouseEnteredAndExited, .activeInActiveApp], owner: self, userInfo: nil))
        
        overlay.addSubview(startStopButton)
        camView.addSubview(overlay)
    }
    
    // MARK: - Camera Setup
    private func setupCamera() {
        let session = AVCaptureSession()
        session.sessionPreset = .high
        guard let device = AVCaptureDevice.default(for: .video),
              let input = try? AVCaptureDeviceInput(device: device) else {
            return
        }
        session.addInput(input)
        let output = AVCaptureVideoDataOutput()
        output.videoSettings = [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA
        ]
        output.setSampleBufferDelegate(self, queue: DispatchQueue(label: "camera.queue"))
        session.addOutput(output)
        session.startRunning()
        self.captureSession = session
    }
    
    private func setupPipeline() {
        guard let device = metalView.device else { return }
        CVMetalTextureCacheCreate(nil, nil, device, nil, &textureCache)
        
        let library = device.makeDefaultLibrary()
        let pipelineDescriptor = MTLRenderPipelineDescriptor()
        pipelineDescriptor.vertexFunction = library?.makeFunction(name: "vertex_passthrough")
        pipelineDescriptor.fragmentFunction = library?.makeFunction(name: "camera_fragment")
        pipelineDescriptor.colorAttachments[0].pixelFormat = metalView.colorPixelFormat
        pipelineState = try? device.makeRenderPipelineState(descriptor: pipelineDescriptor)
    }
    
    // MARK: - Public Methods
    func updateLanguageDisplay(_ languageCode: String, flag: String) {
        DispatchQueue.main.async {
            self.languageLabel?.stringValue = languageCode
            self.flagLabel?.stringValue = flag
        }
    }
    
    func updateStartStopButton(isRecognizing: Bool) {
        guard let startStopButton = startStopButton else { return }
        
        var icon: NSTextField?
        
        if startStopButton.subviews.count >= 2,
           startStopButton.subviews[1].subviews.count >= 2,
           let textField = startStopButton.subviews[1].subviews[1] as? NSTextField {
            icon = textField
        }
        
        // Fallback: Search recursively if direct path fails
        if icon == nil {
            func findAllTextFields(in view: NSView) -> [NSTextField] {
                var textFields: [NSTextField] = []
                for subview in view.subviews {
                    if let textField = subview as? NSTextField {
                        textFields.append(textField)
                    } else {
                        textFields.append(contentsOf: findAllTextFields(in: subview))
                    }
                }
                return textFields
            }
            
            let allTextFieldsRecursive = findAllTextFields(in: startStopButton)
            icon = allTextFieldsRecursive.first
        }
        
        // Update the icon if found
        if let icon = icon {
            NSAnimationContext.runAnimationGroup { context in
                context.duration = 0.3
                context.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
                
                if isRecognizing {
                    // Stop state - Red floating button
                    icon.stringValue = "⏹"
                    icon.textColor = .white
                    startStopButton.layer?.backgroundColor = NSColor.systemRed.withAlphaComponent(0.9).cgColor
                    startStopButton.layer?.shadowColor = NSColor.systemRed.withAlphaComponent(0.4).cgColor
                    startStopButton.layer?.shadowOffset = CGSize(width: 0, height: 12)
                    startStopButton.layer?.shadowOpacity = 0.4
                    startStopButton.layer?.shadowRadius = 16
                    
                    // Add innovative pulsing animation
                    let pulseAnimation = CABasicAnimation(keyPath: "transform.scale")
                    pulseAnimation.duration = 1.2
                    pulseAnimation.fromValue = 1.0
                    pulseAnimation.toValue = 1.08
                    pulseAnimation.autoreverses = true
                    pulseAnimation.repeatCount = .infinity
                    startStopButton.layer?.add(pulseAnimation, forKey: "pulse")
                    
                    // Add glow animation
                    let glowAnimation = CABasicAnimation(keyPath: "shadowOpacity")
                    glowAnimation.duration = 1.2
                    glowAnimation.fromValue = 0.4
                    glowAnimation.toValue = 0.7
                    glowAnimation.autoreverses = true
                    glowAnimation.repeatCount = .infinity
                    startStopButton.layer?.add(glowAnimation, forKey: "glow")
                    
                } else {
                    // Start state - Green floating button
                    icon.stringValue = "▶"
                    icon.textColor = .white
                    startStopButton.layer?.backgroundColor = NSColor.systemGreen.withAlphaComponent(0.9).cgColor
                    startStopButton.layer?.shadowColor = NSColor.black.cgColor
                    startStopButton.layer?.shadowOffset = CGSize(width: 0, height: 8)
                    startStopButton.layer?.shadowOpacity = 0.3
                    startStopButton.layer?.shadowRadius = 12
                    
                    // Remove animations
                    startStopButton.layer?.removeAnimation(forKey: "pulse")
                    startStopButton.layer?.removeAnimation(forKey: "glow")
                }
            }
        }
    }
    
    // MARK: - Actions
    @objc private func toggleRecognition() {
        onStartStopTapped?()
    }
}

// MARK: - MTKViewDelegate
extension CameraSectionView: MTKViewDelegate {
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
        encoder.drawPrimitives(type: .triangleStrip, vertexStart: 0, vertexCount: 4)
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
    
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}
}

// MARK: - AVCaptureVideoDataOutputSampleBufferDelegate
extension CameraSectionView: AVCaptureVideoDataOutputSampleBufferDelegate {
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
} 