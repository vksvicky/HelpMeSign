import Cocoa
import Foundation

@objc class MainWindowController: NSViewController {
    // MARK: - UI State
    var isRecognizing = false
    
    // MARK: - AI & ML Components
    private var aiSystem: AIUserExperienceSystem!
    private var languageEngine: LanguageEngine!
    
    // MARK: - Section Views
    private var cameraSectionView: CameraSectionView!
    private var translationSectionView: TranslationSectionView!
    private var alphabetSectionView: AlphabetSectionView!

    override func loadView() {
        let width: CGFloat = 1024
        let height: CGFloat = 1024
        let topHeight = height * 0.5
        let midHeight = height * 0.2
        let botHeight = height * 0.3
        let container = NSView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        container.wantsLayer = true
        
        // Create gradient background for the whole window to show section boundaries
        let gradientLayer = CAGradientLayer()
        gradientLayer.frame = container.bounds
        gradientLayer.colors = [
            NSColor(calibratedWhite: 0.95, alpha: 1.0).cgColor,
            NSColor(calibratedWhite: 0.90, alpha: 1.0).cgColor,
            NSColor(calibratedWhite: 0.85, alpha: 1.0).cgColor
        ]
        gradientLayer.locations = [0.0, 0.5, 1.0]
        gradientLayer.startPoint = CGPoint(x: 0.5, y: 1.0)
        gradientLayer.endPoint = CGPoint(x: 0.5, y: 0.0)
        container.layer?.addSublayer(gradientLayer)

        // --- Top Section: Camera View ---
        let topSection = NSView(frame: NSRect(x: 0, y: height - topHeight, width: width, height: topHeight))
        topSection.wantsLayer = true
        topSection.layer?.backgroundColor = NSColor.clear.cgColor
        
        cameraSectionView = CameraSectionView(frame: topSection.bounds)
        cameraSectionView.onStartStopTapped = { [weak self] in
            self?.toggleRecognition()
        }
        topSection.addSubview(cameraSectionView)
        container.addSubview(topSection)

        // --- Middle Section: Translation Display ---
        let midSection = NSView(frame: NSRect(x: 0, y: botHeight, width: width, height: midHeight))
        midSection.wantsLayer = true
        midSection.layer?.backgroundColor = NSColor.clear.cgColor
        
        translationSectionView = TranslationSectionView(frame: midSection.bounds)
        translationSectionView.onClearTapped = { [weak self] in
            self?.clearTranslations()
        }
        midSection.addSubview(translationSectionView)
        container.addSubview(midSection)

        // --- Bottom Section: Alphabet Bar ---
        let botSection = NSView(frame: NSRect(x: 0, y: 0, width: width, height: botHeight))
        botSection.wantsLayer = true
        botSection.layer?.backgroundColor = NSColor.clear.cgColor
        
        alphabetSectionView = AlphabetSectionView(frame: botSection.bounds)
        alphabetSectionView.onLetterClicked = { [weak self] letter in
            self?.handleLetterClicked(letter)
        }
        alphabetSectionView.onWritingSystemChanged = { [weak self] writingSystem in
            self?.handleWritingSystemChanged(writingSystem)
        }
        botSection.addSubview(alphabetSectionView)
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
        // Add translation to the history
        translationSectionView.addTranslation(result.sign, confidence: result.confidence)
        
        // Update language display
        cameraSectionView.updateLanguageDisplay(result.language.code, flag: result.language.flag)
    }
    
    private func handleLanguageChange(_ language: SignLanguage) {
        // Update UI for new language
        cameraSectionView.updateLanguageDisplay(language.code, flag: language.flag)
        translationSectionView.updateLanguageDisplay(language.code)
    }
    
    private func handleRecognitionStateChange(_ isActive: Bool) {
        // Update recognition state
        isRecognizing = isActive
        translationSectionView.setRecognitionStatus(isActive)
        
        // Update button state
        cameraSectionView.updateStartStopButton(isRecognizing: isActive)
    }
    
