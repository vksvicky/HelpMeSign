import Foundation
import Vision
import CoreML
import AVFoundation
import AppKit

// MARK: - Sign Language Recognition System
class AIUserExperienceSystem: NSObject {
    
    // MARK: - Properties
    static let shared = AIUserExperienceSystem()
    
    // Supported sign languages with their codes and metadata
    private let supportedLanguages: [SignLanguage] = [
        SignLanguage(code: "ASL", name: "American Sign Language", country: "US", flag: "🇺🇸", modelName: "asl_model"),
        SignLanguage(code: "BSL", name: "British Sign Language", country: "GB", flag: "🇬🇧", modelName: "bsl_model"),
        SignLanguage(code: "ISL", name: "Indian Sign Language", country: "IN", flag: "🇮🇳", modelName: "isl_model"),
        SignLanguage(code: "JSL", name: "Japanese Sign Language", country: "JP", flag: "🇯🇵", modelName: "jsl_model"),
        SignLanguage(code: "KSL", name: "Korean Sign Language", country: "KR", flag: "🇰🇷", modelName: "ksl_model"),
        SignLanguage(code: "CSL", name: "Chinese Sign Language", country: "CN", flag: "🇨🇳", modelName: "csl_model"),
        SignLanguage(code: "FSL", name: "French Sign Language", country: "FR", flag: "🇫🇷", modelName: "fsl_model"),
        SignLanguage(code: "DSL", name: "German Sign Language", country: "DE", flag: "🇩🇪", modelName: "dsl_model"),
        SignLanguage(code: "LIS", name: "Italian Sign Language", country: "IT", flag: "🇮🇹", modelName: "lis_model"),
        SignLanguage(code: "LSE", name: "Spanish Sign Language", country: "ES", flag: "🇪🇸", modelName: "lse_model"),
        SignLanguage(code: "RUS", name: "Russian Sign Language", country: "RU", flag: "🇷🇺", modelName: "rus_model"),
        SignLanguage(code: "PSL", name: "Polish Sign Language", country: "PL", flag: "🇵🇱", modelName: "psl_model"),
        SignLanguage(code: "TSL", name: "Turkish Sign Language", country: "TR", flag: "🇹🇷", modelName: "tsl_model"),
        SignLanguage(code: "ARSL", name: "Arabic Sign Language", country: "SA", flag: "🇸🇦", modelName: "arsl_model"),
        SignLanguage(code: "HZSL", name: "Hebrew Sign Language", country: "IL", flag: "🇮🇱", modelName: "hzsl_model"),
        SignLanguage(code: "THSL", name: "Thai Sign Language", country: "TH", flag: "🇹🇭", modelName: "thsl_model"),
        SignLanguage(code: "VSL", name: "Vietnamese Sign Language", country: "VN", flag: "🇻🇳", modelName: "vsl_model"),
        SignLanguage(code: "MSL", name: "Malay Sign Language", country: "MY", flag: "🇲🇾", modelName: "msl_model"),
        SignLanguage(code: "IDSL", name: "Indonesian Sign Language", country: "ID", flag: "🇮🇩", modelName: "idsl_model"),
        SignLanguage(code: "PHSL", name: "Philippine Sign Language", country: "PH", flag: "🇵🇭", modelName: "phsl_model")
    ]
    
    // Current active language
    private var currentLanguage: SignLanguage = SignLanguage(code: "ASL", name: "American Sign Language", country: "US", flag: "🇺🇸", modelName: "asl_model")
    
    // Vision framework components
    private var handPoseRequest: VNDetectHumanHandPoseRequest?
    private var bodyPoseRequest: VNDetectHumanBodyPoseRequest?
    private var faceLandmarksRequest: VNDetectFaceLandmarksRequest?
    
    // ML models
    private var signLanguageModels: [String: MLModel] = [:]
    private var gestureClassifier: MLModel?
    private var poseEstimator: MLModel?
    
