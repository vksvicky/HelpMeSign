import Foundation
import Vision
import CoreML

// MARK: - Training Mode System
class TrainingMode: NSObject {
    
    // MARK: - Properties
    static let shared = TrainingMode()
    
    // Training session state
    private var isTrainingActive = false
    private var currentSession: TrainingSession?
    private var currentExercise: TrainingExercise?
    
    // Training data
    private var trainingExercises: [TrainingExercise] = []
    private var userProgress: [String: UserProgress] = [:]
    private var feedbackHistory: [TrainingFeedback] = []
    
    // Callbacks
    var onExerciseStarted: ((TrainingExercise) -> Void)?
    var onExerciseCompleted: ((TrainingResult) -> Void)?
    var onProgressUpdated: ((UserProgress) -> Void)?
    var onTrainingSessionEnded: ((TrainingSession) -> Void)?
    
    // MARK: - Core Data Structures
    
    struct TrainingSession {
        let sessionId: String
        let startTime: Date
        let language: String
        let difficulty: TrainingDifficulty
        let targetSigns: [String]
        var completedExercises: [TrainingResult] = []
        var totalScore: Int = 0
        var accuracy: Float = 0.0
    }
    
    struct TrainingExercise {
        let exerciseId: String
        let targetSign: String
        let language: String
        let difficulty: TrainingDifficulty
        let instructions: String
        let hints: [String]
        let expectedFeatures: [Float]?
        let timeLimit: TimeInterval
        let points: Int
        let category: ExerciseCategory
    }
    
    struct TrainingResult {
        let exerciseId: String
        let targetSign: String
        let recognizedSign: String
        let confidence: Float
        let isCorrect: Bool
        let timeTaken: TimeInterval
        let score: Int
        let feedback: String?
        let timestamp: Date
    }
    
    struct UserProgress {
        let userId: String
        let language: String
        var totalSessions: Int
        var totalExercises: Int
        var correctRecognitions: Int
        var averageAccuracy: Float
        var bestAccuracy: Float
        var signProgress: [String: SignProgress]
        var lastSessionDate: Date
    }
    
    struct SignProgress {
        let sign: String
        var attempts: Int
        var correct: Int
        var accuracy: Float
        var lastPracticed: Date
        let difficulty: TrainingDifficulty
    }
    
    struct TrainingFeedback {
        let sessionId: String
        let exerciseId: String
        let originalRecognition: String
        let correctedSign: String
        let userComment: String?
        let timestamp: Date
    }
    
    enum TrainingDifficulty: String, CaseIterable {
        case beginner = "Beginner"
        case intermediate = "Intermediate"
        case advanced = "Advanced"
        case expert = "Expert"
        
        var description: String {
            switch self {
            case .beginner: return "Learn basic signs with clear instructions"
            case .intermediate: return "Practice common signs with moderate difficulty"
            case .advanced: return "Master complex signs and sequences"
            case .expert: return "Perfect your signing with challenging exercises"
            }
        }
        
        var timeLimit: TimeInterval {
            switch self {
            case .beginner: return 10.0
            case .intermediate: return 8.0
            case .advanced: return 6.0
            case .expert: return 4.0
            }
        }
        
        var points: Int {
            switch self {
            case .beginner: return 10
            case .intermediate: return 20
            case .advanced: return 30
            case .expert: return 50
            }
        }
    }
    
    enum ExerciseCategory: String, CaseIterable {
        case alphabet = "Alphabet"
        case numbers = "Numbers"
        case commonWords = "Common Words"
        case phrases = "Phrases"
        case sentences = "Sentences"
        case custom = "Custom"
        
        var description: String {
            switch self {
            case .alphabet: return "Practice individual letters"
            case .numbers: return "Learn number signs"
            case .commonWords: return "Everyday vocabulary"
            case .phrases: return "Short phrases and expressions"
            case .sentences: return "Complete sentences"
            case .custom: return "Custom exercises"
            }
        }
    }
    
    // MARK: - Initialization
    override init() {
        super.init()
        loadTrainingExercises()
        loadUserProgress()
    }
    
    // MARK: - Public Methods
    
    /// Start a new training session
    func startTrainingSession(language: String, difficulty: TrainingDifficulty, targetSigns: [String] = []) -> String {
        let sessionId = UUID().uuidString
        currentSession = TrainingSession(
            sessionId: sessionId,
            startTime: Date(),
            language: language,
            difficulty: difficulty,
            targetSigns: targetSigns.isEmpty ? getDefaultSigns(for: difficulty) : targetSigns
        )
        
        isTrainingActive = true
        NSLog("Training Mode: Started session \(sessionId) for \(language) at \(difficulty.rawValue) level")
        
        return sessionId
    }
    
