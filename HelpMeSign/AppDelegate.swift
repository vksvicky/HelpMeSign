import Cocoa

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        if let window = NSApplication.shared.windows.first {
            window.setFrame(NSRect(x: window.frame.origin.x, y: window.frame.origin.y, width: 1024, height: 1024), display: true)
            window.styleMask.remove(.resizable)
        }
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Insert code here to tear down your application
    }
}
