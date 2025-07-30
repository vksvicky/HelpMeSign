import Foundation
import Vision
import CoreML
import Accelerate

// MARK: - Adaptive Sign Recognition System
class AdaptiveSignRecognition {
    
    // MARK: - Properties
    static let shared = AdaptiveSignRecognition()
    
    // Dynamic learning storage
    private var learnedPatterns: [String: [HandPattern]] = [:]
    private var adaptiveThresholds: [String: Float] = [:]
    private var confidenceHistory: [String: [Float]] = [:]
    
    // Real-time adaptation
    private var currentSession: RecognitionSession?
    private var feedbackQueue: [UserFeedback] = []
    
    // Performance tracking
    private var recognitionStats: RecognitionStatistics = RecognitionStatistics()
    
    // MARK: - Core Data Structures
    
    struct HandPattern {
        let features: [Float]
        let confidence: Float
        let timestamp: Date
        let userCorrection: String?
        let culturalContext: String?
        let handPreference: HandPreference
    }
    
    struct RecognitionSession {
        let sessionId: String
        let startTime: Date
        let language: String
        let userProfile: UserProfile
        var patterns: [HandPattern] = []
        var corrections: [String: String] = [:]
    }
    
    struct UserProfile {
        let userId: String
        let preferredLanguage: String
        let handPreference: HandPreference
        let culturalBackground: String?
        let learningStyle: LearningStyle
        let adaptationRate: Float
    }
    
    struct UserFeedback {
        let originalRecognition: String
        let correctedSign: String
        let confidence: Float
        let timestamp: Date
        let context: String?
    }
    
    struct RecognitionStatistics {
        var totalRecognitions: Int = 0
        var correctRecognitions: Int = 0
        var averageConfidence: Float = 0.0
        var adaptationRate: Float = 0.0
        var culturalAccuracy: [String: Float] = [:]
    }
    
    enum HandPreference: String, CaseIterable {
        case left = "left"
        case right = "right"
        case both = "both"
    }
    
    enum LearningStyle {
        case conservative, adaptive, aggressive
    }
    
    // MARK: - Public Methods
    
    /// Initialize a new recognition session
    func startSession(language: String, userProfile: UserProfile) -> String {
        let sessionId = UUID().uuidString
        currentSession = RecognitionSession(
            sessionId: sessionId,
            startTime: Date(),
            language: language,
            userProfile: userProfile
        )
        
        print("Adaptive Recognition: Started session \(sessionId) for \(language)")
        return sessionId
    }
    
    /// Process hand features and recognize sign adaptively
    func recognizeSignAdaptively(_ features: [Float], context: RecognitionContext) async -> AdaptiveRecognitionResult {
        guard currentSession != nil else {
            return AdaptiveRecognitionResult(sign: "?", confidence: 0.0, isAdaptive: false, suggestions: [])
        }
        
        // Extract hand characteristics for potential future use
        let _ = extractHandCharacteristics(features)
        
        // Find similar patterns in learned data
        let similarPatterns = findSimilarPatterns(features, context: context)
        
        // Apply cultural and contextual adjustments
        let adjustedFeatures = applyCulturalAdjustments(features, context: context)
        
        // Perform adaptive recognition
        let recognitionResult = await performAdaptiveRecognition(
            adjustedFeatures,
            similarPatterns: similarPatterns,
            context: context
        )
        
        // Update learning patterns
        updateLearningPatterns(features, result: recognitionResult, context: context)
        
        // Update statistics
        updateRecognitionStatistics(recognitionResult)
        
        return recognitionResult
    }
    
    /// Provide user feedback for learning
    func provideFeedback(originalSign: String, correctedSign: String, confidence: Float, context: String? = nil) {
        let feedback = UserFeedback(
            originalRecognition: originalSign,
            correctedSign: correctedSign,
            confidence: confidence,
            timestamp: Date(),
            context: context
        )
        
        feedbackQueue.append(feedback)
        
        // Apply immediate learning
        applyFeedbackLearning(feedback)
        
        print("Adaptive Recognition: Received feedback - \(originalSign) → \(correctedSign)")
    }
    
