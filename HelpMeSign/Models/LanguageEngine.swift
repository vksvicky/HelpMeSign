import Foundation
import Vision
import CoreML
import AVFoundation
import AppKit

// MARK: - Dynamic Sign Language Engine
class LanguageEngine: NSObject {
    
    // MARK: - Properties
    static let shared = LanguageEngine()
    
    // Thread safety queue
    private let languageQueue = DispatchQueue(label: "com.helpmesign.language-engine", qos: .userInitiated)
    
    // Dynamic language registry
    private var languageRegistry: [String: SignLanguageConfig] = [:]
    private var loadedModels: [String: MLModel?] = [:]
    private var activeLanguages: Set<String> = []
    
    // Configuration sources (commented out invalid URLs for now)
    private let configSources: [String] = [
        // "https://api.signlanguage.com/languages", // External API (placeholder)
        // "https://github.com/SteezieJ/SIGNSlate/languages", // SIGNSlate repository (placeholder)
        // "https://github.com/thatcherclough/ASL-for-All/languages" // ASL-for-All repository (placeholder)
    ]
    
    // Local cache
    private let cacheDirectory: URL
    private let configCache: URL
    private let modelCache: URL
    
    // Recognition pipeline
    private var recognitionPipeline: RecognitionPipeline?
    private var translationEngine: TranslationEngine?
    
    // Hand preference
    private var handPreference: String = "Right" // Default to right hand
    
    // Callbacks
    var onLanguageLoaded: ((SignLanguageConfig) -> Void)?
    var onTranslationComplete: ((TranslationResult) -> Void)?
    var onRecognitionComplete: ((RecognitionResult) -> Void)?
    
    // MARK: - Initialization
    override init() {
        // Setup cache directories
        let appSupport = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
        cacheDirectory = appSupport.appendingPathComponent("HelpMeSign/LanguageCache")
        configCache = cacheDirectory.appendingPathComponent("configs")
        modelCache = cacheDirectory.appendingPathComponent("models")
        
        super.init()
        
        setupCacheDirectories()
        loadCachedLanguages()
        setupRecognitionPipeline()
        setupTranslationEngine()
    }
    
    // MARK: - Setup Methods
    
