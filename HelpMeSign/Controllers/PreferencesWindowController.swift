import Cocoa

// MARK: - Preferences Window Controller
class PreferencesWindowController: NSWindowController {
    
    // MARK: - Singleton
    static let shared = PreferencesWindowController()
    
    // MARK: - Properties
    private var preferencesViewController: PreferencesViewController?
    
    // MARK: - Initialization
    private override init(window: NSWindow?) {
        super.init(window: window)
        setupWindow()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupWindow()
    }
    
    // MARK: - Setup
    private func setupWindow() {
        // Create window if not already created
        if window == nil {
            let preferencesWindow = NSWindow(
                contentRect: NSRect(x: 0, y: 0, width: 600, height: 600),
                styleMask: [.titled, .closable],
                backing: .buffered,
                defer: false
            )
            
            // Window configuration
            preferencesWindow.title = "Preferences"
            preferencesWindow.isReleasedWhenClosed = false
            preferencesWindow.delegate = self
            
            // Center the window on screen
            preferencesWindow.center()
            
            self.window = preferencesWindow
        }
    }
    
    // MARK: - Public Methods
    
    /// Show the preferences window
    override func showWindow(_ sender: Any?) {
        // Create preferences view controller if needed
        if preferencesViewController == nil {
            preferencesViewController = PreferencesViewController.createForPreferences()
            window?.contentViewController = preferencesViewController
        }
        
        // Show and activate the window
        window?.makeKeyAndOrderFront(sender)
        NSApp.activate(ignoringOtherApps: true)
    }
    
    /// Close the preferences window
    func closeWindow() {
        window?.close()
    }
    
    /// Check if preferences window is currently visible
    var isWindowVisible: Bool {
        return window?.isVisible ?? false
    }
}

// MARK: - NSWindowDelegate
extension PreferencesWindowController: NSWindowDelegate {
    
    func windowWillClose(_ notification: Notification) {
        // Clear the view controller reference when window closes
        preferencesViewController = nil
    }
    
    func windowShouldClose(_ sender: NSWindow) -> Bool {
        // Allow the window to close
        return true
    }
} 