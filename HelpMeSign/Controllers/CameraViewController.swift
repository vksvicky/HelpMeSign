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
    var blurBackground = false
    var centerFrame = false
    
    // MARK: - AI & ML Components
    private var aiSystem: AIUserExperienceSystem!
    private var languageEngine: LanguageEngine!
    private var translationDisplayView: TranslationDisplayView!

    // MARK: - UI Elements
    var camView: NSView!
    var overlay: HoverOverlayView!
    var startStopButton: NSButton!
    var blurButton: NSButton!
    var pulseLayer: CALayer?
    var languageLabel: NSTextField!
    var flagLabel: NSTextField!
    var aiStatusLabel: NSTextField!
    var fallbackTextView: NSTextView!
    
    // Private property to track if view has been loaded
    private var viewHasBeenLoaded = false

    override func loadView() {
        // Only create the view if it hasn't already been loaded
        if viewHasBeenLoaded {
            return
        }
        
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
        
        // AI Status Display (below camera view)
        let aiStatusContainer = NSView(frame: NSRect(x: 0, y: -60, width: camWidth, height: 50))
        aiStatusContainer.wantsLayer = true
        aiStatusContainer.layer?.backgroundColor = NSColor.white.withAlphaComponent(0.95).cgColor
        aiStatusContainer.layer?.cornerRadius = 12
        aiStatusContainer.layer?.borderWidth = 1
        aiStatusContainer.layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.2).cgColor
        
        // AI Status Label
        let aiStatusLabel = NSTextField(labelWithString: "AI Recognition Inactive")
        aiStatusLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        aiStatusLabel.textColor = NSColor.systemGray
        aiStatusLabel.alignment = .center
        aiStatusLabel.frame = NSRect(x: 0, y: 0, width: camWidth, height: 50)
        aiStatusContainer.addSubview(aiStatusLabel)
        
        // Store reference for later updates
        self.aiStatusLabel = aiStatusLabel
        
        camView.addSubview(aiStatusContainer)
        
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
        // Feature button (left) - Innovative Mini Design
        let featureSize: CGFloat = 40
        blurButton = NSButton(title: "", target: self, action: #selector(toggleBlur))
        blurButton.bezelStyle = .regularSquare
        blurButton.setFrameSize(NSSize(width: featureSize, height: featureSize))
        blurButton.frame.origin = CGPoint(x: 20, y: (overlayHeight - featureSize)/2)
        blurButton.wantsLayer = true
        blurButton.layer?.cornerRadius = featureSize/2
        blurButton.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.8).cgColor
        blurButton.layer?.borderWidth = 0
        
        // Add floating shadow effect
        blurButton.layer?.shadowColor = NSColor.black.cgColor
        blurButton.layer?.shadowOffset = CGSize(width: 0, height: 4)
        blurButton.layer?.shadowOpacity = 0.2
        blurButton.layer?.shadowRadius = 6
        
        let blurIcon = NSTextField(labelWithString: "💧")
        blurIcon.font = NSFont.systemFont(ofSize: 18)
        blurIcon.backgroundColor = .clear
        blurIcon.isBordered = false
        blurIcon.isEditable = false
        blurIcon.textColor = .systemGray // Start with gray to show it's off
        blurIcon.alignment = .center
        blurIcon.sizeToFit()
        
        // Center the icon properly
        let blurIconX = (featureSize - blurIcon.frame.width) / 2
        let blurIconY = (featureSize - blurIcon.frame.height) / 2
        blurIcon.frame = NSRect(x: blurIconX, y: blurIconY, width: blurIcon.frame.width, height: blurIcon.frame.height)
        blurButton.addSubview(blurIcon)
        blurButton.contentTintColor = .systemBlue
        blurButton.toolTip = "Blur Background (Click to toggle)"
        
        // Add hover effect
        blurButton.addTrackingArea(NSTrackingArea(rect: blurButton.bounds, options: [.mouseEnteredAndExited, .activeInActiveApp], owner: self, userInfo: nil))
        
        overlay.addSubview(blurButton)
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
        
        // Debug: Print button properties
        print("=== Button Creation Debug ===")
        print("Button size: \(startStopButton.frame.size)")
        print("Button corner radius: \(startStopButton.layer?.cornerRadius ?? 0)")
        print("Button background color: \(startStopButton.layer?.backgroundColor != nil ? "set" : "nil")")
        print("Button title: '\(startStopButton.title)'")
        print("Button isBordered: \(startStopButton.isBordered)")
        print("Button subviews count: \(startStopButton.subviews.count)")
        
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
        viewHasBeenLoaded = true
        
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
    
    private func updateStartStopButton() {
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

    // --- Start/Stop Recognition Handler ---
    @objc func toggleRecognition() {
        isRecognizing.toggle()
        
        if isRecognizing {
            // Start recognition
            aiSystem?.startRecognition()
            aiStatusLabel.stringValue = "AI Recognition Active"
            aiStatusLabel.textColor = NSColor.systemGreen
            print("Started sign language recognition")
        } else {
            // Stop recognition
            aiSystem?.stopRecognition()
            aiStatusLabel.stringValue = "AI Recognition Inactive"
            aiStatusLabel.textColor = NSColor.systemGray
            print("Stopped sign language recognition")
        }
        
        // Update button immediately for better responsiveness
        DispatchQueue.main.async { [weak self] in
            self?.updateStartStopButton()
        }
    }

    // --- Feature Button Handlers ---
    @objc func toggleBlur() {
        blurBackground.toggle()
        
        // Update button visual state with animation
        if let blurIcon = blurButton.subviews.first as? NSTextField {
            NSAnimationContext.runAnimationGroup { context in
                context.duration = 0.2
                context.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
                
                if blurBackground {
                    // Active state
                    blurButton.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.25).cgColor
                    blurButton.layer?.borderColor = NSColor.systemBlue.cgColor
                    blurButton.layer?.borderWidth = 2
                    blurIcon.textColor = .systemBlue
                    
                    // Add subtle glow effect
                    blurButton.layer?.shadowColor = NSColor.systemBlue.cgColor
                    blurButton.layer?.shadowOpacity = 0.3
                    blurButton.layer?.shadowRadius = 4
                } else {
                    // Inactive state
                    blurButton.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.1).cgColor
                    blurButton.layer?.borderColor = NSColor.systemBlue.withAlphaComponent(0.4).cgColor
                    blurButton.layer?.borderWidth = 1.5
                    blurIcon.textColor = .systemGray
                    
                    // Remove glow effect
                    blurButton.layer?.shadowColor = NSColor.black.cgColor
                    blurButton.layer?.shadowOpacity = 0.15
                    blurButton.layer?.shadowRadius = 2
                }
            }
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
        var blurFlag = blurBackground
        encoder.setFragmentBytes(&blurFlag, length: MemoryLayout<Bool>.size, index: 0)
        encoder.drawPrimitives(type: .triangleStrip, vertexStart: 0, vertexCount: 4)
        encoder.endEncoding()
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }
    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {}
}