    /// Get recognition suggestions based on current hand position
    func getSuggestions(_ features: [Float], context: RecognitionContext) -> [String] {
        let similarPatterns = findSimilarPatterns(features, context: context)
        
        return similarPatterns
            .prefix(5)
            .map { $0.sign }
            .filter { $0 != "?" }
    }
    
    /// Export learned patterns for sharing/collaboration
    func exportLearnedPatterns() -> Data? {
        // Convert internal types to Codable types
        var exportPatterns: [String: [HandPatternData]] = [:]
        for (sign, patterns) in learnedPatterns {
            exportPatterns[sign] = patterns.map { pattern in
                HandPatternData(
                    features: pattern.features,
                    confidence: pattern.confidence,
                    timestamp: pattern.timestamp,
                    userCorrection: pattern.userCorrection,
                    culturalContext: pattern.culturalContext,
                    handPreference: String(describing: pattern.handPreference)
                )
            }
        }
        
        let exportStats = RecognitionStatisticsData(
            totalRecognitions: recognitionStats.totalRecognitions,
            correctRecognitions: recognitionStats.correctRecognitions,
            averageConfidence: recognitionStats.averageConfidence,
            adaptationRate: recognitionStats.adaptationRate,
            culturalAccuracy: recognitionStats.culturalAccuracy
        )
        
        let exportData = LearnedPatternsExport(
            patterns: exportPatterns,
            statistics: exportStats,
            timestamp: Date()
        )
        
        return try? JSONEncoder().encode(exportData)
    }
    
    /// Import patterns from other users/systems
    func importPatterns(_ data: Data) throws {
        let importData = try JSONDecoder().decode(LearnedPatternsExport.self, from: data)
        
        // Convert Codable types back to internal types
        var internalPatterns: [String: [HandPattern]] = [:]
        for (sign, patterns) in importData.patterns {
            internalPatterns[sign] = patterns.map { patternData in
                HandPattern(
                    features: patternData.features,
                    confidence: patternData.confidence,
                    timestamp: patternData.timestamp,
                    userCorrection: patternData.userCorrection,
                    culturalContext: patternData.culturalContext,
                    handPreference: HandPreference(rawValue: patternData.handPreference) ?? .right
                )
            }
        }
        
        // Merge patterns intelligently
        mergeImportedPatterns(internalPatterns)
        
        print("Adaptive Recognition: Imported \(importData.patterns.count) pattern sets")
    }
    
    // MARK: - Private Methods
    
    private func extractHandCharacteristics(_ features: [Float]) -> HandCharacteristics {
        guard features.count >= 21 else {
            return HandCharacteristics(
                fingerExtensions: Array(repeating: 0.0, count: 5),
                handShape: HandShape(width: 0.0, height: 0.0, aspectRatio: 0.0, compactness: 0.0),
                fingerCurvatures: Array(repeating: 0.0, count: 5),
                handOrientation: HandOrientation(rotation: 0.0, tilt: 0.0, roll: 0.0),
                confidence: 0.0
            )
        }
        
        // Extract key hand characteristics
        let fingerExtensions = extractFingerExtensions(features)
        let handShape = extractHandShape(features)
        let fingerCurvatures = extractFingerCurvatures(features)
        let handOrientation = extractHandOrientation(features)
        
        return HandCharacteristics(
            fingerExtensions: fingerExtensions,
            handShape: handShape,
            fingerCurvatures: fingerCurvatures,
            handOrientation: handOrientation,
            confidence: calculateFeatureConfidence(features)
        )
    }
    
    private func findSimilarPatterns(_ features: [Float], context: RecognitionContext) -> [PatternMatch] {
        var matches: [PatternMatch] = []
        
        for (sign, patterns) in learnedPatterns {
            for pattern in patterns {
                let similarity = calculateSimilarity(features, pattern.features)
                let contextualSimilarity = applyContextualWeighting(similarity, context: context)
                
                if contextualSimilarity > 0.3 { // Adaptive threshold
                    matches.append(PatternMatch(
                        sign: sign,
                        similarity: contextualSimilarity,
                        pattern: pattern
                    ))
                }
            }
        }
        
        return matches.sorted { $0.similarity > $1.similarity }
    }
    
