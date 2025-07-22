import Cocoa
import MetalKit
import ObjectiveC
@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        print("AppDelegate: applicationDidFinishLaunching(_:) called")
        for window in NSApplication.shared.windows {
            print("Window title: \(window.title)")
            print("Window controller: \(type(of: window.windowController))")
            if let contentVC = window.contentViewController {
                print("Content view controller: \(type(of: contentVC))")
            } else {
                print("No content view controller")
            }
        }
        // Use CameraViewController
        print("Creating CameraViewController programmatically")
        let cameraVC = CameraViewController()
        print("Successfully created CameraViewController: \(type(of: cameraVC))")
        if let window = NSApplication.shared.windows.first {
            window.contentViewController = cameraVC
            print("Set CameraViewController as content view controller")
            window.makeKeyAndOrderFront(nil)
            print("Window content view: \(window.contentView != nil)")
            print("Window content view controller: \(window.contentViewController != nil)")
        }
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Insert code here to tear down your application
    }
}

