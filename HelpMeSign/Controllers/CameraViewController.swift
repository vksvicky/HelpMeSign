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
import CoreML

@objc class CameraViewController: NSViewController, AVCaptureVideoDataOutputSampleBufferDelegate, MTKViewDelegate {
    // MARK: - Camera & Metal Properties
    var captureSession: AVCaptureSession?
    var metalView: MTKView!
    var textureCache: CVMetalTextureCache?
    var currentTexture: MTLTexture?
    var pipelineState: MTLRenderPipelineState?

    // MARK: - UI State
    var isRecognizing = false
    var centerFrame = false
    
    // MARK: - AI & ML Components
    private var aiSystem: AIUserExperienceSystem!
    private var languageEngine: LanguageEngine!
    private var translationDisplayView: TranslationDisplayView!

    // MARK: - UI Elements
    var camView: NSView!
    var overlay: HoverOverlayView!
    var startStopButton: NSButton!
    var pulseLayer: CALayer?
    var languageLabel: NSTextField!
    var flagLabel: NSTextField!
    var fallbackTextView: NSTextView!

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
        container.addSubview(topSection)

        // --- Middle Section: Translation Display ---
        let midSection = NSView(frame: NSRect(x: 0, y: botHeight, width: width, height: midHeight))
        midSection.wantsLayer = true
        midSection.layer?.backgroundColor = NSColor(calibratedWhite: 0.99, alpha: 1.0).cgColor
        
        // Create a simple translation display view (no external file dependency)
        print("🔧 Creating simple translation display view")
        
        // Create header view
        let headerView = NSView(frame: NSRect(x: width * 0.1, y: midHeight * 0.8, width: width * 0.8, height: 40))
        headerView.wantsLayer = true
        headerView.layer?.backgroundColor = NSColor.white.cgColor
        
        // Header label
        let headerLabel = NSTextField(labelWithString: "🇺🇸 ASL - Sign Language Translations")
        headerLabel.font = NSFont.systemFont(ofSize: 16, weight: .semibold)
        headerLabel.textColor = NSColor.systemBlue
        headerLabel.frame = NSRect(x: 10, y: 10, width: 300, height: 20)
        headerView.addSubview(headerLabel)
        
        // Clear button
        let clearButton = NSButton(title: "Clear", target: self, action: #selector(clearTranslationsAction))
        clearButton.bezelStyle = NSButton.BezelStyle.rounded
        clearButton.frame = NSRect(x: width * 0.8 - 70, y: 8, width: 60, height: 24)
        headerView.addSubview(clearButton)
        
        midSection.addSubview(headerView)
        
        // Create scroll view for main text view
        let scrollView = NSScrollView(frame: NSRect(x: width * 0.1, y: midHeight * 0.1, width: width * 0.8, height: midHeight * 0.7))
        scrollView.hasVerticalScroller = true
        scrollView.hasHorizontalScroller = false
        scrollView.autohidesScrollers = true
        scrollView.borderType = .lineBorder
        scrollView.wantsLayer = true
        scrollView.layer?.borderWidth = 1
        scrollView.layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.3).cgColor
        scrollView.layer?.cornerRadius = 8
        
        // Create main text view inside scroll view with proper size
        let textViewWidth = scrollView.frame.width - 20
        let textViewHeight = scrollView.frame.height - 20
        let mainTextView = NSTextView(frame: NSRect(x: 0, y: 0, width: textViewWidth, height: textViewHeight))
        mainTextView.string = "Ready for translations..." // Add initial text to verify visibility
        mainTextView.isEditable = false
        mainTextView.backgroundColor = NSColor.white
        mainTextView.font = NSFont.systemFont(ofSize: 16)
        mainTextView.textColor = NSColor.black // Force black text for visibility
        mainTextView.isSelectable = true
        mainTextView.isVerticallyResizable = true
        mainTextView.isHorizontallyResizable = false
        mainTextView.textContainer?.containerSize = NSSize(width: textViewWidth, height: CGFloat.greatestFiniteMagnitude)
        mainTextView.textContainer?.widthTracksTextView = true
        