    // Recognition state
    private var isRecognizing = false
    private var recognitionConfidence: Float = 0.0
    private var lastRecognizedSign: String = ""
    private var recognitionHistory: [AIRecognitionResult] = []
    private var lastRecognitionTime: Date = Date()
    private var recognitionDebounceInterval: TimeInterval = 3.0 // 3 second debounce for more stability
    private var lastSignCandidate: String = ""
    private var signCandidateCount: Int = 0
    private var requiredCandidateCount: Int = 5 // Must see same sign 5 times before recognizing (increased for stability)
    
    // Frame processing control
    private var lastFrameProcessTime: Date = Date()
    private var frameProcessingInterval: TimeInterval = 0.1 // Process max 10 frames per second
    private var isProcessingFrame = false
    
    // Feature smoothing for stable recognition
    private var lastFeatures: [Float] = []
    private var featureSmoothingFactor: Float = 0.3 // 30% new, 70% old - more stable
    private var featureHistory: [[Float]] = []
    private var maxFeatureHistory: Int = 60 // Keep last 60 frames (2 seconds at 30fps)
    
    // Callbacks
    var onSignRecognized: ((AIRecognitionResult) -> Void)?
    var onLanguageChanged: ((SignLanguage) -> Void)?
    var onRecognitionStateChanged: ((Bool) -> Void)?
    
    // MARK: - Initialization
    override init() {
        super.init()
        setupVisionRequests()
        loadMLModels()
    }
    
    // MARK: - Setup Methods
    private func setupVisionRequests() {
        // Hand pose detection only - disable face and body to prevent crashes
        handPoseRequest = VNDetectHumanHandPoseRequest { [weak self] request, error in
            self?.handleHandPoseDetection(request: request, error: error)
        }
        handPoseRequest?.maximumHandCount = 2
        
        // Disable body pose detection to prevent crashes
        // bodyPoseRequest = VNDetectHumanBodyPoseRequest { [weak self] request, error in
        //     self?.handleBodyPoseDetection(request: request, error: error)
        // }
        
        // Disable face landmarks detection to prevent crashes
        // faceLandmarksRequest = VNDetectFaceLandmarksRequest { [weak self] request, error in
        //     self?.handleFaceLandmarksDetection(request: request, error: error)
        // }
    }
    
    private func loadMLModels() {
        // Load sign language models for each supported language
        for language in supportedLanguages {
            loadModel(for: language)
        }
        
        // Load general gesture classifier
        loadGestureClassifier()
        
        // Load pose estimator
        loadPoseEstimator()
    }
    
    private func loadModel(for language: SignLanguage) {
        // In a real implementation, you would load the actual ML models
        // For now, we'll create placeholder models
        print("Loading model for \(language.name) (\(language.code))")
        
        // Simulate model loading
        DispatchQueue.global(qos: .background).async {
            // Simulate loading time
            Thread.sleep(forTimeInterval: 0.1)
            
            DispatchQueue.main.async {
                print("Model loaded for \(language.name)")
            }
        }
    }
    
    private func loadGestureClassifier() {
        // Load general gesture classification model
        print("Loading gesture classifier")
    }
    
    private func loadPoseEstimator() {
        // Load pose estimation model
        print("Loading pose estimator")
    }
    
    // MARK: - Public Methods
    
    /// Start sign language recognition
    func startRecognition() {
        guard !isRecognizing else { return }
        
        isRecognizing = true
        recognitionHistory.removeAll()
        featureHistory.removeAll()
        lastSignCandidate = ""
        signCandidateCount = 0
        onRecognitionStateChanged?(true)
        
        print("Started sign language recognition for \(currentLanguage.name)")
    }
    
    /// Stop sign language recognition
    func stopRecognition() {
        guard isRecognizing else { return }
        
        isRecognizing = false
        featureHistory.removeAll()
        lastSignCandidate = ""
        signCandidateCount = 0
        onRecognitionStateChanged?(false)
        
        print("Stopped sign language recognition")
    }
    
    /// Process camera frame for sign recognition
    func processFrame(_ sampleBuffer: CMSampleBuffer) {
        guard isRecognizing else { return }
        
        // Frame rate limiting to prevent Vision framework overload
        let now = Date()
        let timeSinceLastFrame = now.timeIntervalSince(lastFrameProcessTime)
        
        if timeSinceLastFrame < frameProcessingInterval || isProcessingFrame {
            return // Skip this frame
        }
        
        isProcessingFrame = true
        lastFrameProcessTime = now
        
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
            print("Failed to get pixel buffer from sample buffer")
            isProcessingFrame = false
            return
        }
        
