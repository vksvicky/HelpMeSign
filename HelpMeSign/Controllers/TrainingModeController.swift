import Cocoa

// MARK: - Training Mode Controller
class TrainingModeController: NSViewController {
    
    // MARK: - UI Elements
    private var trainingModeView: TrainingModeView!
    private var sessionSetupView: NSView!
    private var isTrainingModeActive = false
    
    // Session setup elements
    private var languagePopUp: NSPopUpButton!
    private var difficultyPopUp: NSPopUpButton!
    private var startSessionButton: NSButton!
    private var backButton: NSButton!
    
    // MARK: - Data
    private var trainingMode: TrainingMode
    private var currentLanguage: String = "ASL"
    private var currentDifficulty: TrainingMode.TrainingDifficulty = .beginner
    
    // MARK: - Callbacks
    var onTrainingModeExited: (() -> Void)?
    var onRecognitionResult: ((String, Float) -> Void)?
    
    // MARK: - Initialization
    init(trainingMode: TrainingMode) {
        self.trainingMode = trainingMode
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - View Lifecycle
    override func loadView() {
        view = NSView(frame: NSRect(x: 0, y: 0, width: 800, height: 600))
        setupView()
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCallbacks()
        showSessionSetup()
    }
    
    // MARK: - Setup
    private func setupView() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        
        setupSessionSetupView()
        setupTrainingModeView()
    }
    