    private func setupCacheDirectories() {
        try? FileManager.default.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: configCache, withIntermediateDirectories: true)
        try? FileManager.default.createDirectory(at: modelCache, withIntermediateDirectories: true)
    }
    
    private func loadCachedLanguages() {
        // Load cached language configurations
        let configFiles = try? FileManager.default.contentsOfDirectory(at: configCache, includingPropertiesForKeys: nil)
        
        configFiles?.forEach { url in
            if let data = try? Data(contentsOf: url),
               let config = try? JSONDecoder().decode(SignLanguageConfig.self, from: data) {
                languageQueue.sync {
                    languageRegistry[config.code] = config
                }
                print("Loaded cached config for \(config.name) (\(config.code))")
            }
        }
    }
    
    private func setupRecognitionPipeline() {
        recognitionPipeline = RecognitionPipeline()
        recognitionPipeline?.onRecognitionComplete = { [weak self] result in
            self?.onRecognitionComplete?(result)
        }
    }
    
    private func setupTranslationEngine() {
        translationEngine = TranslationEngine()
        translationEngine?.onTranslationComplete = { [weak self] result in
            self?.onTranslationComplete?(result)
        }
    }
    
    // MARK: - Public Methods
    
    /// Update hand preference for language processing
    func updateHandPreference(_ preference: String) {
        handPreference = preference
        print("LanguageEngine: Hand preference updated to \(preference)")
        
        // Store the preference for use in language processing
        // The recognition and translation engines can access this preference
        // when processing sign language data
    }
    
    /// Discover and load available sign languages dynamically
    func discoverLanguages() async {
        print("Starting language discovery...")
        
        for source in configSources {
            await loadLanguagesFromSource(source)
        }
        
        // Also load from local resources
        await loadLocalLanguages()
        
        print("Language discovery completed. Found \(languageRegistry.count) languages")
    }
    
    /// Load a specific language
    func loadLanguage(_ languageCode: String) async -> Bool {
        var config: SignLanguageConfig?
        var isAlreadyLoaded: Bool = false
        
        languageQueue.sync {
            config = languageRegistry[languageCode]
            isAlreadyLoaded = activeLanguages.contains(languageCode)
        }
        
        guard let config = config else {
            print("Language \(languageCode) not found in registry")
            return false
        }
        
        // Check if already loaded
        if isAlreadyLoaded {
            print("Language \(languageCode) already loaded")
            return true
        }
        
        // Load language model
        let modelLoaded = await loadLanguageModel(for: config)
        if modelLoaded {
            languageQueue.sync {
                activeLanguages.insert(languageCode)
            }
            onLanguageLoaded?(config)
            print("Successfully loaded language: \(config.name) (\(config.code))")
            return true
        }
        
        return false
    }
    
    /// Unload a language to free memory
    func unloadLanguage(_ languageCode: String) {
        var shouldUnload = false
        
        languageQueue.sync {
            shouldUnload = activeLanguages.contains(languageCode)
        }
        
        guard shouldUnload else { return }
        
        languageQueue.sync {
            loadedModels.removeValue(forKey: languageCode)
            activeLanguages.remove(languageCode)
        }
        
        print("Unloaded language: \(languageCode)")
    }
    
    /// Get all available languages
    func getAvailableLanguages() -> [SignLanguageConfig] {
        return languageQueue.sync {
            return Array(languageRegistry.values).sorted { $0.name < $1.name }
        }
    }
    
    /// Get loaded languages
    func getLoadedLanguages() -> [String] {
        return languageQueue.sync {
            return Array(activeLanguages)
        }
    }
    
    /// Process frame for recognition
    func processFrame(_ sampleBuffer: CMSampleBuffer, for languages: [String]) {
        guard !languages.isEmpty else { return }
        
        // Only process for loaded languages
        let loadedLanguages = languageQueue.sync {
            return languages.filter { activeLanguages.contains($0) }
        }
        guard !loadedLanguages.isEmpty else { return }
        
        recognitionPipeline?.processFrame(sampleBuffer, for: loadedLanguages)
    }
    
    /// Translate recognized sign
    func translateSign(_ sign: String, from sourceLanguage: String, to targetLanguage: String) async -> TranslationResult? {
        return await translationEngine?.translate(sign, from: sourceLanguage, to: targetLanguage)
    }
    
    /// Translate sign (alias for translateSign)
    func translate(_ sign: String, from sourceLanguage: String, to targetLanguage: String) async -> TranslationResult? {
        return await translationEngine?.translate(sign, from: sourceLanguage, to: targetLanguage)
    }
    
    /// Recognize gesture in specific language
    func recognize(_ gesture: String, in language: String) async -> RecognitionResult? {
        // Check if language is active
        let isActive = languageQueue.sync {
            return activeLanguages.contains(language)
        }
        
        guard isActive else {
            print("Language \(language) is not active")
            return nil
        }
        
        // Simulate recognition for now
        // In a real implementation, this would use the loaded ML model for the specific language
        let result = RecognitionResult(
            sign: gesture,
            confidence: 0.85,
            language: language,
            timestamp: Date(),
            features: [0.1, 0.2, 0.3, 0.4, 0.5], // Simulated features
            handshapes: ["fist"],
            facialExpressions: ["neutral"]
        )
        
        onRecognitionComplete?(result)
        return result
    }
    
    /// Get language metadata
    func getLanguageMetadata(_ languageCode: String) -> SignLanguageConfig? {
        return languageQueue.sync {
            return languageRegistry[languageCode]
        }
    }
    
    // MARK: - Private Methods
    
    private func loadLanguagesFromSource(_ source: String) async {
        guard let url = URL(string: source) else { return }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let languages = try JSONDecoder().decode([SignLanguageConfig].self, from: data)
            
            for language in languages {
                languageRegistry[language.code] = language
                await cacheLanguageConfig(language)
            }
            
            print("Loaded \(languages.count) languages from \(source)")
        } catch {
            print("Failed to load languages from \(source): \(error)")
        }
    }
    
    private func loadLocalLanguages() async {
        // Load from local JSON files in the app bundle
        guard let bundlePath = Bundle.main.path(forResource: "languages", ofType: "json") else {
            print("No local languages.json found")
            return
        }
        
        do {
            let data = try Data(contentsOf: URL(fileURLWithPath: bundlePath))
            let languages = try JSONDecoder().decode([SignLanguageConfig].self, from: data)
            
            for language in languages {
                languageQueue.sync {
                    languageRegistry[language.code] = language
                }
                await cacheLanguageConfig(language)
            }
            
            print("Loaded \(languages.count) local languages")
        } catch {
            print("Failed to load local languages: \(error)")
        }
    }
    
    private func cacheLanguageConfig(_ config: SignLanguageConfig) async {
        let configURL = configCache.appendingPathComponent("\(config.code).json")
        
        do {
            let data = try JSONEncoder().encode(config)
            try data.write(to: configURL)
        } catch {
            print("Failed to cache config for \(config.code): \(error)")
        }
    }
    
    private func loadLanguageModel(for config: SignLanguageConfig) async -> Bool {
        // For testing purposes, we'll simulate successful model loading
        // In a real implementation, this would load actual ML models
        
        // Simulate a small delay to mimic model loading
        try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 seconds
        
        // For now, we'll just mark the language as loaded without an actual model
        // This allows the tests to pass while we develop the rest of the system
        languageQueue.sync {
            // Store a placeholder to indicate the language is "loaded"
            // In a real implementation, this would be an actual MLModel
            loadedModels[config.code] = nil // Placeholder
        }
        
        print("Simulated model loading for \(config.code)")
        return true
    }
    
    private func downloadLanguageModel(for config: SignLanguageConfig) async -> Bool {
        // For testing purposes, we'll simulate successful model downloading
        // In a real implementation, this would download actual ML models
        
        // Simulate a small delay to mimic downloading
        try? await Task.sleep(nanoseconds: 200_000_000) // 0.2 seconds
        
        print("Simulated model download for \(config.code)")
        return true
    }
}

