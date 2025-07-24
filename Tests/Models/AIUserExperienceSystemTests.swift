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
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful initialization
        XCTAssertNotNil(aiSystem, "AIUserExperienceSystem should be created successfully")
        XCTAssertNotNil(aiSystem.getCurrentLanguage(), "Should have a default language")
        XCTAssertEqual(aiSystem.getCurrentLanguage().code, "ASL", "Should default to ASL")
    }
    
    func testSuccessfulLanguageDiscovery() {
        // Test successful language discovery
        let languages = aiSystem.getSupportedLanguages()
        XCTAssertGreaterThan(languages.count, 0, "Should have supported languages")
        
        // Check for specific languages
        let aslLanguage = languages.first { $0.code == "ASL" }
        XCTAssertNotNil(aslLanguage, "Should support ASL")
        XCTAssertEqual(aslLanguage?.name, "American Sign Language", "Should have correct ASL name")
        XCTAssertEqual(aslLanguage?.flag, "🇺🇸", "Should have correct ASL flag")
    }
    
    func testSuccessfulLanguageChange() {
        // Test successful language change
        let originalLanguage = aiSystem.getCurrentLanguage()
        
        aiSystem.changeLanguage(to: "BSL")
        let newLanguage = aiSystem.getCurrentLanguage()
        
        XCTAssertEqual(newLanguage.code, "BSL", "Should change to BSL")
        XCTAssertEqual(newLanguage.name, "British Sign Language", "Should have correct BSL name")
        XCTAssertEqual(newLanguage.flag, "🇬🇧", "Should have correct BSL flag")
        
        // Change back
        aiSystem.changeLanguage(to: originalLanguage.code)
    }
    
    func testSuccessfulRecognitionStartStop() {
        // Test successful recognition start/stop
        XCTAssertFalse(aiSystem.isRecognizing, "Should start with recognition off")
        
        aiSystem.startRecognition()
        XCTAssertTrue(aiSystem.isRecognizing, "Should start recognition")
        
        aiSystem.stopRecognition()
        XCTAssertFalse(aiSystem.isRecognizing, "Should stop recognition")
    }
    
    func testSuccessfulSignRecognition() {
        // Test successful sign recognition
        let expectation = XCTestExpectation(description: "Sign recognition callback")
        
        aiSystem.onSignRecognized = { result in
            XCTAssertNotNil(result, "Should receive recognition result")
            XCTAssertNotNil(result.sign, "Should have recognized sign")
            XCTAssertGreaterThan(result.confidence, 0.0, "Should have confidence score")
            XCTAssertLessThanOrEqual(result.confidence, 1.0, "Confidence should be normalized")
            XCTAssertEqual(result.language.code, self.aiSystem.getCurrentLanguage().code, "Should match current language")
            expectation.fulfill()
        }
        
        aiSystem.startRecognition()
        
        // Simulate frame processing (this would normally come from camera)
        // For testing, we'll just wait a bit and then stop
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            self.aiSystem.stopRecognition()
        }
        
        wait(for: [expectation], timeout: 2.0)
    }
    
    func testSuccessfulMultipleLanguageSupport() {
        // Test support for multiple languages
        let languages = aiSystem.getSupportedLanguages()
        let supportedCodes = ["ASL", "BSL", "ISL", "JSL", "KSL"]
        
        for code in supportedCodes {
            let language = languages.first { $0.code == code }
            XCTAssertNotNil(language, "Should support \(code)")
            XCTAssertNotNil(language?.name, "Should have name for \(code)")
            XCTAssertNotNil(language?.flag, "Should have flag for \(code)")
            XCTAssertNotNil(language?.modelName, "Should have model for \(code)")
        }
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testInvalidLanguageChange() {
        // Test handling of invalid language code
        let originalLanguage = aiSystem.getCurrentLanguage()
        
        aiSystem.changeLanguage(to: "INVALID")
        let currentLanguage = aiSystem.getCurrentLanguage()
        
        // Should remain unchanged
        XCTAssertEqual(currentLanguage.code, originalLanguage.code, "Should not change to invalid language")
    }
    
    func testMultipleRecognitionStarts() {
        // Test multiple recognition starts
        aiSystem.startRecognition()
        XCTAssertTrue(aiSystem.isRecognizing, "Should be recognizing after first start")
        
        aiSystem.startRecognition()
        XCTAssertTrue(aiSystem.isRecognizing, "Should still be recognizing after second start")
        
        aiSystem.stopRecognition()
        XCTAssertFalse(aiSystem.isRecognizing, "Should stop after stop")
    }
    
    func testMultipleRecognitionStops() {
        // Test multiple recognition stops
        aiSystem.startRecognition()
        aiSystem.stopRecognition()
        XCTAssertFalse(aiSystem.isRecognizing, "Should stop after first stop")
        
        aiSystem.stopRecognition()
        XCTAssertFalse(aiSystem.isRecognizing, "Should remain stopped after second stop")
    }
    
    func testRecognitionWithoutStarting() {
        // Test recognition without starting
        XCTAssertFalse(aiSystem.isRecognizing, "Should not be recognizing initially")
        
        // This should not crash
        aiSystem.stopRecognition()
        XCTAssertFalse(aiSystem.isRecognizing, "Should remain not recognizing")
    }
    
    // MARK: - Exception/Error Tests
    
    func testExceptionHandlingInLanguageChange() {
        // Test that language change handles exceptions gracefully
        XCTAssertNoThrow(aiSystem.changeLanguage(to: "ASL"), "Should not throw when changing to valid language")
        XCTAssertNoThrow(aiSystem.changeLanguage(to: "INVALID"), "Should not throw when changing to invalid language")
    }
    
    func testExceptionHandlingInRecognition() {
        // Test that recognition methods handle exceptions gracefully
        XCTAssertNoThrow(aiSystem.startRecognition(), "Should not throw when starting recognition")
        XCTAssertNoThrow(aiSystem.stopRecognition(), "Should not throw when stopping recognition")
    }
    
    // MARK: - Performance Tests
    
    func testLanguageChangePerformance() {
        // Test performance of language changes
        measure {
            for _ in 0..<10 {
                aiSystem.changeLanguage(to: "ASL")
                aiSystem.changeLanguage(to: "BSL")
            }
        }
    }
    
    func testRecognitionStartStopPerformance() {
        // Test performance of recognition start/stop cycles
        measure {
            for _ in 0..<50 {
                aiSystem.startRecognition()
                aiSystem.stopRecognition()
            }
        }
    }
    
    func testLanguageDiscoveryPerformance() {
        // Test performance of language discovery
        measure {
            for _ in 0..<100 {
                _ = aiSystem.getSupportedLanguages()
            }
        }
    }
    
    // MARK: - Memory Management Tests
    
    func testMemoryManagement() {
        // Test that AI system doesn't create retain cycles
        weak var weakAISystem: AIUserExperienceSystem?
        
        autoreleasepool {
            let localAISystem = AIUserExperienceSystem.shared
            weakAISystem = localAISystem
            
            // Test various operations
            localAISystem.startRecognition()
            localAISystem.changeLanguage(to: "BSL")
            _ = localAISystem.getSupportedLanguages()
            localAISystem.stopRecognition()
        }
        
        // AI system should be retained as singleton
        XCTAssertNotNil(weakAISystem, "AI system should be retained as singleton")
    }
    
    // MARK: - Integration Tests
    
    func testIntegrationWithVisionFramework() {
        // Test integration with Vision framework
        XCTAssertNotNil(aiSystem, "AI system should be accessible")
        
        // Test that we can access vision-related properties
        // Note: These are private in the actual implementation, so we test through public methods
        aiSystem.startRecognition()
        XCTAssertTrue(aiSystem.isRecognizing, "Should be able to start recognition")
        aiSystem.stopRecognition()
    }
    
    func testIntegrationWithCoreML() {
        // Test integration with Core ML
        XCTAssertNotNil(aiSystem, "AI system should be accessible")
        
        // Test language model loading (simulated)
        let languages = aiSystem.getSupportedLanguages()
        XCTAssertGreaterThan(languages.count, 0, "Should have languages with models")
        
        for language in languages.prefix(3) { // Test first 3 languages
            XCTAssertNotNil(language.modelName, "Should have model name for \(language.code)")
        }
    }
    
    // MARK: - Edge Case Tests
    
    func testEmptyLanguageList() {
        // Test behavior with empty language list
        // This would be an edge case in the actual implementation
        let languages = aiSystem.getSupportedLanguages()
        XCTAssertGreaterThan(languages.count, 0, "Should have at least one language")
    }
    
    func testLanguageWithSpecialCharacters() {
        // Test languages with special characters in names
        let languages = aiSystem.getSupportedLanguages()
        
        // Check for languages with special characters
        let jslLanguage = languages.first { $0.code == "JSL" }
        XCTAssertNotNil(jslLanguage, "Should support JSL")
        XCTAssertNotNil(jslLanguage?.nativeName, "Should have native name")
    }
    
    func testLanguageWithEmojis() {
        // Test languages with emoji flags
        let languages = aiSystem.getSupportedLanguages()
        
        for language in languages {
            XCTAssertNotNil(language.flag, "Should have flag for \(language.code)")
            XCTAssertTrue(language.flag.count > 0, "Flag should not be empty for \(language.code)")
        }
    }
    
    func testConcurrentLanguageChanges() {
        // Test concurrent language changes
        let expectation1 = XCTestExpectation(description: "Language change 1")
        let expectation2 = XCTestExpectation(description: "Language change 2")
        
        DispatchQueue.global(qos: .userInitiated).async {
            self.aiSystem.changeLanguage(to: "ASL")
            expectation1.fulfill()
        }
        
        DispatchQueue.global(qos: .userInitiated).async {
            self.aiSystem.changeLanguage(to: "BSL")
            expectation2.fulfill()
        }
        
        wait(for: [expectation1, expectation2], timeout: 1.0)
        
        // Should end up with one of the languages
        let finalLanguage = aiSystem.getCurrentLanguage()
        XCTAssertTrue(["ASL", "BSL"].contains(finalLanguage.code), "Should end up with ASL or BSL")
    }
    
    func testRecognitionHistoryManagement() {
        // Test recognition history management
        let initialHistory = aiSystem.getRecognitionHistory()
        XCTAssertEqual(initialHistory.count, 0, "Should start with empty history")
        
        // Start recognition to potentially add to history
        aiSystem.startRecognition()
        aiSystem.stopRecognition()
        
        // Clear history
        aiSystem.clearRecognitionHistory()
        let finalHistory = aiSystem.getRecognitionHistory()
        XCTAssertEqual(finalHistory.count, 0, "Should have empty history after clearing")
    }
    
    // MARK: - Callback Tests
    
    func testLanguageChangeCallback() {
        // Test language change callback
        let expectation = XCTestExpectation(description: "Language change callback")
        
        aiSystem.onLanguageChanged = { language in
            XCTAssertEqual(language.code, "BSL", "Should receive BSL in callback")
            expectation.fulfill()
        }
        
        aiSystem.changeLanguage(to: "BSL")
        
        wait(for: [expectation], timeout: 1.0)
    }
    
    func testRecognitionStateChangeCallback() {
        // Test recognition state change callback
        let startExpectation = XCTestExpectation(description: "Recognition start callback")
        let stopExpectation = XCTestExpectation(description: "Recognition stop callback")
        
        aiSystem.onRecognitionStateChanged = { isActive in
            if isActive {
                startExpectation.fulfill()
            } else {
                stopExpectation.fulfill()
            }
        }
        
        aiSystem.startRecognition()
        aiSystem.stopRecognition()
        
        wait(for: [startExpectation, stopExpectation], timeout: 2.0)
    }
} 