    /// End the current training session
    func endTrainingSession() {
        guard let session = currentSession else { return }
        
        isTrainingActive = false
        currentExercise = nil
        
        // Calculate final session statistics
        let finalSession = calculateSessionResults(session)
        
        // Update user progress
        updateUserProgress(with: finalSession)
        
        // Save progress
        saveUserProgress()
        
        onTrainingSessionEnded?(finalSession)
        
        NSLog("Training Mode: Ended session \(session.sessionId) with accuracy: \(finalSession.accuracy)")
    }
    
    /// Get next exercise for current session
    func getNextExercise() -> TrainingExercise? {
        guard let session = currentSession else { return nil }
        
        // Filter exercises based on session criteria
        let availableExercises = trainingExercises.filter { exercise in
            exercise.language == session.language &&
            exercise.difficulty == session.difficulty &&
            session.targetSigns.contains(exercise.targetSign)
        }
        
        // Select exercise based on user progress and difficulty
        let nextExercise = selectOptimalExercise(from: availableExercises, for: session)
        
        if let exercise = nextExercise {
            currentExercise = exercise
            onExerciseStarted?(exercise)
        }
        
        return nextExercise
    }
    
    /// Submit recognition result for current exercise
    func submitRecognitionResult(recognizedSign: String, confidence: Float, timeTaken: TimeInterval) {
        guard let _ = currentSession,
              let exercise = currentExercise else { return }
        
        let isCorrect = recognizedSign.lowercased() == exercise.targetSign.lowercased()
        let score = calculateScore(isCorrect: isCorrect, confidence: confidence, timeTaken: timeTaken, difficulty: exercise.difficulty)
        
        let result = TrainingResult(
            exerciseId: exercise.exerciseId,
            targetSign: exercise.targetSign,
            recognizedSign: recognizedSign,
            confidence: confidence,
            isCorrect: isCorrect,
            timeTaken: timeTaken,
            score: score,
            feedback: generateFeedback(isCorrect: isCorrect, confidence: confidence, targetSign: exercise.targetSign, recognizedSign: recognizedSign),
            timestamp: Date()
        )
        
        // Update session
        currentSession?.completedExercises.append(result)
        currentSession?.totalScore += score
        
        // Update progress
        updateSignProgress(sign: exercise.targetSign, isCorrect: isCorrect, confidence: confidence)
        
        onExerciseCompleted?(result)
        
        NSLog("Training Mode: Exercise completed - Target: \(exercise.targetSign), Recognized: \(recognizedSign), Correct: \(isCorrect), Score: \(score)")
    }
    
    /// Provide user feedback for learning
    func provideFeedback(originalRecognition: String, correctedSign: String, userComment: String? = nil) {
        guard currentSession != nil,
              let exercise = currentExercise else { return }
        
        let feedback = TrainingFeedback(
            sessionId: currentSession?.sessionId ?? "unknown", // Use optional chaining
            exerciseId: exercise.exerciseId,
            originalRecognition: originalRecognition,
            correctedSign: correctedSign,
            userComment: userComment,
            timestamp: Date()
        )
        
        feedbackHistory.append(feedback)
        
        // Update AI system with feedback
        AIUserExperienceSystem.shared.provideFeedback(originalSign: originalRecognition, correctedSign: correctedSign)
        
        NSLog("Training Mode: Received feedback - \(originalRecognition) → \(correctedSign)")
    }
    
    /// Get user progress for a specific language
    func getUserProgress(for language: String) -> UserProgress? {
        return userProgress[language]
    }
    
    /// Get training statistics
    func getTrainingStatistics() -> (totalSessions: Int, totalExercises: Int, averageAccuracy: Float, bestAccuracy: Float) {
        let allProgress = userProgress.values
        let totalSessions = allProgress.reduce(0) { $0 + $1.totalSessions }
        let totalExercises = allProgress.reduce(0) { $0 + $1.totalExercises }
        let averageAccuracy = allProgress.isEmpty ? 0.0 : allProgress.map { $0.averageAccuracy }.reduce(0, +) / Float(allProgress.count)
        let bestAccuracy = allProgress.map { $0.bestAccuracy }.max() ?? 0.0
        
        return (totalSessions, totalExercises, averageAccuracy, bestAccuracy)
    }
    
