import XCTest
import Cocoa
import Macaw
@testable import HelpMeSign

class AlphabetLetterViewTests: XCTestCase {
    var testNode: Node?
    
    override func setUp() {
        super.setUp()
        // Create a simple test SVG node
        testNode = Group()
    }
    
    override func tearDown() {
        testNode = nil
        super.tearDown()
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful initialization with valid parameters
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letter = "A"
        let letterView = AlphabetLetterView(frame: frame, letter: letter, svgNode: testNode)
        
        XCTAssertEqual(letterView.letter, "A", "Letter should be set correctly")
        XCTAssertEqual(letterView.frame, frame, "Frame should be set correctly")
        XCTAssertNotNil(letterView.svgNode, "SVG node should be set")
        XCTAssertNotNil(letterView.label, "Label should be created")
        XCTAssertFalse(letterView.isHovered, "Should not be hovered initially")
        XCTAssertGreaterThan(letterView.instanceId, 0, "Instance ID should be assigned")
    }
    
    func testSuccessfulLabelCreation() {
        // Test that label is created with correct properties
        let frame = NSRect(x: 0, y: 0, width: 60, height: 60)
        let letter = "B"
        let letterView = AlphabetLetterView(frame: frame, letter: letter, svgNode: nil)
        
        XCTAssertEqual(letterView.label.stringValue, "B", "Label should display the letter")
        XCTAssertEqual(letterView.label.alignment, .center, "Label should be center aligned")
        XCTAssertEqual(letterView.label.textColor, NSColor.labelColor, "Label should use system label color")
    }
    
    func testSuccessfulLayerConfiguration() {
        // Test that layer properties are set correctly
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "C", svgNode: nil)
        
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
        
        let smallView = AlphabetLetterView(frame: smallFrame, letter: "D", svgNode: nil)
        let largeView = AlphabetLetterView(frame: largeFrame, letter: "E", svgNode: nil)
        