    private func applyCulturalAdjustments(_ features: [Float], context: RecognitionContext) -> [Float] {
        var adjustedFeatures = features
        
        // Apply cultural-specific adjustments
        if let culturalContext = context.culturalContext {
            switch culturalContext {
            case "ASL":
                // ASL-specific adjustments
                adjustedFeatures = applyASLAdjustments(features)
            case "BSL":
                // BSL-specific adjustments
                adjustedFeatures = applyBSLAdjustments(features)
            case "JSL":
                // JSL-specific adjustments
                adjustedFeatures = applyJSLAdjustments(features)
            default:
                // Generic adjustments
                adjustedFeatures = applyGenericAdjustments(features)
            }
        }
        
        return adjustedFeatures
    }
    
    private func performAdaptiveRecognition(
        _ features: [Float],
        similarPatterns: [PatternMatch],
        context: RecognitionContext
    ) async -> AdaptiveRecognitionResult {
        
        // If we have similar patterns, use them for recognition
        if !similarPatterns.isEmpty {
            let bestMatch = similarPatterns[0]
            
            // Apply adaptive confidence calculation
            let adaptiveConfidence = calculateAdaptiveConfidence(
                bestMatch.similarity,
                context: context,
                patternHistory: getPatternHistory(bestMatch.sign)
            )
            
            // Generate suggestions based on similar patterns
            let suggestions = similarPatterns
                .prefix(3)
                .map { $0.sign }
                .filter { $0 != bestMatch.sign }
            
            return AdaptiveRecognitionResult(
                sign: bestMatch.sign,
                confidence: adaptiveConfidence,
                isAdaptive: true,
                suggestions: suggestions
            )
        }
        
        // No similar patterns found - use feature-based recognition
        let featureBasedResult = performFeatureBasedRecognition(features, context: context)
        
        return AdaptiveRecognitionResult(
            sign: featureBasedResult.sign,
            confidence: featureBasedResult.confidence,
            isAdaptive: false,
            suggestions: []
        )
    }
    
    private func performFeatureBasedRecognition(_ features: [Float], context: RecognitionContext) -> (sign: String, confidence: Float) {
        let characteristics = extractHandCharacteristics(features)
        
        // Use hand characteristics to determine sign
        let sign = determineSignFromCharacteristics(characteristics, context: context)
        let confidence = characteristics.confidence
        
        return (sign: sign, confidence: confidence)
    }
    
    private func determineSignFromCharacteristics(_ characteristics: HandCharacteristics, context: RecognitionContext) -> String {
        // Analyze finger extensions
        let fingerPattern = analyzeFingerPattern(characteristics.fingerExtensions)
        
        // Analyze hand shape
        let shapePattern = analyzeHandShape(characteristics.handShape)
        
        // Analyze finger curvatures
        let curvaturePattern = analyzeCurvaturePattern(characteristics.fingerCurvatures)
        
        // Combine patterns for final recognition
        let combinedPattern = combinePatterns(fingerPattern, shapePattern, curvaturePattern)
        
        // Apply cultural context
        let culturallyAdjustedSign = applyCulturalContext(combinedPattern, context: context)
        
        return culturallyAdjustedSign
    }
    
    private func updateLearningPatterns(_ features: [Float], result: AdaptiveRecognitionResult, context: RecognitionContext) {
        guard let session = currentSession else { return }
        
        let pattern = HandPattern(
            features: features,
            confidence: result.confidence,
            timestamp: Date(),
            userCorrection: nil,
            culturalContext: context.culturalContext,
            handPreference: session.userProfile.handPreference
        )
        
        // Store pattern for the recognized sign
        if learnedPatterns[result.sign] == nil {
            learnedPatterns[result.sign] = []
        }
        learnedPatterns[result.sign]?.append(pattern)
        
        // Update session patterns
        currentSession?.patterns.append(pattern)
    }
    
