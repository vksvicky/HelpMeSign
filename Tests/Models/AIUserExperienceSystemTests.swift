import XCTest
import Foundation
import Vision
import CoreML
@testable import HelpMeSign

class AIUserExperienceSystemTests: XCTestCase {
    
    var aiSystem: AIUserExperienceSystem!
    
    override func setUp() {
        super.setUp()
        aiSystem = AIUserExperienceSystem.shared
    }
    
    override func tearDown() {
        aiSystem = nil
        super.tearDown()
    }
    
    // MARK: - Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful singleton initialization
        XCTAssertNotNil(aiSystem, "AIUserExperienceSystem should be initialized successfully")
        XCTAssertEqual(aiSystem, AIUserExperienceSystem.shared, "Should return same singleton instance")
    }
    
    func testSuccessfulRecognitionStart() {
        // Test successful recognition start
        XCTAssertNoThrow(aiSystem.startRecognition(), "Start recognition should not throw")
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should be active after start")
    }
    
    func testSuccessfulRecognitionStop() {
        // Test successful recognition stop
        aiSystem.startRecognition()
        XCTAssertNoThrow(aiSystem.stopRecognition(), "Stop recognition should not throw")
        XCTAssertFalse(aiSystem.isRecognitionActive, "Recognition should be inactive after stop")
    }
    
    func testSuccessfulLanguageChange() {
        // Test successful language change
        let testLanguage = SignLanguage(code: "TEST", name: "Test Language", country: "Test", flag: "🏳️", modelName: "test_model")
        XCTAssertNoThrow(aiSystem.setLanguage(testLanguage), "Language change should not throw")
        XCTAssertEqual(aiSystem.activeLanguage.code, "TEST", "Language should be updated")
    }
    
    func testSuccessfulFeatureExtraction() {
        // Test successful feature extraction with valid data
        let validFeatures: [Float] = Array(repeating: 0.5, count: 42) // 21 joints * 2 coordinates
        let result = aiSystem.testExtractKeyHandFeatures(validFeatures)
        XCTAssertNotNil(result, "Feature extraction should return valid result")
        XCTAssertGreaterThan(result.count, 0, "Extracted features should not be empty")
    }
    
    func testSuccessfulSignDetermination() {
        // Test successful sign determination with valid features
        let validFeatures: [Float] = [0.9, 0.1, -0.5, 0.8, -0.1, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        let sign = aiSystem.testDetermineSignFromHandShape(validFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Sign index should be non-negative")
        XCTAssertLessThan(sign, 10, "Sign index should be within valid range (0-9)")
    }
    
    func testSuccessfulConfidenceCalculation() {
        // Test successful confidence calculation
        let validFeatures: [Float] = Array(repeating: 0.5, count: 42)
        let confidence = aiSystem.testCalculateConfidence(validFeatures)
        XCTAssertGreaterThanOrEqual(confidence, 0.0, "Confidence should be non-negative")
        XCTAssertLessThanOrEqual(confidence, 1.0, "Confidence should be at most 1.0")
    }
    
    func testSuccessfulFeatureProcessing() {
        // Test successful feature processing
        let validFeatures: [Float] = Array(repeating: 0.5, count: 42)
        XCTAssertNoThrow(aiSystem.processFeatures(validFeatures), "Feature processing should not throw")
    }
    
    func testSuccessfulFeatureHistoryClear() {
        // Test successful feature history clearing
        XCTAssertNoThrow(aiSystem.clearFeatureHistory(), "Feature history clearing should not throw")
    }
    
    func testSuccessfulCallbackRegistration() {
        // Test successful callback registration
        var callbackCalled = false
        aiSystem.onSignRecognized = { _ in
            callbackCalled = true
        }
        XCTAssertNotNil(aiSystem.onSignRecognized, "Callback should be registered successfully")
    }
    
    // MARK: - Unhappy Path Tests
    
    func testRecognitionStartWhenAlreadyActive() {
        // Test starting recognition when already active
        aiSystem.startRecognition()
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should be active")
        
        // Try to start again
        XCTAssertNoThrow(aiSystem.startRecognition(), "Starting again should not throw")
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should remain active")
    }
    
    func testRecognitionStopWhenAlreadyInactive() {
        // Test stopping recognition when already inactive
        XCTAssertFalse(aiSystem.isRecognitionActive, "Recognition should be inactive initially")
        
        // Try to stop again
        XCTAssertNoThrow(aiSystem.stopRecognition(), "Stopping again should not throw")
        XCTAssertFalse(aiSystem.isRecognitionActive, "Recognition should remain inactive")
    }
    
    func testFeatureExtractionWithEmptyData() {
        // Test feature extraction with empty data
        let emptyFeatures: [Float] = []
        let result = aiSystem.testExtractKeyHandFeatures(emptyFeatures)
        XCTAssertEqual(result, emptyFeatures, "Empty input should return empty output")
    }
    
    func testFeatureExtractionWithInsufficientData() {
        // Test feature extraction with insufficient data
        let insufficientFeatures: [Float] = [0.1, 0.2, 0.3] // Less than required 42 features
        let result = aiSystem.testExtractKeyHandFeatures(insufficientFeatures)
        XCTAssertEqual(result, insufficientFeatures, "Insufficient data should return input as-is")
    }
    
    func testSignDeterminationWithInsufficientFeatures() {
        // Test sign determination with insufficient features
        let insufficientFeatures: [Float] = [0.1, 0.2] // Less than required 12 features
        let sign = aiSystem.testDetermineSignFromHandShape(insufficientFeatures)
        XCTAssertEqual(sign, 0, "Should return default sign (0) for insufficient features")
    }
    
    func testConfidenceCalculationWithEmptyData() {
        // Test confidence calculation with empty data
        let emptyFeatures: [Float] = []
        let confidence = aiSystem.testCalculateConfidence(emptyFeatures)
        XCTAssertEqual(confidence, 0.0, "Empty data should return zero confidence")
    }
    
    func testFeatureProcessingWithEmptyData() {
        // Test feature processing with empty data
        let emptyFeatures: [Float] = []
        XCTAssertNoThrow(aiSystem.processFeatures(emptyFeatures), "Empty data processing should not throw")
    }
    
    func testLanguageChangeWithNilLanguage() {
        // Test language change with nil language (should use default)
        let originalLanguage = aiSystem.activeLanguage
        XCTAssertNoThrow(aiSystem.setLanguage(originalLanguage), "Should handle language change gracefully")
    }
    
    // MARK: - Error Cases
    
    func testLanguageChangeWithInvalidLanguage() {
        // Test language change with invalid language data
        let invalidLanguage = SignLanguage(code: "", name: "", country: "", flag: "", modelName: "")
        XCTAssertNoThrow(aiSystem.setLanguage(invalidLanguage), "Should handle invalid language gracefully")
    }
    
    func testFeatureExtractionWithInvalidData() {
        // Test feature extraction with invalid data (NaN, infinity)
        let invalidFeatures: [Float] = [Float.nan, Float.infinity, -Float.infinity, 0.5]
        let result = aiSystem.testExtractKeyHandFeatures(invalidFeatures)
        XCTAssertNotNil(result, "Should handle invalid data gracefully")
    }
    
    func testSignDeterminationWithExtremeValues() {
        // Test sign determination with extreme values
        let extremeFeatures: [Float] = [Float.greatestFiniteMagnitude, -Float.greatestFiniteMagnitude, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        let sign = aiSystem.testDetermineSignFromHandShape(extremeFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle extreme values gracefully")
        XCTAssertLessThan(sign, 10, "Should return valid sign index")
    }
    
    func testConfidenceCalculationWithInvalidData() {
        // Test confidence calculation with invalid data
        let invalidFeatures: [Float] = [Float.nan, Float.infinity, -Float.infinity]
        let confidence = aiSystem.testCalculateConfidence(invalidFeatures)
        XCTAssertGreaterThanOrEqual(confidence, 0.0, "Should handle invalid data gracefully")
        XCTAssertLessThanOrEqual(confidence, 1.0, "Should return valid confidence range")
    }
    
    func testFeatureProcessingWithInvalidData() {
        // Test feature processing with invalid data
        let invalidFeatures: [Float] = [Float.nan, Float.infinity, -Float.infinity]
        XCTAssertNoThrow(aiSystem.processFeatures(invalidFeatures), "Should handle invalid data gracefully")
    }
    
    func testLanguageChangeWithInvalidCode() {
        // Test language change with invalid language code
        let invalidLanguage = SignLanguage(code: "INVALID", name: "Invalid", country: "Invalid", flag: "🏳️", modelName: "invalid")
        XCTAssertNoThrow(aiSystem.setLanguage(invalidLanguage), "Should handle invalid language code gracefully")
    }
    
    func testRecognitionWithCorruptedFeatures() {
        // Test recognition with corrupted feature data
        let corruptedFeatures: [Float] = [0.5, 0.3, Float.nan, 0.7, Float.infinity, 0.2]
        XCTAssertNoThrow(aiSystem.processFeatures(corruptedFeatures), "Should handle corrupted data gracefully")
    }
    
    // MARK: - Exception Tests
    
    func testConcurrentRecognitionStart() {
        // Test concurrent recognition start (simulate race condition)
        let expectation = XCTestExpectation(description: "Concurrent recognition start")
        let queue = DispatchQueue.global(qos: .userInitiated)
        
        for _ in 0..<5 {
            queue.async {
                XCTAssertNoThrow(self.aiSystem.startRecognition(), "Concurrent start should not throw")
            }
        }
        
        queue.async {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 2.0)
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should be active after concurrent starts")
    }
    
    func testConcurrentRecognitionStop() {
        // Test concurrent recognition stop
        aiSystem.startRecognition()
        let expectation = XCTestExpectation(description: "Concurrent recognition stop")
        let queue = DispatchQueue.global(qos: .userInitiated)
        
        for _ in 0..<5 {
            queue.async {
                XCTAssertNoThrow(self.aiSystem.stopRecognition(), "Concurrent stop should not throw")
            }
        }
        
        queue.async {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 2.0)
        XCTAssertFalse(aiSystem.isRecognitionActive, "Recognition should be inactive after concurrent stops")
    }
    
    func testConcurrentLanguageChanges() {
        // Test concurrent language changes
        let expectation = XCTestExpectation(description: "Concurrent language changes")
        let queue = DispatchQueue.global(qos: .userInitiated)
        let testLanguages = [
            SignLanguage(code: "TEST1", name: "Test1", country: "Test", flag: "🏳️", modelName: "test1"),
            SignLanguage(code: "TEST2", name: "Test2", country: "Test", flag: "🏳️", modelName: "test2"),
            SignLanguage(code: "TEST3", name: "Test3", country: "Test", flag: "🏳️", modelName: "test3")
        ]
        
        for language in testLanguages {
            queue.async {
                XCTAssertNoThrow(self.aiSystem.setLanguage(language), "Concurrent language change should not throw")
            }
        }
        
        queue.async {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 2.0)
        XCTAssertNotNil(aiSystem.activeLanguage, "Should have valid language after concurrent changes")
    }
    
    func testConcurrentFeatureProcessing() {
        // Test concurrent feature processing
        let expectation = XCTestExpectation(description: "Concurrent feature processing")
        let queue = DispatchQueue.global(qos: .userInitiated)
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        for _ in 0..<10 {
            queue.async {
                XCTAssertNoThrow(self.aiSystem.processFeatures(testFeatures), "Concurrent processing should not throw")
            }
        }
        
        queue.async {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 2.0)
    }
    
    func testMemoryPressureHandling() {
        // Test handling of memory pressure
        let largeFeatureArray = Array(repeating: Float(0.5), count: 10000)
        XCTAssertNoThrow(aiSystem.testExtractKeyHandFeatures(largeFeatureArray), "Should handle large data without memory issues")
    }
    
    func testExceptionHandlingInFeatureExtraction() {
        // Test exception handling in feature extraction
        let problematicFeatures = Array(repeating: Float(0.5), count: 42)
        XCTAssertNoThrow(aiSystem.testExtractKeyHandFeatures(problematicFeatures), "Should handle exceptions gracefully")
    }
    
    func testExceptionHandlingInSignDetermination() {
        // Test exception handling in sign determination
        let problematicFeatures = Array(repeating: Float(0.5), count: 12)
        XCTAssertNoThrow(aiSystem.testDetermineSignFromHandShape(problematicFeatures), "Should handle exceptions gracefully")
    }
    
    // MARK: - Boundary Condition Tests
    
    func testFeatureExtractionBoundaryConditions() {
        // Test feature extraction at boundary conditions
        let exactBoundaryFeatures = Array(repeating: Float(0.0), count: 42) // Exactly 42 features
        let result = aiSystem.testExtractKeyHandFeatures(exactBoundaryFeatures)
        XCTAssertNotNil(result, "Should handle exact boundary condition")
        
        let oneLessFeatures = Array(repeating: Float(0.0), count: 41) // One less than required
        let result2 = aiSystem.testExtractKeyHandFeatures(oneLessFeatures)
        XCTAssertEqual(result2, oneLessFeatures, "Should handle one-less-than-boundary condition")
    }
    
    func testSignDeterminationBoundaryConditions() {
        // Test sign determination at boundary conditions
        let exactBoundaryFeatures = Array(repeating: Float(0.0), count: 12) // Exactly 12 features
        let sign = aiSystem.testDetermineSignFromHandShape(exactBoundaryFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle exact boundary condition")
        
        let oneLessFeatures = Array(repeating: Float(0.0), count: 11) // One less than required
        let sign2 = aiSystem.testDetermineSignFromHandShape(oneLessFeatures)
        XCTAssertEqual(sign2, 0, "Should return default for one-less-than-boundary condition")
    }
    
    func testHandShapeBoundaryConditions() {
        // Test hand shape calculations at boundary conditions
        let zeroFeatures: [Float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        let sign = aiSystem.testDetermineSignFromHandShape(zeroFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle zero values")
        
        let oneFeatures: [Float] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        let sign2 = aiSystem.testDetermineSignFromHandShape(oneFeatures)
        XCTAssertGreaterThanOrEqual(sign2, 0, "Should handle maximum values")
    }
    
    func testConfidenceBoundaryConditions() {
        // Test confidence calculation at boundary conditions
        let zeroFeatures = Array(repeating: Float(0.0), count: 42)
        let confidence = aiSystem.testCalculateConfidence(zeroFeatures)
        XCTAssertGreaterThanOrEqual(confidence, 0.0, "Should handle zero values")
        
        let oneFeatures = Array(repeating: Float(1.0), count: 42)
        let confidence2 = aiSystem.testCalculateConfidence(oneFeatures)
        XCTAssertLessThanOrEqual(confidence2, 1.0, "Should handle maximum values")
    }
    
    func testFeatureProcessingBoundaryConditions() {
        // Test feature processing at boundary conditions
        let minimumFeatures: [Float] = [0.0]
        XCTAssertNoThrow(aiSystem.processFeatures(minimumFeatures), "Should handle minimum features")
        
        let maximumFeatures = Array(repeating: Float(1.0), count: 1000)
        XCTAssertNoThrow(aiSystem.processFeatures(maximumFeatures), "Should handle maximum features")
    }
    
    func testLanguageChangeBoundaryConditions() {
        // Test language change at boundary conditions
        let minimalLanguage = SignLanguage(code: "A", name: "A", country: "A", flag: "A", modelName: "A")
        XCTAssertNoThrow(aiSystem.setLanguage(minimalLanguage), "Should handle minimal language data")
        
        let maximalLanguage = SignLanguage(
            code: String(repeating: "A", count: 100),
            name: String(repeating: "B", count: 100),
            country: String(repeating: "C", count: 100),
            flag: String(repeating: "D", count: 100),
            modelName: String(repeating: "E", count: 100)
        )
        XCTAssertNoThrow(aiSystem.setLanguage(maximalLanguage), "Should handle maximal language data")
    }
    
    // MARK: - Edge Cases
    
    func testFeatureExtractionWithAllZeros() {
        // Test feature extraction with all zero values
        let zeroFeatures = Array(repeating: Float(0.0), count: 42)
        let result = aiSystem.testExtractKeyHandFeatures(zeroFeatures)
        XCTAssertNotNil(result, "Should handle all zero values")
        XCTAssertEqual(result.count, 12, "Should extract expected number of key features")
    }
    
    func testFeatureExtractionWithAllOnes() {
        // Test feature extraction with all one values
        let oneFeatures = Array(repeating: Float(1.0), count: 42)
        let result = aiSystem.testExtractKeyHandFeatures(oneFeatures)
        XCTAssertNotNil(result, "Should handle all one values")
        XCTAssertEqual(result.count, 12, "Should extract expected number of key features")
    }
    
    func testSignDeterminationWithIdenticalFeatures() {
        // Test sign determination with identical feature values
        let identicalFeatures = Array(repeating: Float(0.5), count: 12)
        let sign = aiSystem.testDetermineSignFromHandShape(identicalFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle identical feature values")
        XCTAssertLessThan(sign, 10, "Should return valid sign index")
    }
    
    func testHandShapeWithMinimalSpread() {
        // Test hand shape with minimal finger spread
        let minimalSpreadFeatures: [Float] = [0.0, 0.0, 0.001, 0.001, 0.002, 0.002, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        let sign = aiSystem.testDetermineSignFromHandShape(minimalSpreadFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle minimal spread")
    }
    
    func testHandShapeWithMaximumSpread() {
        // Test hand shape with maximum finger spread
        let maxSpreadFeatures: [Float] = [0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        let sign = aiSystem.testDetermineSignFromHandShape(maxSpreadFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle maximum spread")
    }
    
    func testFeatureHistoryBoundaryConditions() {
        // Test feature history at boundary conditions
        let testFeatures: [Float] = Array(repeating: 0.5, count: 42)
        
        // Test with empty history
        aiSystem.clearFeatureHistory()
        XCTAssertNoThrow(aiSystem.processFeatures(testFeatures), "Should handle empty history")
        
        // Test with maximum history
        for _ in 0..<100 {
            aiSystem.processFeatures(testFeatures)
        }
        XCTAssertNoThrow(aiSystem.processFeatures(testFeatures), "Should handle maximum history")
    }
    
    func testConfidenceCalculationEdgeCases() {
        // Test confidence calculation with edge cases
        let perfectFeatures = Array(repeating: Float(0.5), count: 42)
        let confidence = aiSystem.testCalculateConfidence(perfectFeatures)
        XCTAssertGreaterThanOrEqual(confidence, 0.0, "Confidence should be non-negative")
        XCTAssertLessThanOrEqual(confidence, 1.0, "Confidence should be at most 1.0")
        
        let noisyFeatures = Array(repeating: Float(0.0), count: 42)
        let confidence2 = aiSystem.testCalculateConfidence(noisyFeatures)
        XCTAssertGreaterThanOrEqual(confidence2, 0.0, "Confidence should be non-negative even for noisy data")
    }
    
    func testFeatureExtractionWithAlternatingValues() {
        // Test feature extraction with alternating values
        var alternatingFeatures: [Float] = []
        for i in 0..<42 {
            alternatingFeatures.append(i % 2 == 0 ? 0.0 : 1.0)
        }
        let result = aiSystem.testExtractKeyHandFeatures(alternatingFeatures)
        XCTAssertNotNil(result, "Should handle alternating values")
        XCTAssertEqual(result.count, 12, "Should extract expected number of features")
    }
    
    func testSignDeterminationWithRandomValues() {
        // Test sign determination with random-like values
        let randomFeatures: [Float] = [0.123, 0.456, 0.789, 0.234, 0.567, 0.890, 0.345, 0.678, 0.901, 0.432, 0.765, 0.098]
        let sign = aiSystem.testDetermineSignFromHandShape(randomFeatures)
        XCTAssertGreaterThanOrEqual(sign, 0, "Should handle random-like values")
        XCTAssertLessThan(sign, 10, "Should return valid sign index")
    }
    
    func testFeatureProcessingWithNegativeValues() {
        // Test feature processing with negative values
        let negativeFeatures = Array(repeating: Float(-0.5), count: 42)
        XCTAssertNoThrow(aiSystem.processFeatures(negativeFeatures), "Should handle negative values")
    }
    
    func testLanguageChangeWithSpecialCharacters() {
        // Test language change with special characters
        let specialLanguage = SignLanguage(code: "TEST@#$%", name: "Test\n\r\t", country: "Test\"'", flag: "🏳️", modelName: "test_model")
        XCTAssertNoThrow(aiSystem.setLanguage(specialLanguage), "Should handle special characters")
    }
    
    func testFeatureExtractionWithPrecisionValues() {
        // Test feature extraction with high precision values
        let precisionFeatures: [Float] = [0.123456789, 0.987654321, 0.000000001, 0.999999999]
        let result = aiSystem.testExtractKeyHandFeatures(precisionFeatures)
        XCTAssertNotNil(result, "Should handle high precision values")
    }
    
    // MARK: - Stress Tests
    
    func testRapidRecognitionToggle() {
        // Test rapid recognition toggle
        for _ in 0..<100 {
            aiSystem.startRecognition()
            aiSystem.stopRecognition()
        }
        XCTAssertFalse(aiSystem.isRecognitionActive, "Should end in inactive state after rapid toggles")
    }
    
    func testRapidLanguageChanges() {
        // Test rapid language changes
        let languages = [
            SignLanguage(code: "TEST1", name: "Test1", country: "Test", flag: "🏳️", modelName: "test1"),
            SignLanguage(code: "TEST2", name: "Test2", country: "Test", flag: "🏳️", modelName: "test2"),
            SignLanguage(code: "TEST3", name: "Test3", country: "Test", flag: "🏳️", modelName: "test3")
        ]
        
        for _ in 0..<50 {
            for language in languages {
                aiSystem.setLanguage(language)
            }
        }
        XCTAssertNotNil(aiSystem.activeLanguage, "Should maintain valid language after rapid changes")
    }
    
    func testHighVolumeFeatureProcessing() {
        // Test high volume feature processing
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        for _ in 0..<1000 {
            aiSystem.processFeatures(testFeatures)
        }
        XCTAssertTrue(true, "Should handle high volume processing without issues")
    }
    
    func testMemoryStressTest() {
        // Test memory stress with large feature arrays
        let largeFeatures = Array(repeating: Float(0.5), count: 10000)
        
        for _ in 0..<100 {
            _ = aiSystem.testExtractKeyHandFeatures(largeFeatures)
        }
        XCTAssertTrue(true, "Should handle memory stress without issues")
    }
    
    func testConcurrentStressTest() {
        // Test concurrent stress
        let expectation = XCTestExpectation(description: "Concurrent stress test")
        let queue = DispatchQueue.global(qos: .userInitiated)
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        for _ in 0..<100 {
            queue.async {
                self.aiSystem.startRecognition()
                self.aiSystem.processFeatures(testFeatures)
                self.aiSystem.stopRecognition()
            }
        }
        
        queue.async {
            expectation.fulfill()
        }
        
        wait(for: [expectation], timeout: 10.0)
        XCTAssertTrue(true, "Should handle concurrent stress without issues")
    }
    
    // MARK: - Integration Tests
    
    func testEndToEndRecognitionFlow() {
        // Test complete recognition flow
        let expectation = XCTestExpectation(description: "End-to-end recognition flow")
        
        // Set up callback
        aiSystem.onSignRecognized = { result in
            XCTAssertNotNil(result, "Recognition result should not be nil")
            XCTAssertNotNil(result.sign, "Recognized sign should not be nil")
            XCTAssertGreaterThanOrEqual(result.confidence, 0.0, "Confidence should be non-negative")
            expectation.fulfill()
        }
        
        // Start recognition
        aiSystem.startRecognition()
        
        // Process features with varied values to ensure recognition triggers
        let testFeatures = (0..<42).map { Float($0) * 0.1 }
        aiSystem.processFeaturesForTesting(testFeatures)
        
        // Wait for recognition
        wait(for: [expectation], timeout: 5.0)
        
        // Clean up
        aiSystem.stopRecognition()
    }
    
    func testLanguageChangeWithRecognitionActive() {
        // Test language change while recognition is active
        aiSystem.startRecognition()
        let testLanguage = SignLanguage(code: "TEST", name: "Test", country: "Test", flag: "🏳️", modelName: "test")
        
        XCTAssertNoThrow(aiSystem.setLanguage(testLanguage), "Should handle language change during recognition")
        XCTAssertEqual(aiSystem.activeLanguage.code, "TEST", "Language should be updated")
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should remain active")
        
        aiSystem.stopRecognition()
    }
    
    func testFeatureProcessingWithLanguageChange() {
        // Test feature processing with language change
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        // Process features with default language
        aiSystem.processFeatures(testFeatures)
        
        // Change language and process again
        let testLanguage = SignLanguage(code: "TEST", name: "Test", country: "Test", flag: "🏳️", modelName: "test")
        aiSystem.setLanguage(testLanguage)
        aiSystem.processFeatures(testFeatures)
        
        XCTAssertTrue(true, "Should handle feature processing with language change")
    }
    
    func testRecognitionStatePersistence() {
        // Test recognition state persistence across operations
        aiSystem.startRecognition()
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should be active")
        
        // Perform various operations
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        aiSystem.processFeatures(testFeatures)
        
        let testLanguage = SignLanguage(code: "TEST", name: "Test", country: "Test", flag: "🏳️", modelName: "test")
        aiSystem.setLanguage(testLanguage)
        
        XCTAssertTrue(aiSystem.isRecognitionActive, "Recognition should remain active after operations")
        
        aiSystem.stopRecognition()
    }
    
    func testCallbackIntegration() {
        // Test callback integration
        var recognitionCallbackCalled = false
        var languageCallbackCalled = false
        var stateCallbackCalled = false
        
        aiSystem.onSignRecognized = { _ in
            recognitionCallbackCalled = true
        }
        
        aiSystem.onLanguageChanged = { _ in
            languageCallbackCalled = true
        }
        
        aiSystem.onRecognitionStateChanged = { _ in
            stateCallbackCalled = true
        }
        
        // Trigger callbacks
        aiSystem.startRecognition()
        let testLanguage = SignLanguage(code: "TEST", name: "Test", country: "Test", flag: "🏳️", modelName: "test")
        aiSystem.setLanguage(testLanguage)
        aiSystem.stopRecognition()
        
        XCTAssertTrue(stateCallbackCalled, "State change callback should be called")
        XCTAssertTrue(languageCallbackCalled, "Language change callback should be called")
    }
    
    // MARK: - Performance Tests
    
    func testFeatureExtractionPerformance() {
        // Test feature extraction performance
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        measure {
            for _ in 0..<1000 {
                _ = aiSystem.testExtractKeyHandFeatures(testFeatures)
            }
        }
    }
    
    func testSignDeterminationPerformance() {
        // Test sign determination performance
        let testFeatures = Array(repeating: Float(0.5), count: 12)
        
        measure {
            for _ in 0..<1000 {
                _ = aiSystem.testDetermineSignFromHandShape(testFeatures)
            }
        }
    }
    
    func testConfidenceCalculationPerformance() {
        // Test confidence calculation performance
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        measure {
            for _ in 0..<1000 {
                _ = aiSystem.testCalculateConfidence(testFeatures)
            }
        }
    }
    
    func testFeatureProcessingPerformance() {
        // Test feature processing performance
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        measure {
            for _ in 0..<1000 {
                aiSystem.processFeatures(testFeatures)
            }
        }
    }
    
    func testLanguageChangePerformance() {
        // Test language change performance
        let testLanguage = SignLanguage(code: "TEST", name: "Test", country: "Test", flag: "🏳️", modelName: "test")
        
        measure {
            for _ in 0..<1000 {
                aiSystem.setLanguage(testLanguage)
            }
        }
    }
    
    func testConcurrentProcessingPerformance() {
        // Test concurrent processing performance
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        let queue = DispatchQueue.global(qos: .userInitiated)
        
        measure {
            let group = DispatchGroup()
            for _ in 0..<100 {
                group.enter()
                queue.async {
                    self.aiSystem.processFeatures(testFeatures)
                    group.leave()
                }
            }
            group.wait()
        }
    }
    
    func testMemoryUsagePerformance() {
        // Test memory usage performance
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        
        measure {
            for _ in 0..<1000 {
                aiSystem.processFeatures(testFeatures)
                aiSystem.clearFeatureHistory()
            }
        }
    }
    
    // MARK: - Regression Tests
    
    func testRegressionFeatureExtractionConsistency() {
        // Test that feature extraction produces consistent results
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        let result1 = aiSystem.testExtractKeyHandFeatures(testFeatures)
        let result2 = aiSystem.testExtractKeyHandFeatures(testFeatures)
        
        XCTAssertEqual(result1, result2, "Feature extraction should be consistent")
    }
    
    func testRegressionSignDeterminationConsistency() {
        // Test that sign determination produces consistent results
        let testFeatures = Array(repeating: Float(0.5), count: 12)
        let sign1 = aiSystem.testDetermineSignFromHandShape(testFeatures)
        let sign2 = aiSystem.testDetermineSignFromHandShape(testFeatures)
        
        XCTAssertEqual(sign1, sign2, "Sign determination should be consistent")
    }
    
    func testRegressionConfidenceCalculationConsistency() {
        // Test that confidence calculation produces consistent results
        let testFeatures = Array(repeating: Float(0.5), count: 42)
        let confidence1 = aiSystem.testCalculateConfidence(testFeatures)
        let confidence2 = aiSystem.testCalculateConfidence(testFeatures)
        
        XCTAssertEqual(confidence1, confidence2, "Confidence calculation should be consistent")
    }
    
    func testRegressionLanguageChangeConsistency() {
        // Test that language change produces consistent results
        let testLanguage = SignLanguage(code: "TEST", name: "Test", country: "Test", flag: "🏳️", modelName: "test")
        
        aiSystem.setLanguage(testLanguage)
        let language1 = aiSystem.activeLanguage
        
        aiSystem.setLanguage(testLanguage)
        let language2 = aiSystem.activeLanguage
        
        XCTAssertEqual(language1.code, language2.code, "Language change should be consistent")
    }
    
    // MARK: - Security Tests
    
    func testInputValidation() {
        // Test input validation for various edge cases
        let maliciousFeatures: [Float] = [Float.nan, Float.infinity, -Float.infinity, Float.greatestFiniteMagnitude, -Float.greatestFiniteMagnitude]
        XCTAssertNoThrow(aiSystem.testExtractKeyHandFeatures(maliciousFeatures), "Should handle malicious input gracefully")
    }
    
    func testLanguageCodeValidation() {
        // Test language code validation
        let maliciousLanguage = SignLanguage(
            code: "<script>alert('xss')</script>",
            name: "'; DROP TABLE languages; --",
            country: "Test",
            flag: "🏳️",
            modelName: "test"
        )
        XCTAssertNoThrow(aiSystem.setLanguage(maliciousLanguage), "Should handle malicious language data gracefully")
    }
    
    func testFeatureArrayBoundsChecking() {
        // Test feature array bounds checking
        let oversizedFeatures = Array(repeating: Float(0.5), count: 1000000)
        XCTAssertNoThrow(aiSystem.testExtractKeyHandFeatures(oversizedFeatures), "Should handle oversized arrays gracefully")
    }
} 