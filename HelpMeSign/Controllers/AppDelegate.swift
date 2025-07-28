import Cocoa
import MetalKit
import ObjectiveC

// Note: LanguageManager, LanguageInfo, and CameraViewController should be available in the same target

@main
class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    private var launchQueue = DispatchQueue(label: "com.helpmesign.launch", qos: .userInitiated)
    private var hasLaunched = false
    
    // CRASH PREVENTION: Disable TouchBar globally
    override init() {
        super.init()
        // Disable TouchBar support completely
        UserDefaults.standard.set(false, forKey: "NSTouchBarEnabled")
        
        // Additional TouchBar and Core Animation crash prevention
        UserDefaults.standard.set(false, forKey: "NSTouchBarFinderEnabled")
        UserDefaults.standard.set(false, forKey: "NSTouchBarFinderSetNeedsUpdateOnMain")
        
        // Disable Core Animation for crash prevention
        UserDefaults.standard.set(false, forKey: "NSAnimationEnabled")
        UserDefaults.standard.set(false, forKey: "NSViewAnimationsEnabled")
        
        // Ensure we only launch once
        launchQueue = DispatchQueue(label: "com.helpmesign.launch", qos: .userInitiated)
        hasLaunched = false
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            // Only launch once to prevent race conditions
            guard !hasLaunched else {
                return
            }
            
            hasLaunched = true
            
            DispatchQueue.main.async {
                self.createSimpleWindow()
            }
        }
    }
    
    private func createSimpleWindow() {
        // Create a new window with crash prevention
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1024, height: 1024),
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        
        window.title = "HelpMeSign"
        
        // Center the window on screen
        window.center()
        
        // Aggressive crash prevention for main window
        window.toolbar = nil
        window.touchBar = nil
        window.isMovableByWindowBackground = false
        
        // Create the full MainWindowController with all functionality
        let mainWindowController = MainWindowController()
        
        window.contentViewController = mainWindowController
        
        // Set default language based on system preferences if no language is saved
        setDefaultLanguageIfNeeded()
        
        // Ensure window is centered and visible
        window.setFrameUsingName("MainWindow")
        window.setFrameAutosaveName("MainWindow")
        
        window.makeKeyAndOrderFront(nil)
    }
    
    private func setDefaultLanguageIfNeeded() {
        // TEMPORARY: Clear existing preference to force locale detection
        UserDefaults.standard.removeObject(forKey: "SelectedLanguage")
        
        // Only set default if no language preference is saved
        if UserDefaults.standard.string(forKey: "SelectedLanguage") == nil {
            // Get user's preferred languages from macOS system settings
            let preferredLanguages = Locale.preferredLanguages
            
            // Find the appropriate sign language based on system locale
            var defaultLanguage = getDefaultLanguageFromJSON() // Dynamic fallback
            
            for languageCode in preferredLanguages {
                let language = Locale(identifier: languageCode)
                let baseLanguage = language.language.languageCode?.identifier ?? ""
                let region = language.region?.identifier ?? ""
                
                // Check if we have a sign language that matches this language/region
                if let matchingLanguage = findSignLanguageForSystemLanguage(baseLanguage: baseLanguage, region: region) {
                    defaultLanguage = matchingLanguage
                    break
                }
            }
            
            // Use the detected language (or BSL as fallback)
            UserDefaults.standard.set(defaultLanguage, forKey: "SelectedLanguage")
            
            // Update the main window controller with the default language
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                if let mainWindow = NSApplication.shared.mainWindow,
                   let mainWindowController = mainWindow.contentViewController as? MainWindowController {
                    mainWindowController.changeLanguage(to: defaultLanguage)
                }
            }
        }
    }
    
    private func findSignLanguageForSystemLanguage(baseLanguage: String, region: String) -> String? {
        // Load available sign languages from JSON
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let jsonLanguages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return nil
        }
        
        // Check if any of our sign languages match the system language/region
        for languageDict in jsonLanguages {
            guard let country = languageDict["country"] as? String,
                  let signLanguageCode = languageDict["code"] as? String else { continue }
            
            // Check if the sign language's country code matches the region
            if country == region {
                return signLanguageCode
            }
        }
        
        return nil
    }
    
    private func getDefaultLanguageFromJSON() -> String {
        // Load languages from JSON and return the first available language code
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let jsonLanguages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return "BSL" // Minimal fallback if JSON loading fails
        }
        
        // Return the first language code from the JSON
        if let firstLanguage = jsonLanguages.first,
           let code = firstLanguage["code"] as? String {
            return code
        }
        
        return "BSL" // Minimal fallback if no languages in JSON
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            self.hasLaunched = false
        }
    }
    
    @IBAction func showPreferences(_ sender: Any?) {
        // Create a proper Preferences window with fixed size
        let preferencesWindow = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 600),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: false
        )
        
        // Basic window configuration
        preferencesWindow.title = "Preferences"
        preferencesWindow.isReleasedWhenClosed = false
        
        // Create Preferences view controller
        let preferencesVC = PreferencesViewController()
        
        // Set as content view controller
        preferencesWindow.contentViewController = preferencesVC
        preferencesWindow.delegate = self
        
        // Window size will be enforced in PreferencesViewController
        
        // Center the window on screen
        preferencesWindow.center()
        
        // Show the window
        preferencesWindow.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
    

    
    // MARK: - NSWindowDelegate
    func windowWillClose(_ notification: Notification) {
        // Window closing - no action needed
    }
    

}

