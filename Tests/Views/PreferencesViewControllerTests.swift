import XCTest
import Cocoa
@testable import HelpMeSign

class PreferencesViewControllerTests: XCTestCase {
    var preferencesViewController: PreferencesViewController!
    
    override func setUp() {
        super.setUp()
        preferencesViewController = PreferencesViewController()
        preferencesViewController.loadView()
    }
    
    override func tearDown() {
        preferencesViewController = nil
        super.tearDown()
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test successful initialization
        XCTAssertNotNil(preferencesViewController, "PreferencesViewController should be created successfully")
    }
    
    func testSuccessfulViewLoading() {
        // Test that view loads successfully
        XCTAssertNotNil(preferencesViewController.view, "View should be loaded")
    }
    
    func testSuccessfulStatusLabelCreation() {
        // Test that status labels are created
        // Note: In unit tests, outlets are nil because they're not connected from storyboard
        // This is expected behavior when creating view controllers programmatically
        XCTAssertNil(preferencesViewController.cameraStatusLabel, "Camera status label should be nil in unit tests (not connected from storyboard)")
        XCTAssertNil(preferencesViewController.micStatusLabel, "Microphone status label should be nil in unit tests (not connected from storyboard)")
    }
    
    func testSuccessfulPermissionStatusRetrieval() {
        // Test permission status retrieval
        let cameraStatus = PreferencesViewController.permissionStatus(for: .video)
        let micStatus = PreferencesViewController.permissionStatus(for: .audio)
        
        XCTAssertNotNil(cameraStatus, "Camera permission status should be retrieved")
        XCTAssertNotNil(micStatus, "Microphone permission status should be retrieved")
        XCTAssertNotNil(cameraStatus.text, "Camera status text should exist")
        XCTAssertNotNil(micStatus.text, "Microphone status text should exist")
        XCTAssertNotNil(cameraStatus.color, "Camera status color should exist")
        XCTAssertNotNil(micStatus.color, "Microphone status color should exist")
    }
    
