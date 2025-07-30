import Cocoa

// MARK: - Training Mode View
class TrainingModeView: NSView {
    
    // MARK: - UI Elements
    private var headerView: NSView!
    private var exerciseView: NSView!
    private var progressView: NSView!
    private var feedbackView: NSView!
    
    // Header elements
    private var titleLabel: NSTextField!
    private var difficultyLabel: NSTextField!
    private var scoreLabel: NSTextField!
    private var timerLabel: NSTextField!
    private var endSessionButton: NSButton!
    
    // Exercise elements
    private var targetSignLabel: NSTextField!
    private var instructionsLabel: NSTextField!
    private var hintsLabel: NSTextField!
    private var recognitionStatusLabel: NSTextField!
    private var startExerciseButton: NSButton!
    private var skipExerciseButton: NSButton!
    
    // Progress elements
    private var progressBar: NSProgressIndicator!
    private var accuracyLabel: NSTextField!
    private var exercisesCompletedLabel: NSTextField!
    
    // Feedback elements
    private var feedbackLabel: NSTextField!
    private var correctButton: NSButton!
    private var incorrectButton: NSButton!
    private var feedbackTextField: NSTextField!
    private var submitFeedbackButton: NSButton!
    
    // MARK: - Data
    private var trainingMode: TrainingMode
    private var currentExercise: TrainingMode.TrainingExercise?
    private var exerciseStartTime: Date?
    private var timer: Timer?
    private var timeRemaining: TimeInterval = 0
    
    // MARK: - Callbacks
    var onSessionEnded: ((TrainingMode.TrainingSession) -> Void)?
    var onExerciseCompleted: ((TrainingMode.TrainingResult) -> Void)?
    