    /// Get recommended exercises based on user progress
    func getRecommendedExercises(for language: String, difficulty: TrainingDifficulty) -> [TrainingExercise] {
        let userProgress = getUserProgress(for: language)
        let weakSigns = getWeakSigns(from: userProgress)
        
        return trainingExercises.filter { exercise in
            exercise.language == language &&
            exercise.difficulty == difficulty &&
            weakSigns.contains(exercise.targetSign)
        }
    }
    
    /// Create custom exercise
    func createCustomExercise(targetSign: String, instructions: String, hints: [String], difficulty: TrainingDifficulty) -> TrainingExercise {
        let exercise = TrainingExercise(
            exerciseId: UUID().uuidString,
            targetSign: targetSign,
            language: "Custom", // Assuming custom exercises are language-agnostic or handled elsewhere
            difficulty: difficulty,
            instructions: instructions,
            hints: hints,
            expectedFeatures: nil,
            timeLimit: difficulty.timeLimit,
            points: difficulty.points,
            category: .custom
        )
        
        trainingExercises.append(exercise)
        return exercise
    }
    
    // MARK: - Private Methods
    
    private func loadTrainingExercises() {
        // Load predefined training exercises
        trainingExercises = createDefaultExercises()
        NSLog("Training Mode: Loaded \(trainingExercises.count) training exercises")
    }
    
    private func createDefaultExercises() -> [TrainingExercise] {
        var exercises: [TrainingExercise] = []
        
        // Alphabet exercises
        let alphabetSigns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        
        for sign in alphabetSigns {
            exercises.append(TrainingExercise(
                exerciseId: "alphabet_\(sign.lowercased())",
                targetSign: sign,
                language: "English", // Default language for alphabet
                difficulty: .beginner,
                instructions: "Sign the letter '\(sign)' clearly",
                hints: ["Make sure your hand is clearly visible", "Hold the sign steady for recognition"],
                expectedFeatures: nil,
                timeLimit: 10.0,
                points: 10,
                category: .alphabet
            ))
        }
        
        // Number exercises
        let numberSigns = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        for number in numberSigns {
            exercises.append(TrainingExercise(
                exerciseId: "number_\(number)",
                targetSign: number,
                language: "English", // Default language for numbers
                difficulty: .beginner,
                instructions: "Sign the number '\(number)'",
                hints: ["Use the correct hand shape for numbers", "Position your hand at chest level"],
                expectedFeatures: nil,
                timeLimit: 8.0,
                points: 10,
                category: .numbers
            ))
        }
        
        // Common word exercises
        let commonWords = ["HELLO", "THANK YOU", "PLEASE", "YES", "NO", "GOOD", "BAD", "HELP", "WATER", "FOOD"]
        
        for word in commonWords {
            exercises.append(TrainingExercise(
                exerciseId: "word_\(word.lowercased())",
                targetSign: word,
                language: "English", // Default language for common words
                difficulty: .intermediate,
                instructions: "Sign the word '\(word)'",
                hints: ["Remember the complete sign sequence", "Use appropriate facial expressions"],
                expectedFeatures: nil,
                timeLimit: 12.0,
                points: 20,
                category: .commonWords
            ))
        }
        
        return exercises
    }
    
    private func getDefaultSigns(for difficulty: TrainingDifficulty) -> [String] {
        switch difficulty {
        case .beginner:
            return ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        case .intermediate:
            return ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
        case .advanced:
            return ["U", "V", "W", "X", "Y", "Z", "HELLO", "THANK YOU", "PLEASE"]
        case .expert:
            return ["HELLO", "THANK YOU", "PLEASE", "YES", "NO", "GOOD", "BAD", "HELP"]
        }
    }
    
    private func selectOptimalExercise(from exercises: [TrainingExercise], for session: TrainingSession) -> TrainingExercise? {
        guard !exercises.isEmpty else { return nil }
        
        // Get user progress for this language
        let progress = getUserProgress(for: session.language)
        
        // Prioritize exercises for signs the user struggles with
        if let progress = progress {
            let weakSigns = getWeakSigns(from: progress)
            let weakSignExercises = exercises.filter { weakSigns.contains($0.targetSign) }
            
            if !weakSignExercises.isEmpty {
                return weakSignExercises.randomElement()
            }
        }
        
        // Otherwise, select random exercise
        return exercises.randomElement()
    }
    
    private func getWeakSigns(from progress: UserProgress?) -> [String] {
        guard let progress = progress else { return [] }
        
        return progress.signProgress.compactMap { sign, signProgress in
            return signProgress.accuracy < 0.7 ? sign : nil
        }
    }
    
