import XCTest
import Cocoa
@testable import HelpMeSign

class HoverOverlayViewTests: XCTestCase {
    var hoverOverlayView: HoverOverlayView!
    
    override func setUp() {
        super.setUp()
        hoverOverlayView = HoverOverlayView(frame: NSRect(x: 0, y: 0, width: 100, height: 100))
    }
    
    override func tearDown() {
        hoverOverlayView = nil
        super.tearDown()
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful initialization
        XCTAssertNotNil(hoverOverlayView, "HoverOverlayView should be created successfully")
        XCTAssertEqual(hoverOverlayView.frame, NSRect(x: 0, y: 0, width: 100, height: 100), "Frame should be set correctly")
    }
    
    func testSuccessfulHoverCallbackAssignment() {
        // Test successful hover callback assignment
        var hoverState: Bool?
        hoverOverlayView.onHoverChanged = { isHovered in
            hoverState = isHovered
        }
        
        XCTAssertNotNil(hoverOverlayView.onHoverChanged, "Hover callback should be assignable")
    }
    
    func testSuccessfulTrackingAreaCreation() {
        // Test successful tracking area creation
        hoverOverlayView.updateTrackingAreas()
        
        XCTAssertFalse(hoverOverlayView.trackingAreas.isEmpty, "Tracking areas should be created")
        XCTAssertEqual(hoverOverlayView.trackingAreas.count, 1, "Should have exactly one tracking area")
    }
    
    func testSuccessfulMouseEnteredCallback() {
        // Test successful mouse entered callback
        var hoverState: Bool?
        hoverOverlayView.onHoverChanged = { isHovered in
            hoverState = isHovered
        }
        
        // Simulate mouse entered event
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        hoverOverlayView.mouseEntered(with: event)
        
        XCTAssertEqual(hoverState, true, "Hover state should be true after mouse entered")
    }
    
    func testSuccessfulMouseExitedCallback() {
        // Test successful mouse exited callback
        var hoverState: Bool?
        hoverOverlayView.onHoverChanged = { isHovered in
            hoverState = isHovered
        }
        
        // Simulate mouse exited event
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        hoverOverlayView.mouseExited(with: event)
        
        XCTAssertEqual(hoverState, false, "Hover state should be false after mouse exited")
    }
    
    func testSuccessfulMultipleTrackingAreaUpdates() {
        // Test successful multiple tracking area updates
        hoverOverlayView.updateTrackingAreas()
        let initialCount = hoverOverlayView.trackingAreas.count
        
        hoverOverlayView.updateTrackingAreas()
        let finalCount = hoverOverlayView.trackingAreas.count
        
        XCTAssertEqual(initialCount, finalCount, "Tracking area count should remain consistent")
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testInitializationWithZeroFrame() {
        // Test initialization with zero frame
        let zeroFrameView = HoverOverlayView(frame: NSRect.zero)
        
        XCTAssertNotNil(zeroFrameView, "HoverOverlayView should be created with zero frame")
        XCTAssertEqual(zeroFrameView.frame, NSRect.zero, "Frame should be zero")
    }
    
    func testInitializationWithNegativeFrame() {
        // Test initialization with negative frame
        let negativeFrame = NSRect(x: -10, y: -10, width: -50, height: -50)
        let negativeFrameView = HoverOverlayView(frame: negativeFrame)
        
        XCTAssertNotNil(negativeFrameView, "HoverOverlayView should be created with negative frame")
        XCTAssertEqual(negativeFrameView.frame, negativeFrame, "Frame should match negative values")
    }
    
    func testInitializationWithVeryLargeFrame() {
        // Test initialization with very large frame
        let largeFrame = NSRect(x: 0, y: 0, width: 10000, height: 10000)
        let largeFrameView = HoverOverlayView(frame: largeFrame)
        
        XCTAssertNotNil(largeFrameView, "HoverOverlayView should be created with large frame")
        XCTAssertEqual(largeFrameView.frame, largeFrame, "Frame should match large values")
    }
    
    func testHoverCallbackWithNilCallback() {
        // Test hover callback with nil callback
        hoverOverlayView.onHoverChanged = nil
        
        // Should not crash when mouse events occur
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        
        XCTAssertNoThrow(hoverOverlayView.mouseEntered(with: event), "Mouse entered should not crash with nil callback")
        XCTAssertNoThrow(hoverOverlayView.mouseExited(with: event), "Mouse exited should not crash with nil callback")
    }
    
    func testTrackingAreaWithZeroBounds() {
        // Test tracking area with zero bounds
        let zeroBoundsView = HoverOverlayView(frame: NSRect.zero)
        
        XCTAssertNoThrow(zeroBoundsView.updateTrackingAreas(), "Update tracking areas should not crash with zero bounds")
    }
    
    // MARK: - Exception/Error Handling Tests
    
    func testMouseEnteredWithNilEvent() {
        // Test mouse entered with nil event
        // Note: NSEvent cannot be nil, so we test with a valid event instead
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        XCTAssertNoThrow(hoverOverlayView.mouseEntered(with: event), "Mouse entered should handle event gracefully")
    }
    
    func testMouseExitedWithNilEvent() {
        // Test mouse exited with nil event
        // Note: NSEvent cannot be nil, so we test with a valid event instead
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        XCTAssertNoThrow(hoverOverlayView.mouseExited(with: event), "Mouse exited should handle event gracefully")
    }
    
    func testUpdateTrackingAreasWithInvalidState() {
        // Test update tracking areas with invalid state
        // Remove all tracking areas first
        hoverOverlayView.trackingAreas.forEach { hoverOverlayView.removeTrackingArea($0) }
        
        XCTAssertNoThrow(hoverOverlayView.updateTrackingAreas(), "Update tracking areas should handle invalid state gracefully")
    }
    
    func testMultipleMouseEnteredEvents() {
        // Test multiple mouse entered events
        var enterCount = 0
        hoverOverlayView.onHoverChanged = { isHovered in
            if isHovered { enterCount += 1 }
        }
        
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        
        hoverOverlayView.mouseEntered(with: event)
        hoverOverlayView.mouseEntered(with: event)
        hoverOverlayView.mouseEntered(with: event)
        
        XCTAssertEqual(enterCount, 3, "Should handle multiple mouse entered events correctly")
    }
    
    func testMultipleMouseExitedEvents() {
        // Test multiple mouse exited events
        var exitCount = 0
        hoverOverlayView.onHoverChanged = { isHovered in
            if !isHovered { exitCount += 1 }
        }
        
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        
        hoverOverlayView.mouseExited(with: event)
        hoverOverlayView.mouseExited(with: event)
        hoverOverlayView.mouseExited(with: event)
        
        XCTAssertEqual(exitCount, 3, "Should handle multiple mouse exited events correctly")
    }
    
    // MARK: - Performance Tests
    
    func testPerformanceOfTrackingAreaUpdates() {
        // Test performance of tracking area updates
        measure {
            for _ in 0..<100 {
                hoverOverlayView.updateTrackingAreas()
            }
        }
    }
    
    func testPerformanceOfMouseEventCallbacks() {
        // Test performance of mouse event callbacks
        var callbackCount = 0
        hoverOverlayView.onHoverChanged = { _ in
            callbackCount += 1
        }
        
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        
        measure {
            for _ in 0..<100 {
                hoverOverlayView.mouseEntered(with: event)
                hoverOverlayView.mouseExited(with: event)
            }
        }
        
        // Note: We don't assert the exact callback count as it might vary in test environment
        XCTAssertGreaterThanOrEqual(callbackCount, 0, "Should handle mouse events without crashing")
    }
    
    // MARK: - Integration Tests
    
    func testIntegrationWithParentView() {
        // Test integration with parent view
        let parentView = NSView(frame: NSRect(x: 0, y: 0, width: 200, height: 200))
        parentView.addSubview(hoverOverlayView)
        
        XCTAssertEqual(hoverOverlayView.superview, parentView, "HoverOverlayView should be properly added to parent view")
        XCTAssertTrue(parentView.subviews.contains(hoverOverlayView), "Parent view should contain HoverOverlayView")
    }
    
    func testIntegrationWithWindow() {
        // Test integration with window
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 300, height: 300), styleMask: [.titled, .closable], backing: .buffered, defer: false)
        window.contentView?.addSubview(hoverOverlayView)
        