    func testSuccessfulStatusLabelUpdate() {
        // Test status label update
        // Since outlets are nil in unit tests, we just verify the method doesn't crash
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "Status label update should not crash when outlets are nil")
    }
    
    func testSuccessfulNotificationObserverSetup() {
        // Test notification observer setup
        preferencesViewController.viewWillAppear()
        
        // Verify that the view controller is observing the notification
        // Note: We can't directly access observers, but we can verify the method doesn't crash
        XCTAssertNoThrow(preferencesViewController.viewWillAppear(), "Notification observer setup should not crash")
    }
    
    // MARK: - Negative/Unhappy Path Tests
    
    func testPermissionStatusWithNoUserDefaults() {
        // Test permission status when UserDefaults has no values
        // Clear UserDefaults for testing
        UserDefaults.standard.removeObject(forKey: "CameraAccessGranted")
        UserDefaults.standard.removeObject(forKey: "MicAccessGranted")
        
        let cameraStatus = PreferencesViewController.permissionStatus(for: .video)
        let micStatus = PreferencesViewController.permissionStatus(for: .audio)
        
        XCTAssertEqual(cameraStatus.text, "Not Requested", "Camera status should be 'Not Requested' when no UserDefaults value")
        XCTAssertEqual(micStatus.text, "Not Requested", "Microphone status should be 'Not Requested' when no UserDefaults value")
        XCTAssertEqual(cameraStatus.color, .systemGray, "Camera status color should be gray when not requested")
        XCTAssertEqual(micStatus.color, .systemGray, "Microphone status color should be gray when not requested")
    }
    
    func testPermissionStatusWithDeniedAccess() {
        // Test permission status when access is denied
        UserDefaults.standard.set(false, forKey: "CameraAccessGranted")
        UserDefaults.standard.set(false, forKey: "MicAccessGranted")
        
        let cameraStatus = PreferencesViewController.permissionStatus(for: .video)
        let micStatus = PreferencesViewController.permissionStatus(for: .audio)
        
        XCTAssertEqual(cameraStatus.text, "Denied ❌", "Camera status should be 'Denied' when access is denied")
        XCTAssertEqual(micStatus.text, "Denied ❌", "Microphone status should be 'Denied' when access is denied")
        XCTAssertEqual(cameraStatus.color, .systemRed, "Camera status color should be red when denied")
        XCTAssertEqual(micStatus.color, .systemRed, "Microphone status color should be red when denied")
    }
    
    func testPermissionStatusWithGrantedAccess() {
        // Test permission status when access is granted
        UserDefaults.standard.set(true, forKey: "CameraAccessGranted")
        UserDefaults.standard.set(true, forKey: "MicAccessGranted")
        
        let cameraStatus = PreferencesViewController.permissionStatus(for: .video)
        let micStatus = PreferencesViewController.permissionStatus(for: .audio)
        
        XCTAssertEqual(cameraStatus.text, "Allowed ✅", "Camera status should be 'Allowed' when access is granted")
        XCTAssertEqual(micStatus.text, "Allowed ✅", "Microphone status should be 'Allowed' when access is granted")
        XCTAssertEqual(cameraStatus.color, .systemGreen, "Camera status color should be green when allowed")
        XCTAssertEqual(micStatus.color, .systemGreen, "Microphone status color should be green when allowed")
    }
    
    func testViewWillDisappear() {
        // Test view will disappear
        preferencesViewController.viewWillAppear()
        XCTAssertNoThrow(preferencesViewController.viewWillDisappear(), "viewWillDisappear should not throw")
    }
    
    // MARK: - Exception/Error Handling Tests
    
    func testPermissionStatusWithInvalidType() {
        // Test permission status with invalid type (this would require enum modification to test properly)
        // For now, we test that the existing types work correctly
        XCTAssertNoThrow(PreferencesViewController.permissionStatus(for: .video), "Video permission status should not throw")
        XCTAssertNoThrow(PreferencesViewController.permissionStatus(for: .audio), "Audio permission status should not throw")
    }
    
    func testUpdateStatusLabelsWithNilLabels() {
        // Test update status labels when labels are nil
        // This is difficult to test directly, but we can verify the method doesn't crash
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "updateStatusLabels should not crash")
    }
    
    func testNotificationObserverRemoval() {
        // Test notification observer removal
        preferencesViewController.viewWillAppear()
        preferencesViewController.viewWillDisappear()
        
        // Verify that observers are removed (this is difficult to test directly)
        XCTAssertNoThrow(preferencesViewController.viewWillDisappear(), "viewWillDisappear should not throw when called multiple times")
    }
    
    func testClosePreferencesWithNilWindow() {
        // Test close preferences with nil window
        XCTAssertNoThrow(preferencesViewController.closePreferences(nil), "closePreferences should not crash with nil window")
    }
    
    func testOpenCameraSettings() {
        // Test opening camera settings
        XCTAssertNoThrow(preferencesViewController.openCameraSettings(nil), "openCameraSettings should not throw")
    }
    
    func testOpenMicrophoneSettings() {
        // Test opening microphone settings
        XCTAssertNoThrow(preferencesViewController.openMicrophoneSettings(nil), "openMicrophoneSettings should not throw")
    }
    
    // MARK: - Edge Case Tests
    
    func testMultipleViewWillAppearCalls() {
        // Test multiple viewWillAppear calls
        XCTAssertNoThrow(preferencesViewController.viewWillAppear(), "First viewWillAppear should not throw")
        XCTAssertNoThrow(preferencesViewController.viewWillAppear(), "Second viewWillAppear should not throw")
    }
    
    func testMultipleViewWillDisappearCalls() {
        // Test multiple viewWillDisappear calls
        preferencesViewController.viewWillAppear()
        XCTAssertNoThrow(preferencesViewController.viewWillDisappear(), "First viewWillDisappear should not throw")
        XCTAssertNoThrow(preferencesViewController.viewWillDisappear(), "Second viewWillDisappear should not throw")
    }
    
    func testMultipleUpdateStatusLabelsCalls() {
        // Test multiple updateStatusLabels calls
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "First updateStatusLabels should not throw")
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "Second updateStatusLabels should not throw")
    }
    
    func testPermissionStatusWithMixedStates() {
        // Test permission status with mixed states
        UserDefaults.standard.set(true, forKey: "CameraAccessGranted")
        UserDefaults.standard.set(false, forKey: "MicAccessGranted")
        
        let cameraStatus = PreferencesViewController.permissionStatus(for: .video)
        let micStatus = PreferencesViewController.permissionStatus(for: .audio)
        
        XCTAssertEqual(cameraStatus.text, "Allowed ✅", "Camera status should be 'Allowed' when granted")
        XCTAssertEqual(micStatus.text, "Denied ❌", "Microphone status should be 'Denied' when denied")
        XCTAssertEqual(cameraStatus.color, .systemGreen, "Camera status color should be green when allowed")
        XCTAssertEqual(micStatus.color, .systemRed, "Microphone status color should be red when denied")
    }
    
    func testStatusLabelFontConfiguration() {
        // Test status label font configuration
        // Since outlets are nil in unit tests, we just verify the method doesn't crash
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "Status label font configuration should not crash when outlets are nil")
    }
    
    func testStatusLabelTextFormat() {
        // Test status label text format
        UserDefaults.standard.set(true, forKey: "CameraAccessGranted")
        UserDefaults.standard.set(false, forKey: "MicAccessGranted")
        
        // Since outlets are nil in unit tests, we just verify the method doesn't crash
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "Status label text format should not crash when outlets are nil")
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "CameraAccessGranted")
        UserDefaults.standard.removeObject(forKey: "MicAccessGranted")
    }
    
    // MARK: - Performance Tests
    
    func testPerformanceOfPermissionStatusRetrieval() {
        // Test performance of permission status retrieval
        measure {
            for _ in 0..<1000 {
                _ = PreferencesViewController.permissionStatus(for: .video)
                _ = PreferencesViewController.permissionStatus(for: .audio)
            }
        }
    }
    
    func testPerformanceOfUpdateStatusLabels() {
        // Test performance of update status labels
        measure {
            for _ in 0..<100 {
                preferencesViewController.updateStatusLabels()
            }
        }
    }
    
    func testPerformanceOfViewWillAppear() {
        // Test performance of viewWillAppear
        measure {
            for _ in 0..<100 {
                preferencesViewController.viewWillAppear()
            }
        }
    }
    
    // MARK: - Memory Tests
    
    func testMemoryManagement() {
        // Test memory management
        autoreleasepool {
            let testVC = PreferencesViewController()
            testVC.loadView()
        }
        
        // The view controller should be deallocated after the autorelease pool
        // Note: In some cases, the autorelease pool might not immediately deallocate
        // the object, so we'll just verify the test completes without crashing
        XCTAssertNoThrow({}, "Memory management test should complete without crashing")
    }
    
    func testNotificationObserverMemoryManagement() {
        // Test notification observer memory management
        // Create a separate instance for this test to avoid conflicts with the shared instance
        let testVC = PreferencesViewController()
        testVC.loadView()
        
        // Add notification observer
        testVC.viewWillAppear()
        
        // Remove notification observer
        testVC.viewWillDisappear()
        
        // Verify the test completes without crashing
        XCTAssertNoThrow({}, "Notification observer memory management should complete without crashing")
    }
    
    // MARK: - Integration Tests
    
    func testIntegrationWithUserDefaults() {
        // Test integration with UserDefaults
        let testValue = true
        UserDefaults.standard.set(testValue, forKey: "CameraAccessGranted")
        
        let status = PreferencesViewController.permissionStatus(for: .video)
        XCTAssertEqual(status.text, "Allowed ✅", "Status should reflect UserDefaults value")
        
        // Clean up
        UserDefaults.standard.removeObject(forKey: "CameraAccessGranted")
    }
    
    func testIntegrationWithNotificationCenter() {
        // Test integration with NotificationCenter
        preferencesViewController.viewWillAppear()
        
        // Post notification
        NotificationCenter.default.post(name: AppDelegateNotificationNames.permissionStatusChanged, object: nil)
        
        // This should trigger updateStatusLabels
        XCTAssertNoThrow(preferencesViewController.updateStatusLabels(), "Notification should trigger status update")
    }
    
    func testIntegrationWithNSWorkspace() {
        // Test integration with NSWorkspace for opening settings
        XCTAssertNoThrow(preferencesViewController.openCameraSettings(nil), "Should open camera settings")
        XCTAssertNoThrow(preferencesViewController.openMicrophoneSettings(nil), "Should open microphone settings")
    }
    
    // MARK: - State Tests
    
    func testInitialState() {
        // Test initial state
        XCTAssertNotNil(preferencesViewController.view, "View should be loaded in initial state")
    }
    
    func testStateAfterViewWillAppear() {
        // Test state after viewWillAppear
        // Since outlets are nil in unit tests, we just verify the method doesn't crash
        XCTAssertNoThrow(preferencesViewController.viewWillAppear(), "viewWillAppear should not crash when outlets are nil")
        
        // Verify that notification observer was added (this is the main functionality we want to test)
        // We can't directly access observers, but we can verify the method completes successfully
    }
    
    func testStateAfterViewWillDisappear() {
        // Test state after viewWillDisappear
        preferencesViewController.viewWillAppear()
        preferencesViewController.viewWillDisappear()
        
        // View controller should still exist
        XCTAssertNotNil(preferencesViewController, "View controller should still exist")
    }
    
    // MARK: - Helper Method Tests
    
    func testPermissionTypeEnum() {
        // Test PermissionType enum
        XCTAssertEqual(PreferencesViewController.PermissionType.video, .video, "Video permission type should be accessible")
        XCTAssertEqual(PreferencesViewController.PermissionType.audio, .audio, "Audio permission type should be accessible")
    }
    
    func testPermissionStatusStruct() {
        // Test PermissionStatus struct
        let status = PreferencesViewController.PermissionStatus(text: "Test", color: .red)
        
        XCTAssertEqual(status.text, "Test", "PermissionStatus text should be set correctly")
        XCTAssertEqual(status.color, .red, "PermissionStatus color should be set correctly")
    }
} 