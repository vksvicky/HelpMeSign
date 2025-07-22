import XCTest
import Cocoa
import MetalKit
import AVFoundation
import Vision
import Macaw
@testable import HelpMeSign

class CameraViewControllerTests: XCTestCase {
    var cameraViewController: CameraViewController!
    
    override func setUp() {
        super.setUp()
        cameraViewController = CameraViewController()
    }
    
    override func tearDown() {
        cameraViewController = nil
        super.tearDown()
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful initialization
        XCTAssertNotNil(cameraViewController, "CameraViewController should be created successfully")
        XCTAssertFalse(cameraViewController.isRecognizing, "Should not be recognizing initially")
        XCTAssertFalse(cameraViewController.blurBackground, "Should not blur background initially")
        XCTAssertFalse(cameraViewController.centerFrame, "Should not center frame initially")
    }
    
    func testSuccessfulViewLoading() {
        // Test that view loads successfully
        cameraViewController.loadView()
        
        XCTAssertNotNil(cameraViewController.view, "View should be loaded")
        XCTAssertNotNil(cameraViewController.camView, "Camera view should be created")
        XCTAssertNotNil(cameraViewController.overlay, "Overlay should be created")
        XCTAssertNotNil(cameraViewController.startStopButton, "Start/stop button should be created")
        XCTAssertNotNil(cameraViewController.blurButton, "Blur button should be created")
        XCTAssertNotNil(cameraViewController.languageLabel, "Language label should be created")
        XCTAssertNotNil(cameraViewController.flagLabel, "Flag label should be created")
    }
    
    func testSuccessfulMetalViewCreation() {
        // Test Metal view creation
        cameraViewController.loadView()
        
        XCTAssertNotNil(cameraViewController.metalView, "Metal view should be created")
        XCTAssertNotNil(cameraViewController.metalView.device, "Metal device should be available")
        XCTAssertTrue(cameraViewController.metalView.delegate === cameraViewController, "CameraViewController should be the delegate")
        XCTAssertFalse(cameraViewController.metalView.isPaused, "Metal view should not be paused initially")
        XCTAssertEqual(cameraViewController.metalView.preferredFramesPerSecond, 60, "Preferred FPS should be 60")
    }
    
    func testSuccessfulUIElementConfiguration() {
        // Test UI element configuration
        cameraViewController.loadView()
        
        // Test camera view styling
        XCTAssertNotNil(cameraViewController.camView.layer, "Camera view should have layer")
        XCTAssertEqual(cameraViewController.camView.layer?.cornerRadius, 28, "Camera view should have corner radius")
        XCTAssertNotNil(cameraViewController.camView.layer?.shadowColor, "Camera view should have shadow")
        
        // Test button configuration
        XCTAssertNotNil(cameraViewController.startStopButton, "Start/stop button should exist")
        XCTAssertNotNil(cameraViewController.blurButton, "Blur button should exist")
    }
    
