import Cocoa
import MetalKit
import ObjectiveC

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow?
    private let launchQueue = DispatchQueue(label: "com.helpmesign.launch", qos: .userInitiated)
    private var hasLaunched = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            // Only launch once to prevent race conditions
            guard !hasLaunched else {
                print("AppDelegate: Already launched, skipping duplicate call")
                return
            }
            
            print("AppDelegate: applicationDidFinishLaunching(_:) called")
            hasLaunched = true
            
            // Only create window if we're not in a test environment
            if !isRunningTests() {
                // Create window if it doesn't exist - do this synchronously for better testability
                if self.window == nil {
                    self.createAndSetupWindow()
                }
                
                // Ensure we're on the main thread for UI operations
                DispatchQueue.main.async {
                    // Make window visible
                    self.window?.makeKeyAndOrderFront(nil)
                    print("Window content view: \(self.window?.contentView != nil)")
                    print("Window content view controller: \(self.window?.contentViewController != nil)")
                }
            } else {
                print("AppDelegate: Running in test mode, skipping UI setup")
            }
        }
    }
    
    private func createAndSetupWindow() {
        // Only create window if we're not in a test environment
        guard !isRunningTests() else {
            print("AppDelegate: Skipping window creation in test mode")
            return
        }
        
        // Create a new window with proper configuration
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1024, height: 768),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        
        window.title = "HelpMeSign"
        window.center()
        
        // Create and set up a basic view controller for now
        print("Creating basic view controller for testing")
        let cameraVC = NSViewController()
        print("Successfully created view controller: \(type(of: cameraVC))")
        
        // Create a simple view for the view controller
        let view = NSView(frame: NSRect(x: 0, y: 0, width: 1024, height: 768))
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.white.cgColor
        cameraVC.view = view
        
        window.contentViewController = cameraVC
        print("Set view controller as content view controller")
        
        self.window = window
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            print("AppDelegate: applicationWillTerminate(_:) called")
            
            // Clean up window and view controller synchronously for better testability
            if let window = self.window {
                // Remove content view controller to break retain cycles
                window.contentViewController = nil
                // Close the window only if we're not in test mode
                if !isRunningTests() {
                    window.close()
                }
            }
            self.window = nil
            self.hasLaunched = false
        }
    }
    
    // Helper method to detect if we're running in a test environment
    private func isRunningTests() -> Bool {
        return NSClassFromString("XCTest") != nil
    }
}

