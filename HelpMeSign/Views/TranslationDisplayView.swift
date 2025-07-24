import Cocoa

// MARK: - Translation Display View
class TranslationDisplayView: NSView {
    
    // MARK: - UI Elements
    private var translationLabel: NSTextField!
    private var confidenceLabel: NSTextField!
    private var languageLabel: NSTextField!
    private var statusLabel: NSTextField!
    
    // MARK: - Data
    private var currentSign: String = ""
    private var currentConfidence: Float = 0.0
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
        // Status label
        statusLabel = NSTextField(labelWithString: "AI Sign Language Recognition")
        statusLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        statusLabel.textColor = NSColor.secondaryLabelColor
        statusLabel.alignment = .center
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(statusLabel)
        
        // Main translation label
        translationLabel = NSTextField(labelWithString: "Ready for sign recognition")
        translationLabel.font = NSFont.systemFont(ofSize: 24, weight: .medium)
        translationLabel.textColor = NSColor.labelColor
        translationLabel.alignment = .center
        translationLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(translationLabel)
        
        // Confidence indicator
        confidenceLabel = NSTextField(labelWithString: "")
        confidenceLabel.font = NSFont.systemFont(ofSize: 12, weight: .regular)
        confidenceLabel.textColor = NSColor.secondaryLabelColor
        confidenceLabel.alignment = .center
        confidenceLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(confidenceLabel)
        
        // Language indicator
        languageLabel = NSTextField(labelWithString: "🇺🇸 ASL")
        languageLabel.font = NSFont.systemFont(ofSize: 14, weight: .semibold)
        languageLabel.textColor = NSColor.systemBlue
        languageLabel.alignment = .center
        languageLabel.translatesAutoresizingMaskIntoConstraints = false
        addSubview(languageLabel)
        
        // Constraints
        NSLayoutConstraint.activate([
            statusLabel.centerXAnchor.constraint(equalTo: centerXAnchor),
            statusLabel.topAnchor.constraint(equalTo: topAnchor, constant: 20),
            statusLabel.leadingAnchor.constraint(greaterThanOrEqualTo: leadingAnchor, constant: 20),
            statusLabel.trailingAnchor.constraint(lessThanOrEqualTo: trailingAnchor, constant: -20),
            
            translationLabel.centerXAnchor.constraint(equalTo: centerXAnchor),
            translationLabel.centerYAnchor.constraint(equalTo: centerYAnchor),
            translationLabel.leadingAnchor.constraint(greaterThanOrEqualTo: leadingAnchor, constant: 20),
            translationLabel.trailingAnchor.constraint(lessThanOrEqualTo: trailingAnchor, constant: -20),
            
            confidenceLabel.centerXAnchor.constraint(equalTo: centerXAnchor),
            confidenceLabel.topAnchor.constraint(equalTo: translationLabel.bottomAnchor, constant: 8),
            confidenceLabel.leadingAnchor.constraint(greaterThanOrEqualTo: leadingAnchor, constant: 20),
            confidenceLabel.trailingAnchor.constraint(lessThanOrEqualTo: trailingAnchor, constant: -20),
            
            languageLabel.centerXAnchor.constraint(equalTo: centerXAnchor),
            languageLabel.topAnchor.constraint(equalTo: confidenceLabel.bottomAnchor, constant: 8),
            languageLabel.leadingAnchor.constraint(greaterThanOrEqualTo: leadingAnchor, constant: 20),
            languageLabel.trailingAnchor.constraint(lessThanOrEqualTo: trailingAnchor, constant: -20)
        ])
    }
    
    // MARK: - Public Methods
    
    /// Update the current translation display
    func updateTranslation(sign: String, confidence: Float, language: String) {
        currentSign = sign
        currentConfidence = confidence
        currentLanguage = language
        
        // Update main translation label
        translationLabel.stringValue = sign
        translationLabel.textColor = NSColor.labelColor
        
        // Update confidence indicator
        let confidencePercentage = Int(confidence * 100)
        confidenceLabel.stringValue = "Confidence: \(confidencePercentage)%"
        
        // Update confidence color based on level
        if confidence >= 0.9 {
            confidenceLabel.textColor = NSColor.systemGreen
        } else if confidence >= 0.7 {
            confidenceLabel.textColor = NSColor.systemOrange
        } else {
            confidenceLabel.textColor = NSColor.systemRed
        }
        
        // Update language label
        updateLanguageDisplay(language)
    }
    
    /// Update the language display
    func updateLanguageDisplay(_ languageCode: String) {
        let flag = getFlagForLanguage(languageCode)
        languageLabel.stringValue = "\(flag) \(languageCode)"
    }
    
    /// Clear the current translation
    func clearTranslation() {
        currentSign = ""
        currentConfidence = 0.0
        translationLabel.stringValue = "Ready for sign recognition"
        translationLabel.textColor = NSColor.secondaryLabelColor
        confidenceLabel.stringValue = ""
        languageLabel.stringValue = "🇺🇸 ASL"
    }
    
    /// Set recognition status
    func setRecognitionStatus(_ isActive: Bool) {
        if isActive {
            statusLabel.stringValue = "AI Recognition Active"
            statusLabel.textColor = NSColor.systemGreen
        } else {
            statusLabel.stringValue = "AI Recognition Inactive"
            statusLabel.textColor = NSColor.systemGray
        }
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