        // Add subtle border for visual clarity
        mainTextView.wantsLayer = true
        mainTextView.layer?.borderWidth = 1
        mainTextView.layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.3).cgColor
        
        scrollView.documentView = mainTextView
        midSection.addSubview(scrollView)
        
        print("🔧 Text view frame: \(mainTextView.frame)")
        print("🔧 Scroll view frame: \(scrollView.frame)")
        print("🔧 Text view is hidden: \(mainTextView.isHidden)")
        print("🔧 Text view alpha: \(mainTextView.alphaValue)")
        
        // Store reference for updates
        self.fallbackTextView = mainTextView
        print("🔧 Created simple translation view successfully")
        print("🔧 fallbackTextView reference set: \(fallbackTextView != nil)")
        
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
        
        // Initialize AI & ML components
        setupAIComponents()
    }
    
    // MARK: - AI & ML Setup
    
    private func setupAIComponents() {
        // Initialize AI system
        aiSystem = AIUserExperienceSystem.shared
        
        // Initialize language engine
        languageEngine = LanguageEngine.shared
        
        // Setup callbacks
        setupAICallbacks()
        
        // Start language discovery
        Task {
            await languageEngine.discoverLanguages()
        }
    }
    
    private func setupAICallbacks() {
        // AI system callbacks
        aiSystem.onSignRecognized = { [weak self] (result: AIRecognitionResult) in
            print("🎯 AI System callback triggered: \(result.sign)")
            DispatchQueue.main.async {
                self?.handleSignRecognition(result)
            }
        }
        
        aiSystem.onLanguageChanged = { [weak self] language in
            DispatchQueue.main.async {
                self?.handleLanguageChange(language)
            }
        }
        
        aiSystem.onRecognitionStateChanged = { [weak self] isActive in
            DispatchQueue.main.async {
                self?.handleRecognitionStateChange(isActive)
            }
        }
        
        // Language engine callbacks
        languageEngine.onRecognitionComplete = { [weak self] (result: RecognitionResult) in
            DispatchQueue.main.async {
                self?.handleLanguageEngineRecognition(result)
            }
        }
        
        languageEngine.onTranslationComplete = { [weak self] result in
            DispatchQueue.main.async {
                self?.handleTranslation(result)
            }
        }
    }
    
    // MARK: - AI & ML Handlers
    
    private func handleSignRecognition(_ result: AIRecognitionResult) {
        print("🎯 handleSignRecognition called: \(result.sign) with confidence: \(result.confidence)")
        
        // Add translation to the history
        if let translationView = translationDisplayView {
            print("📝 Adding translation to display: \(result.sign)")
            translationView.addTranslation(result.sign, confidence: result.confidence)
        } else if let fallbackView = fallbackTextView {
            print("📝 Adding translation to fallback view: \(result.sign)")
            let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .short)
            let confidencePercentage = Int(result.confidence * 100)
            let newEntry = "[\(timestamp)] \(result.sign) (\(confidencePercentage)%)\n"
            
            DispatchQueue.main.async {
                let currentText = fallbackView.string
                fallbackView.string = currentText + newEntry
                fallbackView.scrollToEndOfDocument(nil)
                
                // Force refresh the text view
                fallbackView.needsDisplay = true
                fallbackView.needsLayout = true
                
                print("📝 Updated fallback view, new content length: \(fallbackView.string.count)")
                print("📝 Current text preview: \(String(fallbackView.string.suffix(100)))")
                print("📝 Text view frame: \(fallbackView.frame)")
                print("📝 Text view is hidden: \(fallbackView.isHidden)")
            }
        } else {
            print("❌ Both translationDisplayView and fallbackTextView are nil!")
        }
        
        // Update language display
        languageLabel.stringValue = result.language.code
        flagLabel.stringValue = result.language.flag
    }
    
    private func handleLanguageChange(_ language: SignLanguage) {
        // Update UI for new language
        languageLabel.stringValue = language.code
        flagLabel.stringValue = language.flag
        
        translationDisplayView?.updateLanguageDisplay(language.code)
    }
    
    private func handleRecognitionStateChange(_ isActive: Bool) {
        // Update recognition state
        isRecognizing = isActive
        translationDisplayView?.setRecognitionStatus(isActive)
        
        // Update button state
        updateStartStopButton()
    }
    
    private func handleLanguageEngineRecognition(_ result: RecognitionResult) {
        // Handle recognition from language engine
        translationDisplayView?.addTranslation(result.sign, confidence: result.confidence)
    }
    
    private func handleTranslation(_ result: TranslationResult) {
        // Handle translation result
        translationDisplayView?.addTranslation(result.targetSign, confidence: result.confidence)
    }
    
    @objc private func clearTranslationsAction() {
        print("🧹 Clearing translations")
        if let fallbackView = fallbackTextView {
            fallbackView.string = ""
        }
    }
    
    // MARK: - Public Methods for Testing
    
    /// Check camera permission status
    func checkCameraPermission() {
        // This is a simplified implementation for testing
        // In a real app, you would check AVCaptureDevice.authorizationStatus
        print("Checking camera permission...")
    }
    
    /// Display a translation in the UI
    func displayTranslation(_ translation: String?) {
        guard let translation = translation else {
            print("Cannot display nil translation")
            return
        }
        
        print("Displaying translation: \(translation)")
        
        // Add translation to the fallback text view
        if let fallbackView = fallbackTextView {
            let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .short)
            let newEntry = "[\(timestamp)] \(translation)\n"
            
            DispatchQueue.main.async {
                let currentText = fallbackView.string
                fallbackView.string = currentText + newEntry
                fallbackView.scrollToEndOfDocument(nil)
                fallbackView.needsDisplay = true
            }
        }
    }
    
    /// Change the current language
    func changeLanguage(to language: String?) {
        guard let language = language else {
            print("Cannot change to nil language")
            return
        }
        
        print("Changing language to: \(language)")
        
        // Update the language label
        DispatchQueue.main.async {
            self.languageLabel?.stringValue = language
        }
        
        // In a real implementation, you would also update the AI system
        // and language engine with the new language
    }
    
    private func updateStartStopButton() {
        // Check if button exists before proceeding
        guard let startStopButton = startStopButton else {
            print("Start/Stop button is nil, cannot update")
            return
        }
        
        print("=== Button Update Debug ===")
        print("isRecognizing: \(isRecognizing)")
        print("Start/Stop button subviews count: \(startStopButton.subviews.count)")
        
        // Based on debug output, the structure is:
        // startStopButton.subviews[1] = NSView with 2 subviews
        // startStopButton.subviews[1].subviews[1] = NSTextField (the icon)
        
        var icon: NSTextField?
        
        if startStopButton.subviews.count >= 2,
           let containerView = startStopButton.subviews[1] as? NSView,
           containerView.subviews.count >= 2,
           let textField = containerView.subviews[1] as? NSTextField {
            icon = textField
            print("Found icon using direct path: '\(textField.stringValue)'")
        }
        
        // Fallback: Search recursively if direct path fails
        if icon == nil {
            func findAllTextFields(in view: NSView) -> [NSTextField] {
                var textFields: [NSTextField] = []
                for subview in view.subviews {
                    if let textField = subview as? NSTextField {
                        textFields.append(textField)
                    } else if subview is NSView {
                        textFields.append(contentsOf: findAllTextFields(in: subview))
                    }
                }
                return textFields
            }
            
            let allTextFieldsRecursive = findAllTextFields(in: startStopButton)
            print("Found \(allTextFieldsRecursive.count) text fields recursively")
            
            for textField in allTextFieldsRecursive {
                print("Recursive text field: '\(textField.stringValue)'")
            }
            
            icon = allTextFieldsRecursive.first
        }
        
        // Update the icon if found
        if let icon = icon {
            print("Updating icon from '\(icon.stringValue)' to \(isRecognizing ? "⏹" : "▶")")
            
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
                    
                    print("Updated button to STOP state (red floating)")
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
                    
                    print("Updated button to START state (green floating)")
                }
            }
        } else {
            print("No text fields found to update!")
        }
    }
    
    // MARK: - Button Handlers (must be at class level for @objc)
    
    // --- Start/Stop Recognition Handler ---
    @objc func toggleRecognition() {
        isRecognizing.toggle()
        
        if isRecognizing {
            // Start recognition
            aiSystem?.startRecognition()
            print("Started sign language recognition")
        } else {
            // Stop recognition
            aiSystem?.stopRecognition()
            print("Stopped sign language recognition")
        }
        
        // Update button immediately for better responsiveness
        DispatchQueue.main.async { [weak self] in
            self?.updateStartStopButton()
        }
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
        setupLanguageChangeObserver()
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
        
        // Process frame for AI recognition
        if isRecognizing {
            aiSystem?.processFrame(sampleBuffer)
            
            // Also process for language engine if languages are loaded
            let loadedLanguages = languageEngine?.getLoadedLanguages() ?? []
            if !loadedLanguages.isEmpty {
                languageEngine?.processFrame(sampleBuffer, for: loadedLanguages)
            }
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
        encoder.drawPrimitives(type: .triangleStrip, vertexStart: 0, vertexCount: 4)
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
    
    
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}
    
    // MARK: - Language Change Handling
    
    private func setupLanguageChangeObserver() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleLanguageChangeNotification),
            name: NSNotification.Name("LanguageChanged"),
            object: nil
        )
    }
    
    @objc private func handleLanguageChangeNotification(_ notification: Notification) {
        guard let languageCode = notification.userInfo?["languageCode"] as? String else { 
            print("CameraViewController: No languageCode found in notification")
            return 
        }
        
        print("CameraViewController: Language changed to \(languageCode)")
        
        // Check if this is a real language change or just window opening
        if let currentLanguage = getCurrentLanguageFromUI(), currentLanguage == languageCode {
            print("CameraViewController: Language is already \(languageCode), skipping UI updates")
            return
        }
        
        // Update all three sections
        updateLanguageDisplay(languageCode)
        updateTranslationHeader(languageCode)
        updateAlphabetBar(languageCode)
    }
    
    private func updateLanguageDisplay(_ languageCode: String) {
        // Update language label and flag in camera view
        DispatchQueue.main.async {
            print("CameraViewController: Updating language display to \(languageCode)")
            self.languageLabel?.stringValue = languageCode
            
            // Update flag based on language
            let flag = self.getFlagForLanguage(languageCode)
            self.flagLabel?.stringValue = flag
            print("CameraViewController: Updated flag to \(flag)")
        }
    }
    
    private func updateTranslationHeader(_ languageCode: String) {
        // Update translation area header
        DispatchQueue.main.async {
            print("CameraViewController: Updating translation header to \(languageCode)")
            let flag = self.getFlagForLanguage(languageCode)
            let languageName = self.getLanguageName(languageCode)
            
            // Find and update the header label in the translation area
            if let translationSection = self.view.subviews.first(where: { $0.frame.origin.y == 256 }) {
                print("CameraViewController: Found translation section")
                for subview in translationSection.subviews {
                    if let headerView = subview.subviews.first(where: { $0.frame.origin.y > 200 }) {
                        print("CameraViewController: Found header view")
                        for headerSubview in headerView.subviews {
                            if let headerLabel = headerSubview as? NSTextField {
                                headerLabel.stringValue = "\(flag) \(languageCode) - Sign Language Translations"
                                print("CameraViewController: Updated header to \(headerLabel.stringValue)")
                                break
                            }
                        }
                    }
                }
            } else {
                print("CameraViewController: Could not find translation section")
            }
        }
    }
    
    private func updateAlphabetBar(_ languageCode: String) {
        // Reload alphabet from JSON for the new language
        DispatchQueue.main.async {
            print("CameraViewController: Updating alphabet bar to \(languageCode)")
            
            // Only reload if the language actually changed
            if let currentLanguage = self.getCurrentLanguageFromUI(), currentLanguage != languageCode {
                print("CameraViewController: Language changed from \(currentLanguage) to \(languageCode), reloading alphabet")
                self.reloadAlphabetForLanguage(languageCode)
            } else {
                print("CameraViewController: No language change detected, skipping alphabet reload")
            }
        }
    }
    
    private func getCurrentLanguageFromUI() -> String? {
        // Try to get current language from the header
        if let translationSection = self.view.subviews.first(where: { $0.frame.origin.y == 256 }) {
            for subview in translationSection.subviews {
                if let headerView = subview.subviews.first(where: { $0.frame.origin.y > 200 }) {
                    for headerSubview in headerView.subviews {
                        if let headerLabel = headerSubview as? NSTextField {
                            let headerText = headerLabel.stringValue
                            // Extract language code from header text like "🇺🇸 ASL - Sign Language Translations"
                            if let range = headerText.range(of: "\\b[A-Z]{3}\\b", options: .regularExpression) {
                                return String(headerText[range])
                            }
                        }
                    }
                }
            }
        }
        return nil
    }
    
    private func reloadAlphabetForLanguage(_ languageCode: String) {
        // Load languages.json and find the new language
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let languages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            print("Failed to load languages.json")
            return
        }
        
        // Find the selected language
        guard let selectedLanguage = languages.first(where: { ($0["code"] as? String) == languageCode }),
              let handshapes = selectedLanguage["handshapes"] as? [String] else {
            print("Failed to find handshapes for language: \(languageCode)")
            return
        }
        
        print("Reloading alphabet for \(languageCode): \(handshapes)")
        
        // Find the alphabet bar section and update it
        if let bottomSection = self.view.subviews.first(where: { $0.frame.origin.y == 0 }) {
            print("Found bottom section, starting cleanup...")
            
            // COMPLETE cleanup - remove ALL subviews except the divider
            let allSubviews = bottomSection.subviews
            print("Found \(allSubviews.count) subviews to process")
            
            for subview in allSubviews {
                // Keep only the divider (usually at the bottom)
                if subview.frame.origin.y < 10 && subview.frame.height < 10 {
                    print("Keeping divider at position: \(subview.frame)")
                    continue
                }
                
                print("Removing subview: \(type(of: subview)) at position: \(subview.frame)")
                subview.removeFromSuperview()
            }
            
            // Force immediate layout and display updates
            bottomSection.needsLayout = true
            bottomSection.needsDisplay = true
            
            // Force the view to redraw immediately
            bottomSection.layer?.setNeedsDisplay()
            
            // Ensure we're on the main thread and add a small delay for cleanup
            DispatchQueue.main.async {
                // Force another layout pass
                bottomSection.layoutSubtreeIfNeeded()
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    print("Cleanup complete, creating new alphabet grid...")
                    // Create new alphabet grid
                    self.createAlphabetGrid(in: bottomSection, handshapes: handshapes)
                }
            }
        } else {
            print("ERROR: Could not find bottom section for alphabet update")
        }
    }
    
    private func createAlphabetGrid(in section: NSView, handshapes: [String]) {
        let width = section.frame.width
        let height = section.frame.height
        
        // Fixed 12-column grid layout for consistency
        let letterSize: CGFloat = 35
        let letterSpacing: CGFloat = 8
        let columnsPerRow = 12  // Fixed 12 columns
        let rows = Int(ceil(Double(handshapes.count) / Double(columnsPerRow)))
        
        // Calculate spacing to center the grid horizontally
        let totalGridWidth = CGFloat(columnsPerRow) * letterSize + CGFloat(columnsPerRow - 1) * letterSpacing
        let startX = (width - totalGridWidth) / 2
        
        // Calculate total grid height and center it vertically
        let totalGridHeight = CGFloat(rows) * (letterSize + letterSpacing) - letterSpacing
        let startY = (height - totalGridHeight) / 2
        
        print("Creating alphabet grid: \(handshapes.count) letters, \(columnsPerRow) columns, \(rows) rows")
        print("Grid dimensions: \(totalGridWidth) x \(totalGridHeight), starting at (\(startX), \(startY))")
        
        // Create letter buttons in grid layout
        for (index, letter) in handshapes.enumerated() {
            let row = index / columnsPerRow
            let column = index % columnsPerRow
            
            let x = startX + CGFloat(column) * (letterSize + letterSpacing)
            let y = startY + CGFloat(row) * (letterSize + letterSpacing)
            
            let letterButton = createAlphabetButton(
                letter: letter,
                position: CGPoint(x: x, y: y),
                size: CGSize(width: letterSize, height: letterSize)
            )
            
            // Ensure the button is properly added and positioned
            section.addSubview(letterButton)
            letterButton.needsDisplay = true
        }
        
        // Force the section to redraw
        section.needsLayout = true
        section.needsDisplay = true
        
        print("Alphabet grid created with \(handshapes.count) buttons")
    }
    
    private func createAlphabetButton(letter: String, position: CGPoint, size: CGSize) -> NSButton {
        let button = NSButton(title: letter, target: self, action: #selector(letterButtonClicked(_:)))
        button.frame = NSRect(origin: position, size: size)
        button.wantsLayer = true
        button.isBordered = false
        
        // Style the button
        button.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.1).cgColor
        button.layer?.cornerRadius = 8
        button.layer?.borderWidth = 1.5
        button.layer?.borderColor = NSColor.systemBlue.withAlphaComponent(0.3).cgColor
        
        // Add shadow
        button.layer?.shadowColor = NSColor.black.cgColor
        button.layer?.shadowOffset = CGSize(width: 0, height: 2)
        button.layer?.shadowOpacity = 0.1
        button.layer?.shadowRadius = 4
        
        // Style the title
        button.font = NSFont.systemFont(ofSize: 16, weight: .semibold)
        button.contentTintColor = NSColor.systemBlue
        
        // Add tracking area for hover effects
        let trackingArea = NSTrackingArea(
            rect: button.bounds,
            options: [.mouseEnteredAndExited, .activeInActiveApp],
            owner: self,
            userInfo: ["button": button]
        )
        button.addTrackingArea(trackingArea)
        
        return button
    }
    
    @objc private func letterButtonClicked(_ sender: NSButton) {
        print("Letter clicked: \(sender.title)")
        // You can add translation display logic here
    }
    
    override func mouseEntered(with event: NSEvent) {
        if let trackingArea = event.trackingArea,
           let button = trackingArea.userInfo?["button"] as? NSButton {
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.2
                context.timingFunction = CAMediaTimingFunction(name: .easeOut)
                
                button.animator().layer?.transform = CATransform3DMakeScale(1.1, 1.1, 1.0)
                button.animator().layer?.shadowOpacity = 0.3
                button.animator().layer?.shadowRadius = 8
                button.animator().layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.2).cgColor
            })
        }
    }
    
    override func mouseExited(with event: NSEvent) {
        if let trackingArea = event.trackingArea,
           let button = trackingArea.userInfo?["button"] as? NSButton {
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.2
                context.timingFunction = CAMediaTimingFunction(name: .easeIn)
                
                button.animator().layer?.transform = CATransform3DIdentity
                button.animator().layer?.shadowOpacity = 0.1
                button.animator().layer?.shadowRadius = 4
                button.animator().layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.1).cgColor
            })
        }
    }
    
    private func getFlagForLanguage(_ languageCode: String) -> String {
        let flags: [String: String] = [
            "ASL": "🇺🇸", "BSL": "🇬🇧", "ISL": "🇮🇳", "JSL": "🇯🇵", "KSL": "🇰🇷",
            "CSL": "🇨🇳", "FSL": "🇫🇷", "DSL": "🇩🇪"
        ]
        return flags[languageCode] ?? "🌐"
    }
    
    private func getLanguageName(_ languageCode: String) -> String {
        let names: [String: String] = [
            "ASL": "American Sign Language", "BSL": "British Sign Language",
            "ISL": "Indian Sign Language", "JSL": "Japanese Sign Language",
            "KSL": "Korean Sign Language", "CSL": "Chinese Sign Language",
            "FSL": "French Sign Language", "DSL": "German Sign Language"
        ]
        return names[languageCode] ?? languageCode
    }
}