    private func applyFeedbackLearning(_ feedback: UserFeedback) {
        // Find patterns that were incorrectly recognized
        let incorrectPatterns = currentSession?.patterns.filter { pattern in
            // Find patterns that led to the incorrect recognition
            return true // Simplified for now
        } ?? []
        
        // Update patterns with corrections
        for pattern in incorrectPatterns {
            let correctedPattern = HandPattern(
                features: pattern.features,
                confidence: feedback.confidence,
                timestamp: Date(),
                userCorrection: feedback.correctedSign,
                culturalContext: pattern.culturalContext,
                handPreference: pattern.handPreference
            )
            
            // Store corrected pattern
            if learnedPatterns[feedback.correctedSign] == nil {
                learnedPatterns[feedback.correctedSign] = []
            }
            learnedPatterns[feedback.correctedSign]?.append(correctedPattern)
        }
        
        // Update adaptive thresholds
        updateAdaptiveThresholds(feedback)
    }
    
    // MARK: - Helper Methods
    
    private func calculateSimilarity(_ features1: [Float], _ features2: [Float]) -> Float {
        guard features1.count == features2.count else { return 0.0 }
        
        // Use cosine similarity for feature comparison
        var dotProduct: Float = 0.0
        var norm1: Float = 0.0
        var norm2: Float = 0.0
        
        for i in 0..<features1.count {
            dotProduct += features1[i] * features2[i]
            norm1 += features1[i] * features1[i]
            norm2 += features2[i] * features2[i]
        }
        
        let similarity = dotProduct / (sqrt(norm1) * sqrt(norm2))
        return max(0.0, similarity) // Ensure non-negative
    }
    
    private func calculateAdaptiveConfidence(_ similarity: Float, context: RecognitionContext, patternHistory: [HandPattern]) -> Float {
        var confidence = similarity
        
        // Adjust based on pattern history
        if !patternHistory.isEmpty {
            let historicalConfidence = patternHistory.map { $0.confidence }.reduce(0, +) / Float(patternHistory.count)
            confidence = (confidence + historicalConfidence) / 2.0
        }
        
        // Adjust based on cultural context
        if let culturalContext = context.culturalContext {
            confidence *= getCulturalConfidenceMultiplier(culturalContext)
        }
        
        // Apply adaptive threshold
        let adaptiveThreshold = adaptiveThresholds[context.language] ?? 0.5
        confidence = max(0.0, confidence - adaptiveThreshold)
        
        return min(1.0, confidence)
    }
    
    private func getCulturalConfidenceMultiplier(_ culturalContext: String) -> Float {
        switch culturalContext {
        case "ASL": return 1.0
        case "BSL": return 0.95
        case "JSL": return 0.9
        default: return 0.85
        }
    }
    
    private func updateAdaptiveThresholds(_ feedback: UserFeedback) {
        // Adjust thresholds based on feedback
        let currentThreshold = adaptiveThresholds[feedback.originalRecognition] ?? 0.5
        
        if feedback.confidence < 0.3 {
            // Lower threshold for better sensitivity
            adaptiveThresholds[feedback.originalRecognition] = max(0.1, currentThreshold - 0.1)
        } else if feedback.confidence > 0.8 {
            // Raise threshold for better precision
            adaptiveThresholds[feedback.originalRecognition] = min(0.9, currentThreshold + 0.05)
        }
    }
    
    private func getPatternHistory(_ sign: String) -> [HandPattern] {
        return learnedPatterns[sign] ?? []
    }
    
    private func updateRecognitionStatistics(_ result: AdaptiveRecognitionResult) {
        recognitionStats.totalRecognitions += 1
        recognitionStats.averageConfidence = (recognitionStats.averageConfidence + result.confidence) / 2.0
        
        if result.confidence > 0.7 {
            recognitionStats.correctRecognitions += 1
        }
    }
    
    private func mergeImportedPatterns(_ importedPatterns: [String: [HandPattern]]) {
        for (sign, patterns) in importedPatterns {
            if learnedPatterns[sign] == nil {
                learnedPatterns[sign] = []
            }
            learnedPatterns[sign]?.append(contentsOf: patterns)
        }
    }
}

// MARK: - Supporting Types

struct RecognitionContext {
    let language: String
    let culturalContext: String?
    let userProfile: AdaptiveSignRecognition.UserProfile?
    let environment: RecognitionEnvironment
}

struct RecognitionEnvironment {
    let lighting: LightingCondition
    let background: BackgroundType
    let handPosition: HandPosition
    let movement: MovementType
}

enum LightingCondition {
    case bright, normal, dim, variable
}

enum BackgroundType {
    case plain, complex, moving, variable
}