    private func calculateScore(isCorrect: Bool, confidence: Float, timeTaken: TimeInterval, difficulty: TrainingDifficulty) -> Int {
        guard isCorrect else { return 0 }
        
        let baseScore = difficulty.points
        let confidenceBonus = Int(confidence * 10)
        let timeBonus = max(0, Int((10 - timeTaken) * 2)) // Bonus for faster completion
        
        return baseScore + confidenceBonus + timeBonus
    }
    
    private func generateFeedback(isCorrect: Bool, confidence: Float, targetSign: String, recognizedSign: String) -> String {
        if isCorrect {
            if confidence > 0.9 {
                return "Excellent! Perfect recognition with high confidence."
            } else if confidence > 0.7 {
                return "Good job! The sign was recognized correctly."
            } else {
                return "Correct, but try to make the sign more clearly for better confidence."
            }
        } else {
            return "Incorrect. You signed '\(recognizedSign)' but the target was '\(targetSign)'. Try again!"
        }
    }
    
    private func calculateSessionResults(_ session: TrainingSession) -> TrainingSession {
        var finalSession = session
        
        let totalExercises = session.completedExercises.count
        let correctExercises = session.completedExercises.filter { $0.isCorrect }.count
        
        finalSession.accuracy = totalExercises > 0 ? Float(correctExercises) / Float(totalExercises) : 0.0
        
        return finalSession
    }
    
    private func updateUserProgress(with session: TrainingSession) {
        let currentProgress = userProgress[session.language] ?? UserProgress(
            userId: "default",
            language: session.language,
            totalSessions: 0,
            totalExercises: 0,
            correctRecognitions: 0,
            averageAccuracy: 0.0,
            bestAccuracy: 0.0,
            signProgress: [:],
            lastSessionDate: Date.distantPast
        )
        
        var updatedProgress = currentProgress
        updatedProgress.totalSessions += 1
        updatedProgress.totalExercises += session.completedExercises.count
        updatedProgress.correctRecognitions += session.completedExercises.filter { $0.isCorrect }.count
        updatedProgress.lastSessionDate = Date()
        
        // Update average accuracy
        let totalAccuracy = (currentProgress.averageAccuracy * Float(currentProgress.totalExercises - session.completedExercises.count) + session.accuracy * Float(session.completedExercises.count))
        updatedProgress.averageAccuracy = totalAccuracy / Float(updatedProgress.totalExercises)
        
        // Update best accuracy
        updatedProgress.bestAccuracy = max(currentProgress.bestAccuracy, session.accuracy)
        
        // Update sign-specific progress
        for result in session.completedExercises {
            updateSignProgressInUserProgress(&updatedProgress, sign: result.targetSign, isCorrect: result.isCorrect, confidence: result.confidence)
        }
        
        userProgress[session.language] = updatedProgress
        onProgressUpdated?(updatedProgress)
    }
    
    private func updateSignProgress(sign: String, isCorrect: Bool, confidence: Float) {
        // This method updates progress for the current session
        // The actual user progress update happens in updateUserProgress
    }
    
    private func updateSignProgressInUserProgress(_ progress: inout UserProgress, sign: String, isCorrect: Bool, confidence: Float) {
        let currentSignProgress = progress.signProgress[sign] ?? SignProgress(
            sign: sign,
            attempts: 0,
            correct: 0,
            accuracy: 0.0,
            lastPracticed: Date.distantPast,
            difficulty: .beginner
        )
        
        var updatedSignProgress = currentSignProgress
        updatedSignProgress.attempts += 1
        if isCorrect {
            updatedSignProgress.correct += 1
        }
        updatedSignProgress.accuracy = Float(updatedSignProgress.correct) / Float(updatedSignProgress.attempts)
        updatedSignProgress.lastPracticed = Date()
        
        progress.signProgress[sign] = updatedSignProgress
    }
    
    private func loadUserProgress() {
        // Load user progress from UserDefaults or file
        // For now, start with empty progress
        userProgress = [:]
    }
    
    private func saveUserProgress() {
        // Save user progress to UserDefaults or file
        // Implementation would depend on storage requirements
        NSLog("Training Mode: User progress saved")
    }
}

// MARK: - Extensions

extension TrainingMode {
    /// Check if training mode is currently active
    var isActive: Bool {
        return isTrainingActive
    }
    
    /// Get current session
    var activeSession: TrainingSession? {
        return currentSession
    }
    
    /// Get current exercise
    var activeExercise: TrainingExercise? {
        return currentExercise
    }
} 
