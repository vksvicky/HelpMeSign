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
    
    // MARK: - Public Properties for Testing
    var isRecognitionActive: Bool {
        return isRecognizing
    }
    
    var activeLanguage: SignLanguage {
        return currentLanguage
    }
    
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
    private let featureQueue = DispatchQueue(label: "com.helpmesign.feature-processing", qos: .userInitiated)
    
    // Hand preference
    private var handPreference: String = "Right" // Default to right hand
    
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
    
    /// Update hand preference for recognition
    func updateHandPreference(_ preference: String) {
        handPreference = preference
        print("AIUserExperienceSystem: Hand preference updated to \(preference)")
        
        // Store the preference for use in hand pose processing
        // The Vision framework will detect both hands, but we can prioritize processing
        // based on the user's preference in the feature extraction
    }
    
    /// Start sign language recognition
    func startRecognition() {
        guard !isRecognizing else { return }
        
        isRecognizing = true
        recognitionHistory.removeAll()
        featureQueue.sync {
            featureHistory.removeAll()
        }
        lastSignCandidate = ""
        signCandidateCount = 0
        onRecognitionStateChanged?(true)
        
        print("Started sign language recognition for \(currentLanguage.name)")
    }
    
    /// Stop sign language recognition
    func stopRecognition() {
        guard isRecognizing else { return }
        
        isRecognizing = false
        featureQueue.sync {
            featureHistory.removeAll()
        }
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
    
    // MARK: - Public Methods for Testing
    
    /// Set the current language (for testing)
    func setLanguage(_ language: SignLanguage) {
        currentLanguage = language
        onLanguageChanged?(language)
    }
    
    /// Extract key hand features (for testing)
    func testExtractKeyHandFeatures(_ features: [Float]) -> [Float] {
        return extractKeyHandFeatures(features)
    }
    
    /// Determine sign from hand shape (for testing)
    func testDetermineSignFromHandShape(_ keyFeatures: [Float]) -> Int {
        return determineSignFromHandShape(keyFeatures)
    }
    
    /// Calculate confidence (for testing)
    func testCalculateConfidence(_ features: [Float]) -> Float {
        return calculateConfidence(features)
    }
    
    /// Clear feature history (for testing)
    func clearFeatureHistory() {
        featureQueue.sync {
            featureHistory.removeAll()
        }
    }
    
    /// Process features (for testing)
    func processFeatures(_ features: [Float]) {
        classifySign(features: features)
    }
    
    /// Process features for testing with immediate recognition (bypasses thresholds)
    func processFeaturesForTesting(_ features: [Float]) {
        // For testing, bypass the normal thresholds and trigger recognition immediately
        let sign = determineSignFromFeatures(features)
        let confidence = calculateConfidence(features)
        
        // For testing, create result directly and trigger callback, bypassing all restrictions
        let result = AIRecognitionResult(
            sign: sign,
            confidence: confidence,
            language: currentLanguage,
            timestamp: Date(),
            features: features
        )
        
        // Update state
        recognitionHistory.append(result)
        lastRecognizedSign = sign
        recognitionConfidence = confidence
        lastRecognitionTime = Date()
        
        // Trigger callback directly for testing
        onSignRecognized?(result)
        
        print("Test recognition: \(sign) with confidence: \(confidence)")
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
        for joint in VNHumanHandPoseObservation.JointName.allJointNames {
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
                
                // Debug hand shape characteristics
                if keyFeatures.count >= 6 {
                    let wristX = keyFeatures[0]
                    let wristY = keyFeatures[1]
                    let indexTipX = keyFeatures[2]
                    let indexTipY = keyFeatures[3]
                    let middleTipX = keyFeatures[4]
                    let middleTipY = keyFeatures[5]
                    
                    let handSpread = sqrt(pow(indexTipX - middleTipX, 2) + pow(indexTipY - middleTipY, 2))
                    let handHeight = max(indexTipY, middleTipY) - wristY
                    let handWidth = max(indexTipX, middleTipX) - wristX
                    
                    let normalizedSpread = round(handSpread * 10) / 10
                    let normalizedHeight = round(handHeight * 10) / 10
                    let normalizedWidth = round(handWidth * 10) / 10
                    
                    print("🎯 Hand shape: H=\(normalizedHeight), W=\(normalizedWidth), S=\(normalizedSpread)")
                }
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
        featureQueue.sync {
            featureHistory.append(features)
            if featureHistory.count > maxFeatureHistory {
                featureHistory.removeFirst()
            }
        }
        
        // Use average of recent features for more stability (SIGNSlate's dominant average)
        let averageFeatures = averageFeatureHistory()
        
        // Create a more stable feature signature based on hand position
        // Focus on key hand landmarks for more consistent recognition
        let keyFeatures = extractKeyHandFeatures(averageFeatures)
        
        // Use a more deterministic mapping based on hand shape
        let signIndex = determineSignFromHandShape(keyFeatures)
        
        let signs = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"] // Only A-J for testing stability
        let safeIndex = max(0, min(signIndex, signs.count - 1))
        return signs[safeIndex]
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
        guard keyFeatures.count >= 12 else { return 0 } // Need exactly 12 features for hand shape analysis
        
        // Extract key hand position indicators with bounds checking
        let wristX = keyFeatures.count > 0 ? keyFeatures[0] : 0.0
        let wristY = keyFeatures.count > 1 ? keyFeatures[1] : 0.0
        
        // Extract finger tip positions relative to wrist
        let indexTipX = keyFeatures.count > 2 ? keyFeatures[2] : 0.0 // Index finger tip X
        let indexTipY = keyFeatures.count > 3 ? keyFeatures[3] : 0.0 // Index finger tip Y
        let middleTipX = keyFeatures.count > 4 ? keyFeatures[4] : 0.0 // Middle finger tip X
        let middleTipY = keyFeatures.count > 5 ? keyFeatures[5] : 0.0 // Middle finger tip Y
        
        // Calculate hand shape characteristics
        let handSpread = sqrt(pow(indexTipX - middleTipX, 2) + pow(indexTipY - middleTipY, 2))
        let handHeight = max(indexTipY, middleTipY) - wristY
        let handWidth = max(indexTipX, middleTipX) - wristX
        
        // Normalize to stable ranges
        _ = round(handSpread * 10) / 10 // normalizedSpread - unused but keeping for potential future use
        let normalizedHeight = round(handHeight * 10) / 10
        let normalizedWidth = round(handWidth * 10) / 10
        
        // Map hand shapes to specific ASL letters based on real ASL characteristics
        // This creates consistent mapping for similar hand positions
        if normalizedHeight > 0.5 && normalizedWidth < 0.2 {
            // Hand pointing up with fingers together = A
            return 0 // A
        } else if normalizedHeight > 0.4 && normalizedWidth > 0.3 {
            // Hand spread wide = B
            return 1 // B
        } else if normalizedHeight > 0.3 && normalizedWidth < 0.1 {
            // Hand curved = C
            return 2 // C
        } else if normalizedHeight > 0.6 && normalizedWidth < 0.1 {
            // Hand pointing up with index finger = D
            return 3 // D
        } else if normalizedHeight > 0.4 && normalizedWidth < 0.2 {
            // Hand with fingers together pointing up = E
            return 4 // E
        } else if normalizedHeight > 0.3 && normalizedWidth > 0.2 {
            // Hand with thumb and index touching = F
            return 5 // F
        } else if normalizedHeight > 0.5 && normalizedWidth > 0.2 {
            // Hand with index pointing = G
            return 6 // G
        } else if normalizedHeight > 0.4 && normalizedWidth < 0.3 {
            // Hand with index and middle pointing = H
            return 7 // H
        } else if normalizedHeight > 0.6 && normalizedWidth < 0.1 {
            // Hand with pinky pointing up = I
            return 8 // I
        } else {
            // Default case = J
            return 9 // J
        }
    }
    
    private func averageFeatureHistory() -> [Float] {
        return featureQueue.sync {
            guard !featureHistory.isEmpty else { return [] }
            
            // Find the minimum feature count to avoid index out of bounds
            let minFeatureCount = featureHistory.map { $0.count }.min() ?? 0
            guard minFeatureCount > 0 else { return [] }
            
            var averagedFeatures: [Float] = Array(repeating: 0.0, count: minFeatureCount)
            
            for features in featureHistory {
                for (index, value) in features.enumerated() {
                    if index < minFeatureCount {
                        averagedFeatures[index] += value
                    }
                }
            }
            
            return averagedFeatures.map { $0 / Float(featureHistory.count) }
        }
    }
    
    private func calculateConfidence(_ features: [Float]) -> Float {
        // Calculate confidence based on feature quality
        guard !features.isEmpty else { return 0.0 }
        
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

// MARK: - Joint Name Array (Alternative to CaseIterable extension)

// Using a static array instead of CaseIterable extension to avoid potential conflicts
// with future Vision framework updates
extension VNHumanHandPoseObservation.JointName {
    static var allJointNames: [VNHumanHandPoseObservation.JointName] {
        return [
            .wrist, .thumbCMC, .thumbMP, .thumbIP, .thumbTip,
            .indexMCP, .indexPIP, .indexDIP, .indexTip,
            .middleMCP, .middlePIP, .middleDIP, .middleTip,
            .ringMCP, .ringPIP, .ringDIP, .ringTip,
            .littleMCP, .littlePIP, .littleDIP, .littleTip
        ]
    }
} 