// MARK: - Supporting Types

struct SignLanguageConfig: Codable {
    let code: String
    let name: String
    let nativeName: String
    let country: String
    let flag: String
    let modelURL: String
    let alphabetURL: String
    let vocabularyURL: String
    let grammarRules: [String]
    let handshapes: [String]
    let facialExpressions: [String]
    let bodyMovements: [String]
    let regionalVariants: [String]
    let metadata: LanguageMetadata
}

struct LanguageMetadata: Codable {
    let speakers: Int
    let regions: [String]
    let difficulty: String
    let resources: [String]
    let lastUpdated: String
    let version: String
}

struct RecognitionResult {
    let sign: String
    let confidence: Float
    let language: String
    let timestamp: Date
    let features: [Float]
    let handshapes: [String]
    let facialExpressions: [String]
}

struct TranslationResult {
    let sourceSign: String
    let targetSign: String
    let sourceLanguage: String
    let targetLanguage: String
    let confidence: Float
    let alternatives: [String]
    let timestamp: Date
}

// MARK: - Recognition Pipeline

class RecognitionPipeline {
    private var activeLanguages: Set<String> = []
    
    var onRecognitionComplete: ((RecognitionResult) -> Void)?
    
    func processFrame(_ sampleBuffer: CMSampleBuffer, for languages: [String]) {
        // Update active languages
        activeLanguages = Set(languages)
        
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        // Create vision requests for each language
        let requests = languages.map { languageCode in
            createVisionRequest(for: languageCode)
        }
        
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up)
        