    // MARK: - Initialization
    init(frame frameRect: NSRect, trainingMode: TrainingMode) {
        self.trainingMode = trainingMode
        super.init(frame: frameRect)
        setupView()
        setupCallbacks()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Setup
    private func setupView() {
        wantsLayer = true
        layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        
        setupHeaderView()
        setupExerciseView()
        setupProgressView()
        setupFeedbackView()
        
        // Initially hide feedback view
        feedbackView.isHidden = true
    }
    
    private func setupHeaderView() {
        headerView = NSView(frame: NSRect(x: 0, y: bounds.height - 80, width: bounds.width, height: 80))
        headerView.wantsLayer = true
        headerView.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.1).cgColor
        addSubview(headerView)
        
        // Title
        titleLabel = NSTextField(labelWithString: "Training Mode")
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.textColor = NSColor.systemBlue
        titleLabel.alignment = .center
        titleLabel.frame = NSRect(x: 20, y: 50, width: 200, height: 30)
        headerView.addSubview(titleLabel)
        
        // Difficulty
        difficultyLabel = NSTextField(labelWithString: "Difficulty: Beginner")
        difficultyLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        difficultyLabel.textColor = NSColor.secondaryLabelColor
        difficultyLabel.frame = NSRect(x: 20, y: 30, width: 150, height: 20)
        headerView.addSubview(difficultyLabel)
        
        // Score
        scoreLabel = NSTextField(labelWithString: "Score: 0")
        scoreLabel.font = NSFont.systemFont(ofSize: 16, weight: .semibold)
        scoreLabel.textColor = NSColor.labelColor
        scoreLabel.frame = NSRect(x: bounds.width - 200, y: 50, width: 100, height: 20)
        headerView.addSubview(scoreLabel)
        
        // Timer
        timerLabel = NSTextField(labelWithString: "Time: 00:00")
        timerLabel.font = NSFont.systemFont(ofSize: 16, weight: .semibold)
        timerLabel.textColor = NSColor.labelColor
        timerLabel.frame = NSRect(x: bounds.width - 200, y: 30, width: 100, height: 20)
        headerView.addSubview(timerLabel)
        
        // End Session Button
        endSessionButton = NSButton(title: "End Session", target: self, action: #selector(endSessionButtonClicked))
        endSessionButton.bezelStyle = .rounded
        endSessionButton.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        endSessionButton.frame = NSRect(x: bounds.width - 120, y: 10, width: 100, height: 30)
        headerView.addSubview(endSessionButton)
    }
    
    private func setupExerciseView() {
        exerciseView = NSView(frame: NSRect(x: 20, y: 120, width: bounds.width - 40, height: 200))
        exerciseView.wantsLayer = true
        exerciseView.layer?.backgroundColor = NSColor.white.cgColor
        exerciseView.layer?.cornerRadius = 12
        exerciseView.layer?.borderWidth = 1
        exerciseView.layer?.borderColor = NSColor.systemGray.withAlphaComponent(0.3).cgColor
        addSubview(exerciseView)
        
        // Target Sign
        targetSignLabel = NSTextField(labelWithString: "Target Sign: A")
        targetSignLabel.font = NSFont.systemFont(ofSize: 32, weight: .bold)
        targetSignLabel.textColor = NSColor.systemBlue
        targetSignLabel.alignment = .center
        targetSignLabel.frame = NSRect(x: 20, y: 140, width: exerciseView.bounds.width - 40, height: 40)
        exerciseView.addSubview(targetSignLabel)
        
        // Instructions
        instructionsLabel = NSTextField(labelWithString: "Sign the letter 'A' clearly")
        instructionsLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        instructionsLabel.textColor = NSColor.labelColor
        instructionsLabel.alignment = .center
        instructionsLabel.frame = NSRect(x: 20, y: 100, width: exerciseView.bounds.width - 40, height: 20)
        exerciseView.addSubview(instructionsLabel)
        
        // Hints
        hintsLabel = NSTextField(labelWithString: "Hint: Make sure your hand is clearly visible")
        hintsLabel.font = NSFont.systemFont(ofSize: 14)
        hintsLabel.textColor = NSColor.secondaryLabelColor
        hintsLabel.alignment = .center
        hintsLabel.frame = NSRect(x: 20, y: 70, width: exerciseView.bounds.width - 40, height: 20)
        exerciseView.addSubview(hintsLabel)
        
        // Recognition Status
        recognitionStatusLabel = NSTextField(labelWithString: "Ready to start exercise")
        recognitionStatusLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        recognitionStatusLabel.textColor = NSColor.systemOrange
        recognitionStatusLabel.alignment = .center
        recognitionStatusLabel.frame = NSRect(x: 20, y: 40, width: exerciseView.bounds.width - 40, height: 20)
        exerciseView.addSubview(recognitionStatusLabel)
        
        // Start Exercise Button
        startExerciseButton = NSButton(title: "Start Exercise", target: self, action: #selector(startExerciseButtonClicked))
        startExerciseButton.bezelStyle = .rounded
        startExerciseButton.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        startExerciseButton.frame = NSRect(x: 50, y: 10, width: 120, height: 30)
        exerciseView.addSubview(startExerciseButton)
        
        // Skip Exercise Button
        skipExerciseButton = NSButton(title: "Skip", target: self, action: #selector(skipExerciseButtonClicked))
        skipExerciseButton.bezelStyle = .rounded
        skipExerciseButton.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        skipExerciseButton.frame = NSRect(x: exerciseView.bounds.width - 80, y: 10, width: 60, height: 30)
        exerciseView.addSubview(skipExerciseButton)
    }
    
    private func setupProgressView() {
        progressView = NSView(frame: NSRect(x: 20, y: 340, width: bounds.width - 40, height: 80))
        progressView.wantsLayer = true
        progressView.layer?.backgroundColor = NSColor.systemGray.withAlphaComponent(0.1).cgColor
        progressView.layer?.cornerRadius = 8
        addSubview(progressView)
        
        // Progress Bar
        progressBar = NSProgressIndicator()
        progressBar.style = .bar
        progressBar.isIndeterminate = false
        progressBar.minValue = 0
        progressBar.maxValue = 100
        progressBar.doubleValue = 0
        progressBar.frame = NSRect(x: 20, y: 50, width: progressView.bounds.width - 40, height: 20)
        progressView.addSubview(progressBar)
        
        // Accuracy Label
        accuracyLabel = NSTextField(labelWithString: "Accuracy: 0%")
        accuracyLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        accuracyLabel.textColor = NSColor.labelColor
        accuracyLabel.frame = NSRect(x: 20, y: 25, width: 120, height: 20)
        progressView.addSubview(accuracyLabel)
        
        // Exercises Completed Label
        exercisesCompletedLabel = NSTextField(labelWithString: "Completed: 0/10")
        exercisesCompletedLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        exercisesCompletedLabel.textColor = NSColor.labelColor
        exercisesCompletedLabel.frame = NSRect(x: 150, y: 25, width: 120, height: 20)
        progressView.addSubview(exercisesCompletedLabel)
    }
    
    private func setupFeedbackView() {
        feedbackView = NSView(frame: NSRect(x: 20, y: 440, width: bounds.width - 40, height: 120))
        feedbackView.wantsLayer = true
        feedbackView.layer?.backgroundColor = NSColor.systemYellow.withAlphaComponent(0.1).cgColor
        feedbackView.layer?.cornerRadius = 8
        feedbackView.layer?.borderWidth = 1
        feedbackView.layer?.borderColor = NSColor.systemYellow.withAlphaComponent(0.3).cgColor
        addSubview(feedbackView)
        
        // Feedback Label
        feedbackLabel = NSTextField(labelWithString: "Was the recognition correct?")
        feedbackLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        feedbackLabel.textColor = NSColor.labelColor
        feedbackLabel.alignment = .center
        feedbackLabel.frame = NSRect(x: 20, y: 90, width: feedbackView.bounds.width - 40, height: 20)
        feedbackView.addSubview(feedbackLabel)
        
        // Correct Button
        correctButton = NSButton(title: "✓ Correct", target: self, action: #selector(correctButtonClicked))
        correctButton.bezelStyle = .rounded
        correctButton.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        correctButton.frame = NSRect(x: 50, y: 50, width: 80, height: 30)
        feedbackView.addSubview(correctButton)
        
        // Incorrect Button
        incorrectButton = NSButton(title: "✗ Incorrect", target: self, action: #selector(incorrectButtonClicked))
        incorrectButton.bezelStyle = .rounded
        incorrectButton.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        incorrectButton.frame = NSRect(x: 140, y: 50, width: 80, height: 30)
        feedbackView.addSubview(incorrectButton)
        
        // Feedback Text Field
        feedbackTextField = NSTextField()
        feedbackTextField.placeholderString = "Optional comment..."
        feedbackTextField.font = NSFont.systemFont(ofSize: 12)
        feedbackTextField.frame = NSRect(x: 20, y: 20, width: feedbackView.bounds.width - 120, height: 25)
        feedbackView.addSubview(feedbackTextField)
        
        // Submit Feedback Button
        submitFeedbackButton = NSButton(title: "Submit", target: self, action: #selector(submitFeedbackButtonClicked))
        submitFeedbackButton.bezelStyle = .rounded
        submitFeedbackButton.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        submitFeedbackButton.frame = NSRect(x: feedbackView.bounds.width - 80, y: 20, width: 60, height: 25)
        feedbackView.addSubview(submitFeedbackButton)
    }
    
    private func setupCallbacks() {
        trainingMode.onExerciseStarted = { [weak self] exercise in
            DispatchQueue.main.async {
                self?.handleExerciseStarted(exercise)
            }
        }
        
        trainingMode.onExerciseCompleted = { [weak self] result in
            DispatchQueue.main.async {
                self?.handleExerciseCompleted(result)
            }
        }
        
        trainingMode.onProgressUpdated = { [weak self] progress in
            DispatchQueue.main.async {
                self?.updateProgressDisplay(progress)
            }
        }
        
        trainingMode.onTrainingSessionEnded = { [weak self] session in
            DispatchQueue.main.async {
                self?.handleSessionEnded(session)
            }
        }
    }
    
    // MARK: - Public Methods
    
    /// Start a new training session
    func startSession(language: String, difficulty: TrainingMode.TrainingDifficulty) {
        _ = trainingMode.startTrainingSession(language: language, difficulty: difficulty)
        updateHeaderDisplay(difficulty: difficulty)
        getNextExercise()
    }
    
    /// Get the next exercise
    func getNextExercise() {
        if let exercise = trainingMode.getNextExercise() {
            updateExerciseDisplay(exercise)
        } else {
            // No more exercises available
            endSession()
        }
    }
    
    /// Update the display with recognition results
    func updateRecognitionResult(recognizedSign: String, confidence: Float) {
        guard let exercise = currentExercise else { return }
        
        let isCorrect = recognizedSign.lowercased() == exercise.targetSign.lowercased()
        let statusColor = isCorrect ? NSColor.systemGreen : NSColor.systemRed
        let statusText = isCorrect ? "Correct!" : "Incorrect"
        
        recognitionStatusLabel.textColor = statusColor
        recognitionStatusLabel.stringValue = "\(statusText) - Recognized: \(recognizedSign) (\(Int(confidence * 100))%)"
        
        // Submit result after a short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.submitRecognitionResult(recognizedSign: recognizedSign, confidence: confidence)
        }
    }
    
    // MARK: - Private Methods
    
    private func handleExerciseStarted(_ exercise: TrainingMode.TrainingExercise) {
        currentExercise = exercise
        updateExerciseDisplay(exercise)
        startExerciseTimer()
    }
    
    private func handleExerciseCompleted(_ result: TrainingMode.TrainingResult) {
        stopExerciseTimer()
        
        // Show feedback view
        feedbackView.isHidden = false
        
        // Update recognition status
        let statusColor = result.isCorrect ? NSColor.systemGreen : NSColor.systemRed
        recognitionStatusLabel.textColor = statusColor
        recognitionStatusLabel.stringValue = result.feedback ?? "Exercise completed"
        
        // Update score
        updateScoreDisplay()
        
        onExerciseCompleted?(result)
    }
    
    private func handleSessionEnded(_ session: TrainingMode.TrainingSession) {
        stopExerciseTimer()
        
        // Show session summary
        let alert = NSAlert()
        alert.messageText = "Training Session Complete"
        alert.informativeText = """
        Session Results:
        • Total Score: \(session.totalScore)
        • Accuracy: \(Int(session.accuracy * 100))%
        • Exercises Completed: \(session.completedExercises.count)
        """
        alert.alertStyle = .informational
        alert.addButton(withTitle: "OK")
        alert.runModal()
        
        onSessionEnded?(session)
    }
    
    private func updateHeaderDisplay(difficulty: TrainingMode.TrainingDifficulty) {
        difficultyLabel.stringValue = "Difficulty: \(difficulty.rawValue)"
        scoreLabel.stringValue = "Score: 0"
        timerLabel.stringValue = "Time: 00:00"
    }
    
    private func updateExerciseDisplay(_ exercise: TrainingMode.TrainingExercise) {
        targetSignLabel.stringValue = "Target Sign: \(exercise.targetSign)"
        instructionsLabel.stringValue = exercise.instructions
        hintsLabel.stringValue = "Hint: \(exercise.hints.first ?? "None")"
        recognitionStatusLabel.stringValue = "Ready to start exercise"
        recognitionStatusLabel.textColor = NSColor.systemOrange
        
        // Reset buttons
        startExerciseButton.isEnabled = true
        skipExerciseButton.isEnabled = true
    }
    
    private func updateProgressDisplay(_ progress: TrainingMode.UserProgress) {
        let accuracyPercentage = Int(progress.averageAccuracy * 100)
        accuracyLabel.stringValue = "Accuracy: \(accuracyPercentage)%"
        
        let completed = progress.totalExercises
        exercisesCompletedLabel.stringValue = "Completed: \(completed)"
        
        // Update progress bar (assuming 10 exercises per session)
        let progressPercentage = min(100, (completed * 10))
        progressBar.doubleValue = Double(progressPercentage)
    }
    
    private func updateScoreDisplay() {
        guard let session = trainingMode.activeSession else { return }
        scoreLabel.stringValue = "Score: \(session.totalScore)"
    }
    
    private func startExerciseTimer() {
        guard let exercise = currentExercise else { return }
        
        timeRemaining = exercise.timeLimit
        exerciseStartTime = Date()
        
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateTimer()
        }
        
        updateTimer()
    }
    
    private func stopExerciseTimer() {
        timer?.invalidate()
        timer = nil
    }
    
    private func updateTimer() {
        timeRemaining -= 1
        
        let minutes = Int(timeRemaining) / 60
        let seconds = Int(timeRemaining) % 60
        timerLabel.stringValue = String(format: "Time: %02d:%02d", minutes, seconds)
        
        if timeRemaining <= 0 {
            stopExerciseTimer()
            // Time's up - submit result as incorrect
            submitRecognitionResult(recognizedSign: "TIMEOUT", confidence: 0.0)
        }
    }
    
    private func submitRecognitionResult(recognizedSign: String, confidence: Float) {
        guard let _ = currentExercise,
              let startTime = exerciseStartTime else { return }
        
        let timeTaken = Date().timeIntervalSince(startTime)
        trainingMode.submitRecognitionResult(recognizedSign: recognizedSign, confidence: confidence, timeTaken: timeTaken)
    }
    
    private func endSession() {
        trainingMode.endTrainingSession()
    }
    
    // MARK: - Actions
    
    @objc private func endSessionButtonClicked() {
        let alert = NSAlert()
        alert.messageText = "End Training Session"
        alert.informativeText = "Are you sure you want to end this training session?"
        alert.alertStyle = .warning
        alert.addButton(withTitle: "End Session")
        alert.addButton(withTitle: "Cancel")
        
        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            endSession()
        }
    }
    
    @objc private func startExerciseButtonClicked() {
        startExerciseButton.isEnabled = false
        recognitionStatusLabel.stringValue = "Exercise active - Sign now!"
        recognitionStatusLabel.textColor = NSColor.systemGreen
    }
    
    @objc private func skipExerciseButtonClicked() {
        submitRecognitionResult(recognizedSign: "SKIPPED", confidence: 0.0)
    }
    
    @objc private func correctButtonClicked() {
        feedbackView.isHidden = true
        getNextExercise()
    }
    
    @objc private func incorrectButtonClicked() {
        // Show feedback text field for correction
        feedbackTextField.stringValue = ""
        feedbackTextField.becomeFirstResponder()
    }
    
    @objc private func submitFeedbackButtonClicked() {
        guard let _ = currentExercise else { return }
        
        let correctedSign = feedbackTextField.stringValue.isEmpty ? "UNKNOWN" : feedbackTextField.stringValue
        trainingMode.provideFeedback(
            originalRecognition: currentExercise?.targetSign ?? "UNKNOWN",
            correctedSign: correctedSign,
            userComment: feedbackTextField.stringValue.isEmpty ? nil : feedbackTextField.stringValue
        )
        
        feedbackView.isHidden = true
        getNextExercise()
    }
} 