        // Font sizes should be different based on frame size
        XCTAssertNotEqual(smallView.label.font?.pointSize ?? 0, largeView.label.font?.pointSize ?? 0, "Font sizes should differ based on frame size")
    }
    
    func testSuccessfulInstanceIdIncrement() {
        // Test that instance IDs are incremented correctly
        let initialCount = AlphabetLetterView.instanceCount
        
        let view1 = AlphabetLetterView(frame: NSRect(x: 0, y: 0, width: 50, height: 50), letter: "F", svgNode: nil)
        let view2 = AlphabetLetterView(frame: NSRect(x: 0, y: 0, width: 50, height: 50), letter: "G", svgNode: nil)
        
        XCTAssertEqual(view1.instanceId, initialCount + 1, "First view should have incremented instance ID")
        XCTAssertEqual(view2.instanceId, initialCount + 2, "Second view should have incremented instance ID")
        XCTAssertEqual(AlphabetLetterView.instanceCount, initialCount + 2, "Static count should be updated")
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testInitializationWithEmptyLetter() {
        // Test initialization with empty letter string
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "", svgNode: nil)
        
        XCTAssertEqual(letterView.letter, "", "Empty letter should be handled")
        XCTAssertEqual(letterView.label.stringValue, "", "Label should show empty string")
    }
    
    func testInitializationWithNilSVGNode() {
        // Test initialization with nil SVG node
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "H", svgNode: nil)
        
        XCTAssertNil(letterView.svgNode, "SVG node should be nil")
        XCTAssertNil(letterView.macawView, "Macaw view should be nil when SVG node is nil")
        XCTAssertNotNil(letterView.label, "Label should still be created as fallback")
    }
    
    func testInitializationWithZeroFrame() {
        // Test initialization with zero-sized frame
        let zeroFrame = NSRect(x: 0, y: 0, width: 0, height: 0)
        let letterView = AlphabetLetterView(frame: zeroFrame, letter: "I", svgNode: nil)
        
        XCTAssertEqual(letterView.frame, zeroFrame, "Zero frame should be accepted")
        XCTAssertNotNil(letterView.label, "Label should still be created")
    }
    
    func testInitializationWithNegativeFrame() {
        // Test initialization with negative frame dimensions
        let negativeFrame = NSRect(x: -10, y: -10, width: -20, height: -20)
        let letterView = AlphabetLetterView(frame: negativeFrame, letter: "J", svgNode: nil)
        
        XCTAssertEqual(letterView.frame, negativeFrame, "Negative frame should be accepted")
        XCTAssertNotNil(letterView.label, "Label should still be created")
    }
    
    func testInitializationWithVeryLargeFrame() {
        // Test initialization with very large frame
        let largeFrame = NSRect(x: 0, y: 0, width: 1000, height: 1000)
        let letterView = AlphabetLetterView(frame: largeFrame, letter: "K", svgNode: nil)
        
        XCTAssertEqual(letterView.frame, largeFrame, "Large frame should be accepted")
        XCTAssertNotNil(letterView.label, "Label should still be created")
    }
    
    // MARK: - Exception/Error Handling Tests
    
    func testInitializationWithSpecialCharacters() {
        // Test initialization with special characters in letter
        let specialChars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "="]
        
        for char in specialChars {
            let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
            let letterView = AlphabetLetterView(frame: frame, letter: char, svgNode: nil)
            
            XCTAssertEqual(letterView.letter, char, "Special character '\(char)' should be handled")
            XCTAssertEqual(letterView.label.stringValue, char, "Label should display special character '\(char)'")
        }
    }
    
    func testInitializationWithUnicodeCharacters() {
        // Test initialization with Unicode characters
        let unicodeChars = ["α", "β", "γ", "δ", "ε", "ñ", "ç", "ü", "é", "à"]
        
        for char in unicodeChars {
            let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
            let letterView = AlphabetLetterView(frame: frame, letter: char, svgNode: nil)
            
            XCTAssertEqual(letterView.letter, char, "Unicode character '\(char)' should be handled")
            XCTAssertEqual(letterView.label.stringValue, char, "Label should display Unicode character '\(char)'")
        }
    }
    
    func testInitializationWithLongString() {
        // Test initialization with very long letter string
        let longString = String(repeating: "A", count: 100)
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: longString, svgNode: nil)
        
        XCTAssertEqual(letterView.letter, longString, "Long string should be handled")
        XCTAssertEqual(letterView.label.stringValue, longString, "Label should display long string")
    }
    
    func testInitializationWithWhitespaceOnly() {
        // Test initialization with whitespace-only string
        let whitespaceString = "   \t\n   "
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: whitespaceString, svgNode: nil)
        
        XCTAssertEqual(letterView.letter, whitespaceString, "Whitespace string should be handled")
        XCTAssertEqual(letterView.label.stringValue, whitespaceString, "Label should display whitespace string")
    }
    
    // MARK: - Edge Case Tests
    
    func testHoverStateChanges() {
        // Test hover state changes
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "L", svgNode: nil)
        
        XCTAssertFalse(letterView.isHovered, "Should not be hovered initially")
        
        // Simulate mouse enter
        letterView.mouseEntered(with: NSEvent())
        XCTAssertTrue(letterView.isHovered, "Should be hovered after mouse enter")
        
        // Simulate mouse exit
        letterView.mouseExited(with: NSEvent())
        XCTAssertFalse(letterView.isHovered, "Should not be hovered after mouse exit")
    }
    
    func testTrackingAreaCreation() {
        // Test that tracking areas are created
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "M", svgNode: nil)
        
        XCTAssertGreaterThan(letterView.trackingAreas.count, 0, "Tracking areas should be created")
        
        let trackingArea = letterView.trackingAreas.first
        XCTAssertNotNil(trackingArea, "Tracking area should exist")
        XCTAssertEqual(trackingArea?.owner as? AlphabetLetterView, letterView, "Tracking area owner should be the view")
    }
    
    func testAnimationWithoutSVGNode() {
        // Test animation when no SVG node is present
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "N", svgNode: nil)
        
        // This should not crash
        letterView.animateZoom()
        
        // Simulate hover to trigger animation
        letterView.isHovered = true
        letterView.animateZoom()
        
        letterView.isHovered = false
        letterView.animateZoom()
    }
    
    func testAnimationWithSVGNode() {
        // Test animation when SVG node is present
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "O", svgNode: testNode)
        
        // This should not crash
        letterView.animateZoom()
        
        // Simulate hover to trigger animation
        letterView.isHovered = true
        letterView.animateZoom()
        
        letterView.isHovered = false
        letterView.animateZoom()
    }
    
    func testMultipleHoverStateChanges() {
        // Test rapid hover state changes
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "P", svgNode: nil)
        
        for _ in 0..<10 {
            letterView.isHovered = true
            letterView.isHovered = false
        }
        
        XCTAssertFalse(letterView.isHovered, "Final state should be not hovered")
    }
    
    func testLabelPositioning() {
        // Test label positioning in different frame sizes
        let smallFrame = NSRect(x: 0, y: 0, width: 30, height: 30)
        let largeFrame = NSRect(x: 0, y: 0, width: 100, height: 100)
        
        let smallView = AlphabetLetterView(frame: smallFrame, letter: "Q", svgNode: nil)
        let largeView = AlphabetLetterView(frame: largeFrame, letter: "R", svgNode: nil)
        
        // Labels should be positioned within their respective frames
        XCTAssertTrue(smallView.label.frame.maxX <= smallFrame.width, "Small view label should fit within frame")
        XCTAssertTrue(smallView.label.frame.maxY <= smallFrame.height, "Small view label should fit within frame")
        XCTAssertTrue(largeView.label.frame.maxX <= largeFrame.width, "Large view label should fit within frame")
        XCTAssertTrue(largeView.label.frame.maxY <= largeFrame.height, "Large view label should fit within frame")
    }
    
    // MARK: - Performance Tests
    
    func testPerformanceWithManyViews() {
        // Test performance when creating many views
        measure {
            for i in 0..<100 {
                let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
                let letter = String(UnicodeScalar(65 + (i % 26))!) // A-Z
                let _ = AlphabetLetterView(frame: frame, letter: letter, svgNode: nil)
            }
        }
    }
    
    func testPerformanceWithRapidHoverChanges() {
        // Test performance with rapid hover state changes
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "S", svgNode: nil)
        
        measure {
            for _ in 0..<1000 {
                letterView.isHovered.toggle()
            }
        }
    }
    
    func testPerformanceWithLargeFrames() {
        // Test performance with large frame sizes
        measure {
            for i in 0..<50 {
                let frame = NSRect(x: 0, y: 0, width: 500 + i, height: 500 + i)
                let letter = String(UnicodeScalar(65 + (i % 26))!) // A-Z
                let _ = AlphabetLetterView(frame: frame, letter: letter, svgNode: nil)
            }
        }
    }
    
    // MARK: - Memory Tests
    
    func testMemoryManagement() {
        // Test that views are properly deallocated
        weak var weakView: AlphabetLetterView?
        
        autoreleasepool {
            let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
            let letterView = AlphabetLetterView(frame: frame, letter: "T", svgNode: nil)
            weakView = letterView
        }
        
        // The view should be deallocated after the autorelease pool
        XCTAssertNil(weakView, "View should be deallocated")
    }
    
    func testTrackingAreaCleanup() {
        // Test that tracking areas are properly managed
        let frame = NSRect(x: 0, y: 0, width: 50, height: 50)
        let letterView = AlphabetLetterView(frame: frame, letter: "U", svgNode: nil)
        
        let initialTrackingAreaCount = letterView.trackingAreas.count
        XCTAssertGreaterThan(initialTrackingAreaCount, 0, "Should have tracking areas initially")
        
        // Remove all tracking areas
        for area in letterView.trackingAreas {
            letterView.removeTrackingArea(area)
        }
        
        XCTAssertEqual(letterView.trackingAreas.count, 0, "All tracking areas should be removed")
    }
} 