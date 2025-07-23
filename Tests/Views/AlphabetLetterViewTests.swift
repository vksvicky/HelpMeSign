import XCTest
import Cocoa
@testable import HelpMeSign

class AlphabetLetterViewTests: XCTestCase {
    var testSvgString: String?
    
    override func setUp() {
        super.setUp()
        // Create a simple test SVG string
        testSvgString = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <symbol id="A">
                <circle cx="50" cy="50" r="20" fill="blue"/>
            </symbol>
        </svg>
        """
    }
    
    override func tearDown() {
        testSvgString = nil
        super.tearDown()
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful initialization with valid parameters
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letter = "A"
        let letterView = AlphabetLetterView(frame: frame, letter: letter, svgString: testSvgString)
        
        XCTAssertEqual(letterView.letter, "A", "Letter should be set correctly")
        XCTAssertEqual(letterView.frame, frame, "Frame should be set correctly")
        XCTAssertNotNil(letterView.svgString, "SVG string should be set")
        XCTAssertNotNil(letterView.label, "Label should be created")
        XCTAssertFalse(letterView.isHovered, "Should not be hovered initially")
        XCTAssertGreaterThan(letterView.instanceId, 0, "Instance ID should be assigned")
    }
    
    func testSuccessfulLabelCreation() {
        // Test that label is created with correct properties
        let frame = NSRect(x: 0, y: 0, width: 60, height: 60)
        let letter = "B"
        let letterView = AlphabetLetterView(frame: frame, letter: letter, svgString: nil)
        
        XCTAssertEqual(letterView.label.stringValue, "B", "Label should display the letter")
        XCTAssertEqual(letterView.label.alignment, .center, "Label should be center aligned")
        XCTAssertEqual(letterView.label.textColor, NSColor.labelColor, "Label should use system label color")
    }
    
    func testSuccessfulLayerConfiguration() {
        // Test that layer properties are set correctly
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "C", svgString: nil)
        
        XCTAssertTrue(letterView.wantsLayer, "View should want layer")
        XCTAssertNotNil(letterView.layer, "Layer should be created")
        XCTAssertEqual(letterView.layer?.cornerRadius, 6, "Corner radius should be set")
        XCTAssertEqual(letterView.layer?.borderWidth, 0.5, "Border width should be set")
        XCTAssertNotNil(letterView.layer?.shadowColor, "Shadow should be configured")
    }
    
    func testSuccessfulFontSizeCalculation() {
        // Test font size calculation for different frame sizes
        let smallFrame = NSRect(x: 0, y: 0, width: 40, height: 40)
        let largeFrame = NSRect(x: 0, y: 0, width: 80, height: 80)
        
        let smallView = AlphabetLetterView(frame: smallFrame, letter: "D", svgString: nil)
        let largeView = AlphabetLetterView(frame: largeFrame, letter: "E", svgString: nil)
        
        // Font sizes should be different based on frame size
        XCTAssertNotEqual(smallView.label.font?.pointSize ?? 0, largeView.label.font?.pointSize ?? 0, "Font sizes should differ based on frame size")
    }
    
    func testSuccessfulInstanceIdIncrement() {
        // Test that instance IDs are incremented correctly
        let initialCount = AlphabetLetterView.instanceCount
        
        let view1 = AlphabetLetterView(frame: NSRect(x: 0, y: 0, width: 50, height: 50), letter: "F", svgString: nil)
        let view2 = AlphabetLetterView(frame: NSRect(x: 0, y: 0, width: 50, height: 50), letter: "G", svgString: nil)
        
        XCTAssertEqual(view1.instanceId, initialCount + 1, "First view should have incremented instance ID")
        XCTAssertEqual(view2.instanceId, initialCount + 2, "Second view should have incremented instance ID")
        XCTAssertEqual(AlphabetLetterView.instanceCount, initialCount + 2, "Static count should be updated")
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testInitializationWithEmptyLetter() {
        // Test initialization with empty letter string
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "", svgString: nil)
        
        XCTAssertEqual(letterView.letter, "", "Empty letter should be handled")
        XCTAssertEqual(letterView.label.stringValue, "", "Label should show empty string")
    }
    
    func testInitializationWithNilSVGString() {
        // Test initialization with nil SVG string
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "H", svgString: nil)
        
        XCTAssertNil(letterView.svgString, "SVG string should be nil")
        XCTAssertNotNil(letterView.label, "Label should still be created as fallback")
    }
    
    func testInitializationWithZeroFrame() {
        // Test initialization with zero-sized frame
        let zeroFrame = NSRect(x: 0, y: 0, width: 0, height: 0)
        let letterView = AlphabetLetterView(frame: zeroFrame, letter: "I", svgString: nil)
        
        XCTAssertEqual(letterView.frame, zeroFrame, "Zero frame should be accepted")
        XCTAssertNotNil(letterView.label, "Label should still be created")
    }
    
    func testInitializationWithNegativeFrame() {
        // Test initialization with negative frame dimensions
        let negativeFrame = NSRect(x: -10, y: -10, width: -20, height: -20)
        let letterView = AlphabetLetterView(frame: negativeFrame, letter: "J", svgString: nil)
        
        XCTAssertEqual(letterView.frame, negativeFrame, "Negative frame should be accepted")
        XCTAssertNotNil(letterView.label, "Label should still be created")
    }
    
    func testInitializationWithVeryLargeFrame() {
        // Test initialization with very large frame
        let largeFrame = NSRect(x: 0, y: 0, width: 1000, height: 1000)
        let letterView = AlphabetLetterView(frame: largeFrame, letter: "K", svgString: nil)
        
        XCTAssertEqual(letterView.frame, largeFrame, "Large frame should be accepted")
        XCTAssertNotNil(letterView.label, "Label should still be created")
    }
    
    // MARK: - Exception/Error Handling Tests
    
    func testInitializationWithSpecialCharacters() {
        // Test initialization with special characters in letter
        let specialChars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "="]
        
        for char in specialChars {
            let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
            let letterView = AlphabetLetterView(frame: frame, letter: char, svgString: nil)
            
            XCTAssertEqual(letterView.letter, char, "Special character '\(char)' should be handled")
            XCTAssertEqual(letterView.label.stringValue, char, "Label should display special character '\(char)'")
        }
    }
    
    func testInitializationWithUnicodeCharacters() {
        // Test initialization with Unicode characters
        let unicodeChars = ["α", "β", "γ", "δ", "ε", "ñ", "ç", "ü", "é", "à"]
        
        for char in unicodeChars {
            let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
            let letterView = AlphabetLetterView(frame: frame, letter: char, svgString: nil)
            
            XCTAssertEqual(letterView.letter, char, "Unicode character '\(char)' should be handled")
            XCTAssertEqual(letterView.label.stringValue, char, "Label should display Unicode character '\(char)'")
        }
    }
    
    func testInitializationWithLongString() {
        // Test initialization with very long letter string
        let longString = String(repeating: "A", count: 100)
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: longString, svgString: nil)
        
        XCTAssertEqual(letterView.letter, longString, "Long string should be handled")
        XCTAssertEqual(letterView.label.stringValue, longString, "Label should display long string")
    }
    
    func testInitializationWithWhitespaceOnly() {
        // Test initialization with whitespace-only string
        let whitespaceString = "   \t\n   "
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: whitespaceString, svgString: nil)
        
        XCTAssertEqual(letterView.letter, whitespaceString, "Whitespace string should be handled")
        XCTAssertEqual(letterView.label.stringValue, whitespaceString, "Label should display whitespace string")
    }
    
    // MARK: - Edge Case Tests
    
    func testHoverStateChanges() {
        // Test hover state changes
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "L", svgString: nil)
        
        XCTAssertFalse(letterView.isHovered, "Should not be hovered initially")
        
        // Simulate mouse enter
        letterView.mouseEntered(with: NSEvent())
        XCTAssertTrue(letterView.isHovered, "Should be hovered after mouse enter")
        
        // Simulate mouse exit
        letterView.mouseExited(with: NSEvent())
        XCTAssertFalse(letterView.isHovered, "Should not be hovered after mouse exit")
    }
    
    func testAnimationWithoutSVGString() {
        // Test animation behavior when no SVG string is provided
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "M", svgString: nil)
        
        // Should not crash when animating without SVG
        XCTAssertNoThrow(letterView.mouseEntered(with: NSEvent()), "Should not crash on hover without SVG")
        XCTAssertNoThrow(letterView.mouseExited(with: NSEvent()), "Should not crash on exit without SVG")
    }
    
    func testAnimationWithSVGString() {
        // Test animation behavior when SVG string is provided
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "N", svgString: testSvgString)
        
        // Should not crash when animating with SVG
        XCTAssertNoThrow(letterView.mouseEntered(with: NSEvent()), "Should not crash on hover with SVG")
        XCTAssertNoThrow(letterView.mouseExited(with: NSEvent()), "Should not crash on exit with SVG")
    }
    
    // MARK: - Performance Tests
    
    func testPerformanceOfMultipleInitializations() {
        // Test performance of creating multiple views
        measure {
            for i in 0..<100 {
                let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
                let letter = String(UnicodeScalar(65 + (i % 26))!) // A-Z
                let _ = AlphabetLetterView(frame: frame, letter: letter, svgString: nil)
            }
        }
    }
    
    func testPerformanceOfHoverAnimations() {
        // Test performance of hover animations
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "O", svgString: nil)
        
        measure {
            for _ in 0..<1000 {
                letterView.mouseEntered(with: NSEvent())
                letterView.mouseExited(with: NSEvent())
            }
        }
    }
    
    // MARK: - Memory Tests
    
    func testMemoryUsageWithLargeNumberOfViews() {
        // Test memory usage with many views
        var views: [AlphabetLetterView] = []
        
        for i in 0..<1000 {
            let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
            let letter = String(UnicodeScalar(65 + (i % 26))!) // A-Z
            let view = AlphabetLetterView(frame: frame, letter: letter, svgString: nil)
            views.append(view)
        }
        
        XCTAssertEqual(views.count, 1000, "Should create 1000 views")
        XCTAssertGreaterThan(AlphabetLetterView.instanceCount, 1000, "Instance count should reflect all created views")
    }
    
    func testMemoryCleanup() {
        // Test that views are properly cleaned up
        let initialCount = AlphabetLetterView.instanceCount
        
        autoreleasepool {
            for i in 0..<100 {
                let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
                let letter = String(UnicodeScalar(65 + (i % 26))!) // A-Z
                let _ = AlphabetLetterView(frame: frame, letter: letter, svgString: nil)
            }
        }
        
        // Instance count should not be affected by cleanup since it's static
        XCTAssertGreaterThanOrEqual(AlphabetLetterView.instanceCount, initialCount, "Instance count should not decrease after cleanup")
    }
    
    // MARK: - Integration Tests
    
    func testIntegrationWithParentView() {
        // Test integration with a parent view
        let parentView = NSView(frame: NSRect(x: 0, y: 0, width: 200, height: 200))
        let letterView = AlphabetLetterView(frame: NSRect(x: 10, y: 10, width: 50, height: 50), letter: "P", svgString: nil)
        
        parentView.addSubview(letterView)
        
        XCTAssertTrue(parentView.subviews.contains(letterView), "Letter view should be added to parent")
        XCTAssertEqual(letterView.superview, parentView, "Parent view should be set correctly")
    }
    
    func testIntegrationWithWindow() {
        // Test integration with a window
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 300, height: 300), styleMask: [.titled], backing: .buffered, defer: false)
        let letterView = AlphabetLetterView(frame: NSRect(x: 10, y: 10, width: 50, height: 50), letter: "Q", svgString: nil)
        
        window.contentView?.addSubview(letterView)
        
        XCTAssertNotNil(window.contentView, "Window should have content view")
        XCTAssertTrue(window.contentView?.subviews.contains(letterView) ?? false, "Letter view should be added to window")
    }
    

    
    // MARK: - Debug Tests
    
    func testDebugIndexAssignment() {
        // Test debug index assignment
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "S", svgString: nil)
        
        // Debug index is optional and may not be set in tests
        // Just verify the property exists and can be set
        letterView.debugIndex = 42
        XCTAssertEqual(letterView.debugIndex, 42, "Debug index should be assignable")
    }
    
    func testInstanceIdUniqueness() {
        // Test that instance IDs are unique
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let view1 = AlphabetLetterView(frame: frame, letter: "T", svgString: nil)
        let view2 = AlphabetLetterView(frame: frame, letter: "U", svgString: nil)
        
        XCTAssertNotEqual(view1.instanceId, view2.instanceId, "Instance IDs should be unique")
        XCTAssertGreaterThan(view2.instanceId, view1.instanceId, "Later views should have higher instance IDs")
    }
} 
