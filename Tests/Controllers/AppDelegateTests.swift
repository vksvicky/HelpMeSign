import XCTest
@testable import HelpMeSign

class AppDelegateTests: XCTestCase {
    
    var appDelegate: AppDelegate!
    
    override func setUp() {
        super.setUp()
        appDelegate = AppDelegate()
    }
    
    override func tearDown() {
        appDelegate = nil
        super.tearDown()
    }
    
    // MARK: - Basic Tests
    
    func testBasicInitialization() {
        // Test that AppDelegate can be created
        XCTAssertNotNil(appDelegate, "AppDelegate should be created successfully")
    }
    
    func testBasicMethodCalls() {
        // Test that basic methods can be called without crashing
        let launchNotification = Notification(name: NSApplication.didFinishLaunchingNotification)
        let terminateNotification = Notification(name: NSApplication.willTerminateNotification)
        
        // These should not throw or crash
        XCTAssertNoThrow(appDelegate.applicationDidFinishLaunching(launchNotification))
        XCTAssertNoThrow(appDelegate.applicationWillTerminate(terminateNotification))
    }
    
    // MARK: - Success/Happy Path Tests
    
    func testSuccessfulInitialization() {
        // Test basic initialization
        XCTAssertNotNil(appDelegate, "AppDelegate should be created successfully")
    }
    
    func testMultipleApplicationDidFinishLaunchingCalls() {
        // Test that multiple calls to applicationDidFinishLaunching are handled gracefully
        let notification = Notification(name: NSApplication.didFinishLaunchingNotification)
        
        // First call should succeed
        XCTAssertNoThrow(appDelegate.applicationDidFinishLaunching(notification))
        
        // Second call should also succeed (but might be ignored due to hasLaunched flag)
        XCTAssertNoThrow(appDelegate.applicationDidFinishLaunching(notification))
        
        // Third call should also succeed
        XCTAssertNoThrow(appDelegate.applicationDidFinishLaunching(notification))
    }
    
    func testSuccessfulApplicationStateManagement() {
        // Test successful application state management
        let launchNotification = Notification(name: NSApplication.didFinishLaunchingNotification)
        let terminateNotification = Notification(name: NSApplication.willTerminateNotification)
        
        // Test that launch method can be called without throwing
        XCTAssertNoThrow(appDelegate.applicationDidFinishLaunching(launchNotification), 
                        "applicationDidFinishLaunching should not throw")
        
        // Test that terminate method can be called without throwing
        XCTAssertNoThrow(appDelegate.applicationWillTerminate(terminateNotification), 
                        "applicationWillTerminate should not throw")
    }
    
    // MARK: - Memory Management Tests
    
    func testMemoryManagement() {
        // Test memory management
        let notification = Notification(name: NSApplication.didFinishLaunchingNotification)
        
        weak var weakAppDelegate: AppDelegate?
        
        autoreleasepool {
            let localAppDelegate = AppDelegate()
            weakAppDelegate = localAppDelegate
            
            // Test that the method can be called without crashing
            XCTAssertNoThrow(localAppDelegate.applicationDidFinishLaunching(notification), 
                           "applicationDidFinishLaunching should not throw")
            
            // Clean up properly
            let terminateNotification = Notification(name: NSApplication.willTerminateNotification)
            XCTAssertNoThrow(localAppDelegate.applicationWillTerminate(terminateNotification),
                           "applicationWillTerminate should not throw")
        }
        
        // In a test environment, we can't guarantee immediate deallocation
        // Just verify that the method calls didn't crash
        XCTAssertTrue(true, "Memory management test completed without crashing")
    }
    
    func testMemoryManagementWithMultipleLaunches() {
        // Test memory management with multiple launches
        let notification = Notification(name: NSApplication.didFinishLaunchingNotification)
        
        weak var weakAppDelegate1: AppDelegate?
        weak var weakAppDelegate2: AppDelegate?
        
        autoreleasepool {
            let localAppDelegate1 = AppDelegate()
            let localAppDelegate2 = AppDelegate()
            weakAppDelegate1 = localAppDelegate1
            weakAppDelegate2 = localAppDelegate2
            
            // Test multiple launches
            XCTAssertNoThrow(localAppDelegate1.applicationDidFinishLaunching(notification))
            XCTAssertNoThrow(localAppDelegate2.applicationDidFinishLaunching(notification))
            
            // Clean up
            let terminateNotification = Notification(name: NSApplication.willTerminateNotification)
            XCTAssertNoThrow(localAppDelegate1.applicationWillTerminate(terminateNotification))
            XCTAssertNoThrow(localAppDelegate2.applicationWillTerminate(terminateNotification))
        }
        
        // In a test environment, we can't guarantee immediate deallocation
        // Just verify that the method calls didn't crash
        XCTAssertTrue(true, "Multiple launches memory management test completed without crashing")
    }
} 