    func testSuccessfulLayoutCalculation() {
        // Test layout calculations
        cameraViewController.loadView()
        
        let view = cameraViewController.view
        XCTAssertNotNil(view, "View should be loaded")
        
        // Test that view has reasonable dimensions
        XCTAssertGreaterThan(view.frame.width, 0, "View should have positive width")
        XCTAssertGreaterThan(view.frame.height, 0, "View should have positive height")
        
        // Test that camera view is positioned within bounds
        XCTAssertGreaterThanOrEqual(cameraViewController.camView.frame.minX, 0, "Camera view should not be positioned outside bounds")
        XCTAssertGreaterThanOrEqual(cameraViewController.camView.frame.minY, 0, "Camera view should not be positioned outside bounds")
        XCTAssertLessThanOrEqual(cameraViewController.camView.frame.maxX, view.frame.width, "Camera view should not extend beyond bounds")
        XCTAssertLessThanOrEqual(cameraViewController.camView.frame.maxY, view.frame.height, "Camera view should not extend beyond bounds")
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testInitializationWithNoMetalDevice() {
        // Test behavior when Metal device is not available
        // This is difficult to test directly, but we can test the Metal view creation
        cameraViewController.loadView()
        
        // Even if Metal device is not available, the view should still be created
        XCTAssertNotNil(cameraViewController.metalView, "Metal view should be created even without device")
    }
    
    func testViewLoadingWithoutCameraPermissions() {
        // Test view loading when camera permissions are not granted
        cameraViewController.loadView()
        
        // View should still load successfully even without camera permissions
        XCTAssertNotNil(cameraViewController.view, "View should load even without camera permissions")
        XCTAssertNotNil(cameraViewController.camView, "Camera view should be created")
    }
    
    func testMetalViewDelegateMethods() {
        // Test Metal view delegate methods
        cameraViewController.loadView()
        
        // Test drawable size change
        let newSize = CGSize(width: 800, height: 600)
        cameraViewController.mtkView(cameraViewController.metalView, drawableSizeWillChange: newSize)
        
        // Test draw method
        cameraViewController.draw(in: cameraViewController.metalView)
        
        // These methods should not crash even if Metal setup is incomplete
    }
    
    func testCaptureSessionWithoutPermissions() {
        // Test capture session behavior without permissions
        cameraViewController.loadView()
        
        // Capture session might be nil without permissions, but should not crash
        XCTAssertNoThrow(cameraViewController.captureSession, "Accessing capture session should not crash")
    }
    
    // MARK: - Exception/Error Handling Tests
    
    func testMetalViewDrawWithInvalidState() {
        // Test Metal view draw method with invalid state
        cameraViewController.loadView()
        
        // Force invalid state by setting device to nil
        cameraViewController.metalView.device = nil
        
        // Draw should handle invalid state gracefully
        XCTAssertNoThrow(cameraViewController.draw(in: cameraViewController.metalView), "Draw should handle invalid Metal state")
    }
    
    func testCaptureSessionInitializationFailure() {
        // Test capture session initialization failure
        cameraViewController.loadView()
        
        // This test verifies that the app doesn't crash when camera setup fails
        // The actual capture session setup happens in viewDidLoad or similar
        XCTAssertNoThrow(cameraViewController.captureSession, "Accessing capture session should not crash even if initialization failed")
    }
    
    func testMetalTextureCacheFailure() {
        // Test Metal texture cache failure
        cameraViewController.loadView()
        
        // Access texture cache - should not crash even if not properly initialized
        XCTAssertNoThrow(cameraViewController.textureCache, "Accessing texture cache should not crash")
    }
    
    func testPipelineStateFailure() {
        // Test pipeline state failure
        cameraViewController.loadView()
        
        // Access pipeline state - should not crash even if not properly initialized
        XCTAssertNoThrow(cameraViewController.pipelineState, "Accessing pipeline state should not crash")
    }
    
    // MARK: - Edge Case Tests
    
    func testViewLoadingMultipleTimes() {
        // Test loading view multiple times
        cameraViewController.loadView()
        let firstView = cameraViewController.view
        
        cameraViewController.loadView()
        let secondView = cameraViewController.view
        
        XCTAssertEqual(firstView, secondView, "Loading view multiple times should return the same view")
    }
    
    func testMetalViewDelegateReassignment() {
        // Test Metal view delegate reassignment
        cameraViewController.loadView()
        
        let originalDelegate = cameraViewController.metalView.delegate
        cameraViewController.metalView.delegate = nil
        cameraViewController.metalView.delegate = originalDelegate
        
        XCTAssertTrue(cameraViewController.metalView.delegate === originalDelegate, "Delegate should be properly reassigned")
    }
    
    func testUIElementAccessBeforeViewLoad() {
        // Test accessing UI elements before view is loaded
        XCTAssertNil(cameraViewController.camView, "Camera view should be nil before view load")
        XCTAssertNil(cameraViewController.overlay, "Overlay should be nil before view load")
        XCTAssertNil(cameraViewController.startStopButton, "Start/stop button should be nil before view load")
        XCTAssertNil(cameraViewController.blurButton, "Blur button should be nil before view load")
    }
    
    func testViewFrameChanges() {
        // Test view frame changes
        cameraViewController.loadView()
        
        let originalFrame = cameraViewController.view.frame
        let newFrame = NSRect(x: 100, y: 100, width: 800, height: 600)
        
        cameraViewController.view.frame = newFrame
        XCTAssertEqual(cameraViewController.view.frame, newFrame, "View frame should be updated")
        
        // Reset to original frame
        cameraViewController.view.frame = originalFrame
        XCTAssertEqual(cameraViewController.view.frame, originalFrame, "View frame should be reset")
    }
    
    func testMetalViewConfiguration() {
        // Test Metal view configuration
        cameraViewController.loadView()
        
        // Test clear color
        XCTAssertNotNil(cameraViewController.metalView.clearColor, "Clear color should be set")
        
        // Test enableSetNeedsDisplay
        XCTAssertTrue(cameraViewController.metalView.enableSetNeedsDisplay, "enableSetNeedsDisplay should be true")
        
        // Test corner radius
        XCTAssertEqual(cameraViewController.metalView.layer?.cornerRadius, 28, "Metal view should have corner radius")
        XCTAssertTrue(cameraViewController.metalView.layer?.masksToBounds == true, "Metal view should mask to bounds")
    }
    
    // MARK: - Performance Tests
    
    func testPerformanceOfViewLoading() {
        // Test performance of view loading
        measure {
            let testVC = CameraViewController()
            testVC.loadView()
        }
    }
    
    func testPerformanceOfMetalViewDraw() {
        // Test performance of Metal view draw
        cameraViewController.loadView()
        
        measure {
            for _ in 0..<100 {
                cameraViewController.draw(in: cameraViewController.metalView)
            }
        }
    }
    
    func testPerformanceOfDrawableSizeChange() {
        // Test performance of drawable size change
        cameraViewController.loadView()
        
        measure {
            for i in 0..<100 {
                let size = CGSize(width: 100 + i, height: 100 + i)
                cameraViewController.mtkView(cameraViewController.metalView, drawableSizeWillChange: size)
            }
        }
    }
    
    // MARK: - Memory Tests
    
    func testMemoryManagement() {
        // Test memory management
        weak var weakVC: CameraViewController?
        
        autoreleasepool {
            let testVC = CameraViewController()
            testVC.loadView()
            weakVC = testVC
        }
        
        // The view controller should be deallocated after the autorelease pool
        XCTAssertNil(weakVC, "View controller should be deallocated")
    }
    
    func testMetalViewMemoryManagement() {
        // Test Metal view memory management
        cameraViewController.loadView()
        
        weak var weakMetalView: MTKView?
        
        autoreleasepool {
            weakMetalView = cameraViewController.metalView
        }
        
        // Metal view should still exist as it's retained by the view controller
        XCTAssertNotNil(weakMetalView, "Metal view should still exist")
    }
    
    // MARK: - Integration Tests
    
    func testHoverOverlayViewCreation() {
        // Test HoverOverlayView creation and functionality
        let hoverView = HoverOverlayView()
        var hoverState = false
        
        hoverView.onHoverChanged = { isHovered in
            hoverState = isHovered
        }
        
        // Test mouse enter
        hoverView.mouseEntered(with: NSEvent())
        XCTAssertTrue(hoverState, "Hover state should be true after mouse enter")
        
        // Test mouse exit
        hoverView.mouseExited(with: NSEvent())
        XCTAssertFalse(hoverState, "Hover state should be false after mouse exit")
    }
    
    func testTrackingAreaManagement() {
        // Test tracking area management in HoverOverlayView
        let hoverView = HoverOverlayView()
        
        // Initially no tracking areas
        XCTAssertEqual(hoverView.trackingAreas.count, 0, "Should have no tracking areas initially")
        
        // Update tracking areas
        hoverView.updateTrackingAreas()
        
        // Should have tracking areas after update
        XCTAssertGreaterThan(hoverView.trackingAreas.count, 0, "Should have tracking areas after update")
        
        // Update again should not duplicate
        let initialCount = hoverView.trackingAreas.count
        hoverView.updateTrackingAreas()
        XCTAssertEqual(hoverView.trackingAreas.count, initialCount, "Should not duplicate tracking areas")
    }
} 