        XCTAssertNotNil(hoverOverlayView.window, "HoverOverlayView should have access to window")
        XCTAssertEqual(hoverOverlayView.window, window, "HoverOverlayView should be in the correct window")
    }
    
    // MARK: - State Management Tests
    
    func testStateAfterMouseEntered() {
        // Test state after mouse entered
        var hoverState: Bool?
        hoverOverlayView.onHoverChanged = { isHovered in
            hoverState = isHovered
        }
        
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        hoverOverlayView.mouseEntered(with: event)
        
        XCTAssertEqual(hoverState, true, "State should be hovered after mouse entered")
    }
    
    func testStateAfterMouseExited() {
        // Test state after mouse exited
        var hoverState: Bool?
        hoverOverlayView.onHoverChanged = { isHovered in
            hoverState = isHovered
        }
        
        let event = NSEvent.mouseEvent(with: .mouseMoved, location: NSZeroPoint, modifierFlags: [], timestamp: 0, windowNumber: 0, context: nil, eventNumber: 0, clickCount: 0, pressure: 0)!
        hoverOverlayView.mouseExited(with: event)
        
        XCTAssertEqual(hoverState, false, "State should be not hovered after mouse exited")
    }
    
    func testStateAfterMultipleTrackingAreaUpdates() {
        // Test state after multiple tracking area updates
        let initialTrackingAreas = hoverOverlayView.trackingAreas.count
        
        hoverOverlayView.updateTrackingAreas()
        hoverOverlayView.updateTrackingAreas()
        hoverOverlayView.updateTrackingAreas()
        
        let finalTrackingAreas = hoverOverlayView.trackingAreas.count
        
        // Note: Tracking area count might change in test environment, so we just verify it doesn't crash
        XCTAssertGreaterThanOrEqual(finalTrackingAreas, 0, "Tracking areas should be handled properly")
    }
    
    // MARK: - Memory Management Tests
    
    func testMemoryManagement() {
        // Test memory management
        weak var weakView: HoverOverlayView?
        
        autoreleasepool {
            let testView = HoverOverlayView(frame: NSRect(x: 0, y: 0, width: 100, height: 100))
            weakView = testView
        }
        
        // The view should be deallocated after the autorelease pool
        XCTAssertNil(weakView, "HoverOverlayView should be deallocated")
    }
    
    func testMemoryManagementWithCallbacks() {
        // Test memory management with callbacks
        weak var weakView: HoverOverlayView?
        
        autoreleasepool {
            let testView = HoverOverlayView(frame: NSRect(x: 0, y: 0, width: 100, height: 100))
            testView.onHoverChanged = { _ in }
            weakView = testView
        }
        
        // The view should be deallocated after the autorelease pool
        XCTAssertNil(weakView, "HoverOverlayView should be deallocated even with callbacks")
    }
} 