    private func handleLanguageEngineRecognition(_ result: RecognitionResult) {
        // Handle recognition from language engine
        translationSectionView.addTranslation(result.sign, confidence: result.confidence)
    }
    
    private func handleTranslation(_ result: TranslationResult) {
        // Handle translation result
        translationSectionView.addTranslation(result.targetSign, confidence: result.confidence)
    }
    
    // MARK: - Public Methods for Testing
    
    /// Check camera permission status
    func checkCameraPermission() {
        // This is a simplified implementation for testing
        // In a real app, you would check AVCaptureDevice.authorizationStatus
    }
    
    /// Display a translation in the UI
    func displayTranslation(_ translation: String?) {
        guard let translation = translation else {
            return
        }
        
        // Only update UI if views are loaded and on main thread
        DispatchQueue.main.async { [weak self] in
            guard let self = self, self.isViewLoaded else { return }
            self.translationSectionView?.addTranslation(translation)
        }
    }
    
    /// Change the current language
    func changeLanguage(to language: String?) {
        guard let language = language else {
            return
        }
        
        // Only update UI if views are loaded and on main thread
        DispatchQueue.main.async { [weak self] in
            guard let self = self, self.isViewLoaded else { return }
            // Update the language display
            self.cameraSectionView?.updateLanguageDisplay(language, flag: "🇺🇸")
            
            // Reload alphabet for the new language
            self.alphabetSectionView?.reloadAlphabetForLanguage(language)
        }
        
        // In a real implementation, you would also update the AI system
        // and language engine with the new language
    }
    
    // MARK: - Actions
    
    private func toggleRecognition() {
        isRecognizing.toggle()
        
        if isRecognizing {
            // Start recognition
            aiSystem?.startRecognition()
        } else {
            // Stop recognition
            aiSystem?.stopRecognition()
        }
        
        // Update button immediately for better responsiveness
        DispatchQueue.main.async { [weak self] in
            self?.cameraSectionView?.updateStartStopButton(isRecognizing: self?.isRecognizing ?? false)
        }
    }
    
    private func clearTranslations() {
        translationSectionView?.clearTranslations()
    }
    
    private func handleLetterClicked(_ letter: String) {
        // Handle letter button clicks
        // You can add translation display logic here
    }
    
    private func handleWritingSystemChanged(_ writingSystem: String) {
        // Handle writing system changes
        // This could trigger a reload of the alphabet with the new writing system
    }
    
    // MARK: - View Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupLanguageChangeObserver()
        
        // Load saved language preference AFTER AppDelegate has had a chance to set defaults
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            self.loadSavedLanguagePreference()
        }
    }
    
    // MARK: - Language Preference Loading
    
    private func loadSavedLanguagePreference() {
        // Get saved language preference
        let savedLanguage = UserDefaults.standard.string(forKey: "SelectedLanguage") ?? "ASL"
        
        // Update the UI with the saved language
        DispatchQueue.main.async {
            self.changeLanguage(to: savedLanguage)
        }
    }
    
    // MARK: - Language Change Handling
    
    private func setupLanguageChangeObserver() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleLanguageChangeNotification),
            name: NSNotification.Name("LanguageChanged"),
            object: nil
        )
        
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleHandPreferenceChangeNotification),
            name: NSNotification.Name("HandPreferenceChanged"),
            object: nil
        )
    }
    
    @objc private func handleLanguageChangeNotification(_ notification: Notification) {
        guard let languageCode = notification.userInfo?["languageCode"] as? String else { 
            return 
        }
        
        // Update all sections
        changeLanguage(to: languageCode)
    }
    
    @objc private func handleHandPreferenceChangeNotification(_ notification: Notification) {
        guard let handPreference = notification.userInfo?["handPreference"] as? String else { 
            return 
        }
        
        // Update AI system with new hand preference
        aiSystem?.updateHandPreference(handPreference)
        
        // Update language engine with new hand preference
        languageEngine?.updateHandPreference(handPreference)
    }
} 