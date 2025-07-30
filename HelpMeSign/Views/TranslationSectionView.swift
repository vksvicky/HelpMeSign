import Cocoa

class TranslationSectionView: NSView {
    
    // MARK: - UI Elements
    private var scrollView: NSScrollView!
    private var textView: NSTextView!
    private var clearButton: NSButton!
    
    // MARK: - Callbacks
    var onClearTapped: (() -> Void)?
    
    // MARK: - Data
    private var lastTranslation: String = ""
    private var lastTranslationTime: Date = Date.distantPast
    private let translationCooldown: TimeInterval = 2.0 // 2 second cooldown for same translation
    
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
        
        setupTranslationDisplay()
        setupClearButton()
    }
    
    // MARK: - Translation Display Setup
    private func setupTranslationDisplay() {
        let height = bounds.height
        
        // Create scroll view for main text view - full height, no border
        scrollView = NSScrollView(frame: NSRect(x: bounds.width * 0.1, y: height * 0.05, width: bounds.width * 0.8, height: height * 0.9))
        scrollView.hasVerticalScroller = true
        scrollView.hasHorizontalScroller = false
        scrollView.autohidesScrollers = true
        scrollView.scrollerStyle = .overlay
        scrollView.borderType = .noBorder
        scrollView.wantsLayer = true
        scrollView.layer?.cornerRadius = 8
        
        // Create main text view inside scroll view with proper size
        let textViewWidth = scrollView.frame.width - 20
        let textViewHeight = scrollView.frame.height - 40
        textView = NSTextView(frame: NSRect(x: 0, y: 0, width: textViewWidth, height: textViewHeight))
        textView.string = "Ready for translations..." // Add initial text to verify visibility
        textView.isEditable = false
        textView.backgroundColor = NSColor.white
        textView.font = NSFont.systemFont(ofSize: 16)
        textView.textColor = NSColor.black // Force black text for visibility
        textView.isSelectable = true
        textView.isVerticallyResizable = true
        textView.isHorizontallyResizable = false
        textView.textContainer?.containerSize = NSSize(width: textViewWidth, height: CGFloat.greatestFiniteMagnitude)
        textView.textContainer?.widthTracksTextView = true
        
        // Add subtle border for visual clarity
        textView.wantsLayer = true
        textView.layer?.borderWidth = 1
        textView.layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.3).cgColor
        
        scrollView.documentView = textView
        addSubview(scrollView)
    }
    
    // MARK: - Clear Button Setup
    private func setupClearButton() {
        // Add clear button outside the text area (positioned to the right of scroll view)
        clearButton = NSButton(title: "🧹", target: self, action: #selector(clearButtonTapped))
        clearButton.bezelStyle = NSButton.BezelStyle.regularSquare
        clearButton.frame = NSRect(x: scrollView.frame.maxX + 10, y: scrollView.frame.minY + 5, width: 36, height: 28)
        clearButton.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        clearButton.wantsLayer = true
        clearButton.layer?.backgroundColor = NSColor.white.withAlphaComponent(0.9).cgColor
        clearButton.layer?.cornerRadius = 4
        clearButton.layer?.borderWidth = 1
        clearButton.layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.3).cgColor
        clearButton.toolTip = "Clear all translations"
        addSubview(clearButton)
    }
    
    // MARK: - Public Methods
    func addTranslation(_ translation: String, confidence: Float = 1.0) {
        let now = Date()
        
        // Check if this is the same translation as the last one
        if translation == lastTranslation {
            let timeSinceLastTranslation = now.timeIntervalSince(lastTranslationTime)
            
            // If same translation was shown recently, skip it
            if timeSinceLastTranslation < translationCooldown {
                NSLog("TranslationDisplay: Skipping repeated translation '\(translation)' (shown \(timeSinceLastTranslation)s ago)")
                return
            }
        }
        
        let timestamp = DateFormatter.localizedString(from: now, dateStyle: .none, timeStyle: .short)
        let confidencePercentage = Int(confidence * 100)
        let entry = "[\(timestamp)] \(translation) (\(confidencePercentage)%)\n"
        
        DispatchQueue.main.async {
            let currentText = self.textView.string
            self.textView.string = currentText + entry
            self.textView.scrollToEndOfDocument(nil)
            
            // Force refresh the text view
            self.textView.needsDisplay = true
            self.textView.needsLayout = true
        }
        
        // Update last translation info
        lastTranslation = translation
        lastTranslationTime = now
    }
    
    func clearTranslations() {
        DispatchQueue.main.async {
            self.textView.string = ""
        }
    }
    
    func updateLanguageDisplay(_ languageCode: String) {
        // This could be used to update any language-specific UI elements
        // For now, we'll keep it simple
    }
    
    func setRecognitionStatus(_ isActive: Bool) {
        // This could be used to show recognition status
        // For now, we'll keep it simple
    }
    
    // MARK: - Actions
    @objc private func clearButtonTapped() {
        clearTranslations()
        onClearTapped?()
    }
} 