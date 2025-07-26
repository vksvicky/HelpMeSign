import Cocoa
import MetalKit
import ObjectiveC

@main
class AppDelegate: NSObject, NSApplicationDelegate {
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
            
            // Create a simple window with visible content
            print("AppDelegate: Creating simple window with visible content")
            
            DispatchQueue.main.async {
                self.createSimpleWindow()
            }
        }
    }
    
    private func createSimpleWindow() {
        // Create a new window
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1024, height: 768),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        
        window.title = "HelpMeSign"
        window.center()
        
        // Create the full CameraViewController with all functionality
        print("AppDelegate: Creating full CameraViewController")
        let cameraVC = CameraViewController()
        print("AppDelegate: CameraViewController created successfully")
        
        window.contentViewController = cameraVC
        
        // Set fixed window size - not resizable
        window.styleMask = [.titled, .closable, .miniaturizable]
        window.setFrame(NSRect(x: 0, y: 0, width: 1024, height: 1024), display: true)
        
        print("AppDelegate: Full CameraViewController loaded with camera, AI, and translation functionality")
        window.makeKeyAndOrderFront(nil)
        
        print("AppDelegate: Window with CameraViewController created and made visible")
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            print("AppDelegate: applicationWillTerminate(_:) called")
            self.hasLaunched = false
        }
    }
}