        // Check if the pixel buffer is valid
        let width = CVPixelBufferGetWidth(pixelBuffer)
        let height = CVPixelBufferGetHeight(pixelBuffer)
        
        guard width > 0 && height > 0 else {
            print("Invalid pixel buffer dimensions: \(width)x\(height)")
            isProcessingFrame = false
            return
        }
        
        // Create image request handler
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up)
        
        // Perform vision requests with proper error handling and reduced load
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            do {
                // Only perform hand pose detection to reduce load and prevent crashes
                if let handPoseRequest = self?.handPoseRequest {
                    try handler.perform([handPoseRequest])
                }
            } catch {
                print("Failed to perform vision requests: \(error)")
            }
            
            DispatchQueue.main.async {
                self?.isProcessingFrame = false
            }
        }
    }
    
    /// Change the current sign language
    func changeLanguage(to languageCode: String) {
        guard let language = supportedLanguages.first(where: { $0.code == languageCode }) else {
            print("Unsupported language: \(languageCode)")
            return
        }
        
        currentLanguage = language
        onLanguageChanged?(language)
        
        print("Changed language to \(language.name) (\(language.code))")
    }
    
    /// Get all supported languages
    func getSupportedLanguages() -> [SignLanguage] {
        return supportedLanguages
    }
    
    /// Get current language
    func getCurrentLanguage() -> SignLanguage {
        return currentLanguage
    }
    
    /// Get recognition history
    func getRecognitionHistory() -> [AIRecognitionResult] {
        return recognitionHistory
    }
    
    /// Clear recognition history
    func clearRecognitionHistory() {
        recognitionHistory.removeAll()
    }
    
    // MARK: - Vision Handlers
    
    private func handleHandPoseDetection(request: VNRequest, error: Error?) {
        if let error = error {
            print("Hand pose detection error: \(error)")
            return
        }
        
        guard let observations = request.results as? [VNHumanHandPoseObservation] else {
            return
        }
        
        for observation in observations {
            processHandPose(observation)
        }
    }
    
    private func handleBodyPoseDetection(request: VNRequest, error: Error?) {
        guard let observations = request.results as? [VNHumanBodyPoseObservation] else {
            return
        }
        
        for observation in observations {
            processBodyPose(observation)
        }
    }
    
    private func handleFaceLandmarksDetection(request: VNRequest, error: Error?) {
        guard let observations = request.results as? [VNFaceObservation] else {
            return
        }
        
        for observation in observations {
            processFaceLandmarks(observation)
        }
    }
    
    // MARK: - Pose Processing
    
    private func processHandPose(_ observation: VNHumanHandPoseObservation) {
        // Extract hand landmarks
        guard let landmarks = try? observation.recognizedPoints(.all) else {
            return
        }
        
        // Convert landmarks to feature vector
        let rawFeatures = extractHandFeatures(from: landmarks)
        
        // Apply feature smoothing for stable recognition
        let smoothedFeatures = smoothFeatures(rawFeatures)
        
        // Classify the sign
        classifySign(features: smoothedFeatures)
    }
    
    private func smoothFeatures(_ newFeatures: [Float]) -> [Float] {
        guard !newFeatures.isEmpty else { return newFeatures }
        
        if lastFeatures.isEmpty {
            lastFeatures = newFeatures
            return newFeatures
        }
        
        // Apply exponential smoothing
        let smoothedFeatures = zip(newFeatures, lastFeatures).map { new, old in
            new * featureSmoothingFactor + old * (1 - featureSmoothingFactor)
        }
        
        lastFeatures = smoothedFeatures
        return smoothedFeatures
    }
    
    private func processBodyPose(_ observation: VNHumanBodyPoseObservation) {
        // Extract body landmarks
        guard let landmarks = try? observation.recognizedPoints(.all) else {
            return
        }
        
        // Process body pose for context
        let bodyFeatures = extractBodyFeatures(from: landmarks)
        
        // Use body pose to enhance sign recognition
        enhanceRecognitionWithBodyPose(bodyFeatures)
    }
    
    private func processFaceLandmarks(_ observation: VNFaceObservation) {
        // Extract face landmarks
        guard let landmarks = observation.landmarks else {
            return
        }
        
        // Process facial expressions for context
        let faceFeatures = extractFaceFeatures(from: landmarks)
        
        // Use facial expressions to enhance sign recognition
        enhanceRecognitionWithFaceExpressions(faceFeatures)
    }
    
    // MARK: - Feature Extraction
    
    private func extractHandFeatures(from landmarks: [VNHumanHandPoseObservation.JointName: VNRecognizedPoint]) -> [Float] {
        var features: [Float] = []
        
        // Extract joint positions with confidence filtering
        for joint in VNHumanHandPoseObservation.JointName.allCases {
            if let point = landmarks[joint], point.confidence > 0.3 {
                // Only include high-confidence landmarks
                features.append(Float(point.location.x))
                features.append(Float(point.location.y))
                features.append(Float(point.confidence))
            } else {
                // Use zeros for low-confidence or missing landmarks
                features.append(0.0)
                features.append(0.0)
                features.append(0.0)
            }
        }
        
        // Normalize features to reduce noise
        if !features.isEmpty {
            let maxValue = features.max() ?? 1.0
            if maxValue > 0 {
                features = features.map { $0 / maxValue }
            }
        }
        
        return features
    }
    
    private func extractBodyFeatures(from landmarks: [VNHumanBodyPoseObservation.JointName: VNRecognizedPoint]) -> [Float] {
        var features: [Float] = []
        
        // Extract key body joint positions
        let keyJoints: [VNHumanBodyPoseObservation.JointName] = [
            .nose, .leftShoulder, .rightShoulder, .leftElbow, .rightElbow,
            .leftWrist, .rightWrist, .leftHip, .rightHip
        ]
        
        for joint in keyJoints {
            if let point = landmarks[joint] {
                features.append(Float(point.location.x))
                features.append(Float(point.location.y))
                features.append(Float(point.confidence))
            } else {
                features.append(0.0)
                features.append(0.0)
                features.append(0.0)
            }
        }
        
        return features
    }
    
    private func extractFaceFeatures(from landmarks: VNFaceLandmarks2D) -> [Float] {
        var features: [Float] = []
        
        // Extract key facial landmarks
        if let leftEye = landmarks.leftEye {
            features.append(contentsOf: leftEye.normalizedPoints.flatMap { [Float($0.x), Float($0.y)] })
        }
        
        if let rightEye = landmarks.rightEye {
            features.append(contentsOf: rightEye.normalizedPoints.flatMap { [Float($0.x), Float($0.y)] })
        }
        
        if let outerLips = landmarks.outerLips {
            features.append(contentsOf: outerLips.normalizedPoints.flatMap { [Float($0.x), Float($0.y)] })
        }
        
        return features
    }
    
    // MARK: - Sign Classification
    
    private func classifySign(features: [Float]) {
        // In a real implementation, you would use the loaded ML models
        // For now, we'll implement a more realistic feature-based classification
        
        // Simulate classification delay
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            // Use feature vector to determine sign (more consistent)
            let sign = self?.determineSignFromFeatures(features) ?? "A"
            let confidence = self?.calculateConfidence(features) ?? 0.8
            
            // Debug: Print feature stability
            if let keyFeatures = self?.extractKeyHandFeatures(features) {
                let featureSignature = keyFeatures.map { round($0 * 10) / 10 }.prefix(6)
                print("🎯 Processing sign: \(sign) with confidence: \(confidence)")
                print("🎯 Key features: \(featureSignature)")
            }
            
            DispatchQueue.main.async {
                self?.handleSignCandidate(sign: sign, confidence: confidence, features: features)
            }
        }
    }
    
    private func handleSignCandidate(sign: String, confidence: Float, features: [Float]) {
        // Only process high-confidence candidates
        guard confidence > 0.8 else { // Increased threshold for stability
            print("Sign candidate confidence too low: \(confidence)")
            return
        }
        
        // Check if this is the same sign as the last candidate
        if sign == lastSignCandidate {
            signCandidateCount += 1
            print("Sign candidate '\(sign)' count: \(signCandidateCount)/\(requiredCandidateCount)")
        } else {
            // Reset for new sign
            lastSignCandidate = sign
            signCandidateCount = 1
            print("New sign candidate: '\(sign)'")
        }
        
        // Only recognize if we've seen the same sign multiple times
        if signCandidateCount >= requiredCandidateCount {
            print("🎯 FINAL RECOGNITION: \(sign) with \(signCandidateCount) consistent detections!")
            handleSignRecognition(sign: sign, confidence: confidence, features: features)
            // Reset after recognition to prevent repeated recognition
            signCandidateCount = 0
            lastSignCandidate = "" // Clear the last candidate to force new sign detection
        }
    }
    
    private func determineSignFromFeatures(_ features: [Float]) -> String {
        // Use feature vector to determine sign consistently (SIGNSlate approach)
        // This simulates how a real ML model would work
        
        guard !features.isEmpty else { return "A" }
        
        // Add current features to history (SIGNSlate's 2-second window approach)
        featureHistory.append(features)
        if featureHistory.count > maxFeatureHistory {
            featureHistory.removeFirst()
        }
        
        // Use average of recent features for more stability (SIGNSlate's dominant average)
        let averageFeatures = averageFeatureHistory()
        
        // Create a more stable feature signature based on hand position
        // Focus on key hand landmarks for more consistent recognition
        let keyFeatures = extractKeyHandFeatures(averageFeatures)
        
        // Use a more deterministic mapping based on hand shape
        let signIndex = determineSignFromHandShape(keyFeatures)
        
        let signs = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"] // Only A-J for testing stability
        return signs[signIndex]
    }
    
    private func extractKeyHandFeatures(_ features: [Float]) -> [Float] {
        // Extract key features that represent hand shape more consistently
        // Focus on finger positions and hand orientation
        guard features.count >= 42 else { return features } // 21 joints * 2 coordinates
        
        var keyFeatures: [Float] = []
        
        // Extract wrist position (base reference)
        let wristX = features[0]
        let wristY = features[1]
        keyFeatures.append(wristX)
        keyFeatures.append(wristY)
        
        // Extract finger tip positions relative to wrist
        let fingerTips = [8, 12, 16, 20] // Index, middle, ring, little finger tips
        for tipIndex in fingerTips {
            let baseIndex = tipIndex * 2
            if baseIndex + 1 < features.count {
                let tipX = features[baseIndex] - wristX
                let tipY = features[baseIndex + 1] - wristY
                keyFeatures.append(tipX)
                keyFeatures.append(tipY)
            }
        }
        
        // Extract thumb position
        let thumbTipIndex = 4 * 2
        if thumbTipIndex + 1 < features.count {
            let thumbX = features[thumbTipIndex] - wristX
            let thumbY = features[thumbTipIndex + 1] - wristY
            keyFeatures.append(thumbX)
            keyFeatures.append(thumbY)
        }
        
        return keyFeatures
    }
    
    private func determineSignFromHandShape(_ keyFeatures: [Float]) -> Int {
        guard keyFeatures.count >= 12 else { return 0 } // Need at least 6 points (x,y)
        
        // Create a much more stable signature based on hand shape
        // Use only the most stable features (wrist and finger tips)
        let stableFeatures = Array(keyFeatures.prefix(10)) // First 5 points (x,y)
        
        // Normalize to larger buckets for stability
        let normalizedFeatures = stableFeatures.map { round($0 * 5) / 5 } // Round to 0.2 for much more stability
        
        // Calculate a simpler, more stable signature
        var signature: Int = 0
        for (index, feature) in normalizedFeatures.enumerated() {
            // Use smaller multipliers to reduce sensitivity
            signature += Int(feature * 20) * (index + 1)
        }
        
        // Use a smaller modulo for more consistent results
        let signIndex = abs(signature) % 10 // Only 10 signs for now (A-J) for testing
        
        // Map to specific signs based on hand position
        // This simulates a more realistic classification
        let signMapping = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] // A, B, C, D, E, F, G, H, I, J
        
        return signMapping[signIndex]
    }
    
    private func averageFeatureHistory() -> [Float] {
        guard !featureHistory.isEmpty else { return [] }
        
        let featureCount = featureHistory[0].count
        var averagedFeatures: [Float] = Array(repeating: 0.0, count: featureCount)
        
        for features in featureHistory {
            for (index, value) in features.enumerated() {
                if index < featureCount {
                    averagedFeatures[index] += value
                }
            }
        }
        
        return averagedFeatures.map { $0 / Float(featureHistory.count) }
    }
    
    private func calculateConfidence(_ features: [Float]) -> Float {
        // Calculate confidence based on feature quality
        guard !features.isEmpty else { return 0.5 }
        
        // Higher confidence for more stable features
        let averageFeature = features.reduce(0, +) / Float(features.count)
        let variance = features.map { pow($0 - averageFeature, 2) }.reduce(0, +) / Float(features.count)
        
        // Lower variance = higher confidence (more stable hand position)
        let stabilityScore = max(0, 1 - variance)
        return min(0.95, max(0.6, stabilityScore))
    }
    
    private func enhanceRecognitionWithBodyPose(_ features: [Float]) {
        // Use body pose to enhance sign recognition accuracy
        // This could include checking for proper arm positioning, body orientation, etc.
    }
    
    private func enhanceRecognitionWithFaceExpressions(_ features: [Float]) {
        // Use facial expressions to enhance sign recognition accuracy
        // This could include checking for mouth movements, facial expressions, etc.
    }
    
    private func handleSignRecognition(sign: String, confidence: Float, features: [Float]) {
        let now = Date()
        
        // Debounce: only recognize if enough time has passed or if it's a different sign
        let timeSinceLastRecognition = now.timeIntervalSince(lastRecognitionTime)
        let isSameSign = sign == lastRecognizedSign
        
        if timeSinceLastRecognition < recognitionDebounceInterval && isSameSign {
            // Skip recognition - too soon and same sign
            print("⏸️ Skipping recognition: \(sign) (debounced)")
            return
        }
        
        // Only recognize if confidence is high enough
        guard confidence > 0.8 else { // Increased threshold for stability
            print("Sign recognition confidence too low: \(confidence)")
            return
        }
        
        // Check if features have changed significantly
        if !lastFeatures.isEmpty && isSameSign {
            let featureChange = calculateFeatureChange(features, comparedTo: lastFeatures)
            if featureChange < 0.1 { // Less than 10% change
                print("Features too similar, skipping recognition")
                return
            }
        }
        
        let result = AIRecognitionResult(
            sign: sign,
            confidence: confidence,
            language: currentLanguage,
            timestamp: now,
            features: features
        )
        
        recognitionHistory.append(result)
        lastRecognizedSign = sign
        recognitionConfidence = confidence
        lastRecognitionTime = now
        
        onSignRecognized?(result)
        
        print("Recognized sign: \(sign) with confidence: \(confidence)")
    }
    
    private func calculateFeatureChange(_ newFeatures: [Float], comparedTo oldFeatures: [Float]) -> Float {
        guard newFeatures.count == oldFeatures.count else { return 1.0 }
        
        let differences = zip(newFeatures, oldFeatures).map { abs($0 - $1) }
        let averageDifference = differences.reduce(0, +) / Float(differences.count)
        return averageDifference
    }
}

// MARK: - Supporting Types

struct SignLanguage {
    let code: String
    let name: String
    let country: String
    let flag: String
    let modelName: String
}

struct AIRecognitionResult {
    let sign: String
    let confidence: Float
    let language: SignLanguage
    let timestamp: Date
    let features: [Float]
}

// MARK: - Extensions

extension VNHumanHandPoseObservation.JointName: CaseIterable {
    public static var allCases: [VNHumanHandPoseObservation.JointName] {
        return [
            .wrist, .thumbCMC, .thumbMP, .thumbIP, .thumbTip,
            .indexMCP, .indexPIP, .indexDIP, .indexTip,
            .middleMCP, .middlePIP, .middleDIP, .middleTip,
            .ringMCP, .ringPIP, .ringDIP, .ringTip,
            .littleMCP, .littlePIP, .littleDIP, .littleTip
        ]
    }
} 