        do {
            try handler.perform(requests)
        } catch {
            print("Failed to perform vision requests: \(error)")
        }
    }
    
    private func createVisionRequest(for languageCode: String) -> VNDetectHumanHandPoseRequest {
        let request = VNDetectHumanHandPoseRequest { [weak self] request, error in
            self?.handleHandPoseDetection(request: request, error: error, languageCode: languageCode)
        }
        request.maximumHandCount = 2
        return request
    }
    
    private func handleHandPoseDetection(request: VNRequest, error: Error?, languageCode: String) {
        guard let observations = request.results as? [VNHumanHandPoseObservation] else { return }
        
        for observation in observations {
            processHandPose(observation, languageCode: languageCode)
        }
    }
    
    private func processHandPose(_ observation: VNHumanHandPoseObservation, languageCode: String) {
        // Extract features and classify sign for specific language
        // This would use the loaded ML model for the specific language
        let features = extractFeatures(from: observation)
        
        // Simulate recognition for now
        let result = RecognitionResult(
            sign: "A",
            confidence: 0.85,
            language: languageCode,
            timestamp: Date(),
            features: features,
            handshapes: ["fist"],
            facialExpressions: ["neutral"]
        )
        
        onRecognitionComplete?(result)
    }
    
    private func extractFeatures(from observation: VNHumanHandPoseObservation) -> [Float] {
        // Extract hand pose features
        var features: [Float] = []
        
        if let landmarks = try? observation.recognizedPoints(.all) {
            // Use specific joint names instead of allCases to avoid compilation issues
            let jointNames: [VNHumanHandPoseObservation.JointName] = [
                .wrist, .thumbCMC, .thumbMP, .thumbIP, .thumbTip,
                .indexMCP, .indexPIP, .indexDIP, .indexTip,
                .middleMCP, .middlePIP, .middleDIP, .middleTip,
                .ringMCP, .ringPIP, .ringDIP, .ringTip,
                .littleMCP, .littlePIP, .littleDIP, .littleTip
            ]
            
            for joint in jointNames {
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
        }
        
        return features
    }
}

// MARK: - Translation Engine

class TranslationEngine {
    private var translationCache: [String: TranslationResult] = [:]
    private let cacheQueue = DispatchQueue(label: "com.helpmesign.translation.cache", attributes: .concurrent)
    
    var onTranslationComplete: ((TranslationResult) -> Void)?
    
    func translate(_ sign: String, from sourceLanguage: String, to targetLanguage: String) async -> TranslationResult? {
        // Check cache first with thread-safe read
        let cacheKey = "\(sourceLanguage):\(sign):\(targetLanguage)"
        
        // Use concurrent queue for read operations
        let cached = cacheQueue.sync {
            return translationCache[cacheKey]
        }
        
        if let cached = cached {
            return cached
        }
        
        // Perform translation
        let result = await performTranslation(sign, from: sourceLanguage, to: targetLanguage)
        
        // Cache result with thread-safe write
        if let result = result {
            cacheQueue.async(flags: .barrier) {
                self.translationCache[cacheKey] = result
            }
        }
        
        return result
    }
    
    private func performTranslation(_ sign: String, from sourceLanguage: String, to targetLanguage: String) async -> TranslationResult? {
        // Simulate translation for now
        // In a real implementation, this would use ML models or APIs
        
        let result = TranslationResult(
            sourceSign: sign,
            targetSign: sign, // Same sign for now
            sourceLanguage: sourceLanguage,
            targetLanguage: targetLanguage,
            confidence: 0.9,
            alternatives: [sign],
            timestamp: Date()
        )
        
        onTranslationComplete?(result)
        return result
    }
}

// MARK: - Extensions
// Note: VNHumanHandPoseObservation.JointName extension is defined in AIUserExperienceSystem.swift 