    private func setupSessionSetupView() {
        sessionSetupView = NSView(frame: view.bounds)
        sessionSetupView.wantsLayer = true
        sessionSetupView.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        view.addSubview(sessionSetupView)
        
        // Title
        let titleLabel = NSTextField(labelWithString: "Training Mode Setup")
        titleLabel.font = NSFont.systemFont(ofSize: 28, weight: .bold)
        titleLabel.textColor = NSColor.systemBlue
        titleLabel.alignment = .center
        titleLabel.frame = NSRect(x: 0, y: view.bounds.height - 100, width: view.bounds.width, height: 40)
        sessionSetupView.addSubview(titleLabel)
        
        // Subtitle
        let subtitleLabel = NSTextField(labelWithString: "Configure your training session")
        subtitleLabel.font = NSFont.systemFont(ofSize: 16)
        subtitleLabel.textColor = NSColor.secondaryLabelColor
        subtitleLabel.alignment = .center
        subtitleLabel.frame = NSRect(x: 0, y: view.bounds.height - 130, width: view.bounds.width, height: 20)
        sessionSetupView.addSubview(subtitleLabel)
        
        // Language Selection
        let languageLabel = NSTextField(labelWithString: "Sign Language:")
        languageLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        languageLabel.textColor = NSColor.labelColor
        languageLabel.frame = NSRect(x: 200, y: view.bounds.height - 200, width: 150, height: 25)
        sessionSetupView.addSubview(languageLabel)
        
        languagePopUp = NSPopUpButton(frame: NSRect(x: 360, y: view.bounds.height - 200, width: 200, height: 25))
        languagePopUp.addItems(withTitles: ["ASL", "BSL", "ISL", "JSL", "KSL"])
        languagePopUp.selectItem(withTitle: currentLanguage)
        languagePopUp.target = self
        languagePopUp.action = #selector(languageChanged)
        sessionSetupView.addSubview(languagePopUp)
        
        // Difficulty Selection
        let difficultyLabel = NSTextField(labelWithString: "Difficulty Level:")
        difficultyLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        difficultyLabel.textColor = NSColor.labelColor
        difficultyLabel.frame = NSRect(x: 200, y: view.bounds.height - 250, width: 150, height: 25)
        sessionSetupView.addSubview(difficultyLabel)
        
        difficultyPopUp = NSPopUpButton(frame: NSRect(x: 360, y: view.bounds.height - 250, width: 200, height: 25))
        difficultyPopUp.addItems(withTitles: TrainingMode.TrainingDifficulty.allCases.map { $0.rawValue })
        difficultyPopUp.selectItem(withTitle: currentDifficulty.rawValue)
        difficultyPopUp.target = self
        difficultyPopUp.action = #selector(difficultyChanged)
        sessionSetupView.addSubview(difficultyPopUp)
        
        // Difficulty Description
        let difficultyDescriptionLabel = NSTextField(labelWithString: currentDifficulty.description)
        difficultyDescriptionLabel.font = NSFont.systemFont(ofSize: 14)
        difficultyDescriptionLabel.textColor = NSColor.secondaryLabelColor
        difficultyDescriptionLabel.alignment = .center
        difficultyDescriptionLabel.frame = NSRect(x: 200, y: view.bounds.height - 280, width: 360, height: 20)
        sessionSetupView.addSubview(difficultyDescriptionLabel)
        
        // Progress Summary
        let progressLabel = NSTextField(labelWithString: "Your Progress:")
        progressLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        progressLabel.textColor = NSColor.labelColor
        progressLabel.frame = NSRect(x: 200, y: view.bounds.height - 350, width: 150, height: 25)
        sessionSetupView.addSubview(progressLabel)
        
        let progressStats = getProgressStats()
        let progressStatsLabel = NSTextField(labelWithString: progressStats)
        progressStatsLabel.font = NSFont.systemFont(ofSize: 14)
        progressStatsLabel.textColor = NSColor.secondaryLabelColor
        progressStatsLabel.frame = NSRect(x: 200, y: view.bounds.height - 380, width: 360, height: 40)
        sessionSetupView.addSubview(progressStatsLabel)
        
        // Start Session Button
        startSessionButton = NSButton(title: "Start Training Session", target: self, action: #selector(startSessionButtonClicked))
        startSessionButton.bezelStyle = .rounded
        startSessionButton.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        startSessionButton.frame = NSRect(x: 300, y: view.bounds.height - 450, width: 200, height: 40)
        sessionSetupView.addSubview(startSessionButton)
        
        // Back Button
        backButton = NSButton(title: "Back to Main App", target: self, action: #selector(backButtonClicked))
        backButton.bezelStyle = .rounded
        backButton.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        backButton.frame = NSRect(x: 50, y: 50, width: 150, height: 30)
        sessionSetupView.addSubview(backButton)
    }
    
    private func setupTrainingModeView() {
        trainingModeView = TrainingModeView(frame: view.bounds, trainingMode: trainingMode)
        trainingModeView.isHidden = true
        view.addSubview(trainingModeView)
        
        // Set up callbacks
        trainingModeView.onSessionEnded = { [weak self] session in
            self?.handleSessionEnded(session)
        }
        
        trainingModeView.onExerciseCompleted = { [weak self] result in
            self?.handleExerciseCompleted(result)
        }
    }
    
    private func setupCallbacks() {
        // Set up any additional callbacks here
    }
    
    // MARK: - Public Methods
    
    /// Show the training mode interface
    func showTrainingMode() {
        isTrainingModeActive = true
        showSessionSetup()
    }
    
    /// Hide the training mode interface
    func hideTrainingMode() {
        isTrainingModeActive = false
        if trainingMode.isActive {
            trainingMode.endTrainingSession()
        }
        onTrainingModeExited?()
    }
    
    /// Update recognition results from the main app
    func updateRecognitionResult(recognizedSign: String, confidence: Float) {
        if isTrainingModeActive && trainingMode.isActive {
            trainingModeView.updateRecognitionResult(recognizedSign: recognizedSign, confidence: confidence)
        }
    }
    
    // MARK: - Private Methods
    
    private func showSessionSetup() {
        sessionSetupView.isHidden = false
        trainingModeView.isHidden = true
        
        // Update progress display
        updateProgressDisplay()
    }
    
    private func showTrainingSession() {
        sessionSetupView.isHidden = true
        trainingModeView.isHidden = false
        
        // Start the training session
        trainingModeView.startSession(language: currentLanguage, difficulty: currentDifficulty)
    }
    
    private func updateProgressDisplay() {
        // Update progress statistics in the setup view
        // This would refresh the progress display when returning to setup
    }
    
    private func getProgressStats() -> String {
        let stats = trainingMode.getTrainingStatistics()
        let progress = trainingMode.getUserProgress(for: currentLanguage)
        
        var statsText = "Total Sessions: \(stats.totalSessions)\n"
        statsText += "Total Exercises: \(stats.totalExercises)\n"
        statsText += "Average Accuracy: \(Int(stats.averageAccuracy * 100))%"
        
        if let progress = progress {
            statsText += "\nBest Accuracy: \(Int(progress.bestAccuracy * 100))%"
        }
        
        return statsText
    }
    
    private func handleSessionEnded(_ session: TrainingMode.TrainingSession) {
        // Show session summary and return to setup
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.showSessionSetup()
        }
    }
    
    private func handleExerciseCompleted(_ result: TrainingMode.TrainingResult) {
        // Handle exercise completion
        NSLog("Training Controller: Exercise completed - \(result.targetSign) → \(result.recognizedSign) (Correct: \(result.isCorrect))")
    }
    
    // MARK: - Actions
    
    @objc private func languageChanged() {
        currentLanguage = languagePopUp.selectedItem?.title ?? "ASL"
        updateProgressDisplay()
    }
    
    @objc private func difficultyChanged() {
        if let difficultyTitle = difficultyPopUp.selectedItem?.title,
           let difficulty = TrainingMode.TrainingDifficulty.allCases.first(where: { $0.rawValue == difficultyTitle }) {
            currentDifficulty = difficulty
            
            // Update difficulty description
            if let descriptionLabel = sessionSetupView.subviews.first(where: { $0 is NSTextField && ($0 as! NSTextField).stringValue.contains("Learn basic signs") }) as? NSTextField {
                descriptionLabel.stringValue = difficulty.description
            }
        }
    }
    
    @objc private func startSessionButtonClicked() {
        showTrainingSession()
    }
    
    @objc private func backButtonClicked() {
        hideTrainingMode()
    }
}

// MARK: - Extensions

extension TrainingModeController {
    /// Check if training mode is currently active
    var isActive: Bool {
        return isTrainingModeActive
    }
    
    /// Get current training session
    var activeSession: TrainingMode.TrainingSession? {
        return trainingMode.activeSession
    }
} 