import Cocoa

// MARK: - Translation Display View
class TranslationDisplayView: NSView {
    
    // MARK: - UI Elements
    private var translationScrollView: NSScrollView!
    private var translationTextView: NSTextView!
    private var languageLabel: NSTextField!
    private var clearButton: NSButton!
    
    // MARK: - Data
    private var translationHistory: [String] = []
    private var currentLanguage: String = "ASL"
    
    // MARK: - Callbacks
    var onClearHistory: (() -> Void)?
    var onLanguageSelected: ((String) -> Void)?
    
    // MARK: - Initialization
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        setupView()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupView()
    }
    
    // MARK: - Setup
    private func setupView() {
        wantsLayer = true
        layer?.backgroundColor = NSColor(calibratedWhite: 0.98, alpha: 1.0).cgColor
        layer?.cornerRadius = 12
        layer?.borderWidth = 1
        layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.2).cgColor
        
        setupTranslationDisplay()
    }
    
    private func setupTranslationDisplay() {
        // Header with language indicator
        languageLabel = NSTextField(labelWithString: "🇺🇸 ASL - Sign Language Translations")
        languageLabel.font = NSFont.systemFont(ofSize: 16, weight: .semibold)
        languageLabel.textColor = NSColor.systemBlue
        languageLabel.alignment = .center
        languageLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(languageLabel)
        
        // Clear button
        clearButton = NSButton(title: "Clear", target: self, action: #selector(clearHistoryAction))
        clearButton.bezelStyle = .rounded
        clearButton.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        clearButton.translatesAutoresizingMaskIntoConstraints = false
        addSubview(clearButton)
        
        // Translation text view in scroll view
        translationTextView = NSTextView()
        translationTextView.font = NSFont.systemFont(ofSize: 18, weight: .medium)
        translationTextView.textColor = NSColor.labelColor
        translationTextView.backgroundColor = NSColor.clear
        translationTextView.isEditable = false
        translationTextView.isSelectable = true
        translationTextView.string = "Ready for sign recognition...\n\nTranslations will appear here as you sign."
        
        // Scroll view
        translationScrollView = NSScrollView()
        translationScrollView.hasVerticalScroller = true
        translationScrollView.hasHorizontalScroller = false
        translationScrollView.autohidesScrollers = true
        translationScrollView.borderType = .lineBorder
        translationScrollView.translatesAutoresizingMaskIntoConstraints = false
        
        // Set the text view as the document view
        translationScrollView.documentView = translationTextView
        
        addSubview(translationScrollView)
        
        // Constraints
        NSLayoutConstraint.activate([
            languageLabel.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            languageLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            languageLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            
            clearButton.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            clearButton.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            clearButton.widthAnchor.constraint(equalToConstant: 60),
            clearButton.heightAnchor.constraint(equalToConstant: 24),
            
            translationScrollView.topAnchor.constraint(equalTo: languageLabel.bottomAnchor, constant: 12),
            translationScrollView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 16),
            translationScrollView.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -16),
            translationScrollView.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -16)
        ])
    }
    
    // MARK: - Public Methods
    
    /// Add a new translation to the history
    func addTranslation(_ translation: String, confidence: Float = 1.0) {
        print("📝 TranslationDisplayView.addTranslation called with: \(translation)")
        
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .short)
        let confidencePercentage = Int(confidence * 100)
        let entry = "[\(timestamp)] \(translation) (\(confidencePercentage)%)"
        
        translationHistory.append(entry)
        print("📝 Added entry: \(entry)")
        print("📝 Total entries: \(translationHistory.count)")
        
        // Update the text view
        updateTranslationDisplay()
        
        // Scroll to bottom
        DispatchQueue.main.async {
            self.translationTextView.scrollToEndOfDocument(nil)
        }
    }
    
    /// Update the language display
    func updateLanguageDisplay(_ languageCode: String) {
        currentLanguage = languageCode
        let flag = getFlagForLanguage(languageCode)
        languageLabel.stringValue = "\(flag) \(languageCode) - Sign Language Translations"
    }
    
    /// Clear all translations
    func clearTranslations() {
        translationHistory.removeAll()
        updateTranslationDisplay()
    }
    
    /// Set recognition status (this will be moved to camera view)
    func setRecognitionStatus(_ isActive: Bool) {
        // This method is deprecated - status will be shown in camera view
    }
    
    // MARK: - Private Methods
    
    private func updateTranslationDisplay() {
        print("📝 updateTranslationDisplay called, history count: \(translationHistory.count)")
        
        if translationHistory.isEmpty {
            translationTextView.string = "Ready for sign recognition...\n\nTranslations will appear here as you sign."
            print("📝 Set empty state text")
        } else {
            let displayText = translationHistory.joined(separator: "\n")
            translationTextView.string = displayText
            print("📝 Set display text with \(translationHistory.count) entries")
            print("📝 Display text: \(displayText)")
        }
    }
    
    @objc private func clearHistoryAction() {
        clearTranslations()
        onClearHistory?()
    }
    
    // MARK: - Helper Methods
    
    private func getFlagForLanguage(_ languageCode: String) -> String {
        let flagMap: [String: String] = [
            "ASL": "🇺🇸",
            "BSL": "🇬🇧",
            "ISL": "🇮🇳",
            "JSL": "🇯🇵",
            "KSL": "🇰🇷",
            "CSL": "🇨🇳",
            "FSL": "🇫🇷",
            "DSL": "🇩🇪",
            "LIS": "🇮🇹",
            "LSE": "🇪🇸",
            "RUS": "🇷🇺",
            "PSL": "🇵🇱",
            "TSL": "🇹🇷",
            "ARSL": "🇸🇦",
            "HZSL": "🇮🇱",
            "THSL": "🇹🇭",
            "VSL": "🇻🇳",
            "MSL": "🇲🇾",
            "IDSL": "🇮🇩",
            "PHSL": "🇵🇭"
        ]
        
        return flagMap[languageCode] ?? "🌐"
    }
} 