enum HandPosition {
    case center, left, right, high, low
}

enum MovementType {
    case stationary, slow, fast, variable
}

struct HandCharacteristics {
    let fingerExtensions: [Float]
    let handShape: HandShape
    let fingerCurvatures: [Float]
    let handOrientation: HandOrientation
    let confidence: Float
}

struct HandShape {
    let width: Float
    let height: Float
    let aspectRatio: Float
    let compactness: Float
}

struct HandOrientation {
    let rotation: Float
    let tilt: Float
    let roll: Float
}

struct PatternMatch {
    let sign: String
    let similarity: Float
    let pattern: AdaptiveSignRecognition.HandPattern
}

struct AdaptiveRecognitionResult {
    let sign: String
    let confidence: Float
    let isAdaptive: Bool
    let suggestions: [String]
    let timestamp: Date = Date()
}

struct LearnedPatternsExport: Codable {
    let patterns: [String: [HandPatternData]]
    let statistics: RecognitionStatisticsData
    let timestamp: Date
}

// Codable versions of internal types
struct HandPatternData: Codable {
    let features: [Float]
    let confidence: Float
    let timestamp: Date
    let userCorrection: String?
    let culturalContext: String?
    let handPreference: String // Convert enum to string for Codable
}

struct RecognitionStatisticsData: Codable {
    let totalRecognitions: Int
    let correctRecognitions: Int
    let averageConfidence: Float
    let adaptationRate: Float
    let culturalAccuracy: [String: Float]
}

// MARK: - Extension Methods (Placeholders for implementation)

extension AdaptiveSignRecognition {
    
    private func extractFingerExtensions(_ features: [Float]) -> [Float] {
        // Extract finger extension values from hand landmarks
        guard features.count >= 21 else { return Array(repeating: 0.0, count: 5) }
        
        // Simplified extraction - in real implementation, this would analyze
        // the relative positions of finger joints to determine extension
        return Array(features.prefix(5))
    }
    
    private func extractHandShape(_ features: [Float]) -> HandShape {
        // Extract hand shape characteristics
        return HandShape(width: 1.0, height: 1.0, aspectRatio: 1.0, compactness: 1.0)
    }
    
    private func extractFingerCurvatures(_ features: [Float]) -> [Float] {
        // Extract finger curvature values
        return Array(repeating: 0.0, count: 5)
    }
    
    private func extractHandOrientation(_ features: [Float]) -> HandOrientation {
        // Extract hand orientation
        return HandOrientation(rotation: 0.0, tilt: 0.0, roll: 0.0)
    }
    
    private func calculateFeatureConfidence(_ features: [Float]) -> Float {
        // Calculate confidence based on feature quality
        return 0.8
    }
    
    private func applyContextualWeighting(_ similarity: Float, context: RecognitionContext) -> Float {
        // Apply contextual weighting to similarity
        return similarity
    }
    
    private func applyASLAdjustments(_ features: [Float]) -> [Float] {
        // Apply ASL-specific adjustments
        return features
    }
    
    private func applyBSLAdjustments(_ features: [Float]) -> [Float] {
        // Apply BSL-specific adjustments
        return features
    }
    
    private func applyJSLAdjustments(_ features: [Float]) -> [Float] {
        // Apply JSL-specific adjustments
        return features
    }
    
    private func applyGenericAdjustments(_ features: [Float]) -> [Float] {
        // Apply generic adjustments
        return features
    }
    
    private func analyzeFingerPattern(_ extensions: [Float]) -> String {
        // Analyze finger extension pattern
        return "A"
    }
    
    private func analyzeHandShape(_ shape: HandShape) -> String {
        // Analyze hand shape pattern
        return "A"
    }
    
    private func analyzeCurvaturePattern(_ curvatures: [Float]) -> String {
        // Analyze finger curvature pattern
        return "A"
    }
    
    private func combinePatterns(_ fingerPattern: String, _ shapePattern: String, _ curvaturePattern: String) -> String {
        // Combine different pattern analyses
        return fingerPattern
    }
    
    private func applyCulturalContext(_ pattern: String, context: RecognitionContext) -> String {
        // Apply cultural context to pattern
        return pattern
    }
} 