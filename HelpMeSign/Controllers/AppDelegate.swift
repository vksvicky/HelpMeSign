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
        
        // Create the full CameraViewController with all functionality
        print("AppDelegate: Creating full CameraViewController")
        let cameraVC = CameraViewController()
        print("AppDelegate: CameraViewController created successfully")
        
        window.contentViewController = cameraVC
        
        // Set default language based on system preferences if no language is saved
        setDefaultLanguageIfNeeded()
        
        // Ensure window is centered and visible
        window.setFrameUsingName("MainWindow")
        window.setFrameAutosaveName("MainWindow")
        
        print("AppDelegate: Full CameraViewController loaded with camera, AI, and translation functionality")
        window.makeKeyAndOrderFront(nil)
        
        print("AppDelegate: Window with CameraViewController created and made visible")
    }
    
    private func setDefaultLanguageIfNeeded() {
        // TEMPORARY: Clear existing preference to force locale detection
        UserDefaults.standard.removeObject(forKey: "SelectedLanguage")
        print("AppDelegate: Cleared existing language preference to force locale detection")
        
        // Only set default if no language preference is saved
        if UserDefaults.standard.string(forKey: "SelectedLanguage") == nil {
            print("AppDelegate: No saved language preference, setting default based on system")
            
            // Get user's preferred languages from macOS system settings
            let preferredLanguages = Locale.preferredLanguages
            print("AppDelegate: System preferred languages: \(preferredLanguages)")
            
            // Find the appropriate sign language based on system locale
            var defaultLanguage = getDefaultLanguageFromJSON() // Dynamic fallback
            
            for languageCode in preferredLanguages {
                let language = Locale(identifier: languageCode)
                let baseLanguage = language.language.languageCode?.identifier ?? ""
                let region = language.region?.identifier ?? ""
                
                print("AppDelegate: Checking language: \(baseLanguage), region: \(region)")
                
                // Check if we have a sign language that matches this language/region
                if let matchingLanguage = findSignLanguageForSystemLanguage(baseLanguage: baseLanguage, region: region) {
                    defaultLanguage = matchingLanguage
                    print("AppDelegate: Found matching sign language: \(matchingLanguage) for system language: \(languageCode)")
                    break
                }
            }
            
            // Use the detected language (or BSL as fallback)
            print("AppDelegate: Using detected language: \(defaultLanguage)")
            UserDefaults.standard.set(defaultLanguage, forKey: "SelectedLanguage")
            print("AppDelegate: Force set default language to \(defaultLanguage) for debugging")
            
            // Update the camera view controller with the default language
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                if let mainWindow = NSApplication.shared.mainWindow,
                   let cameraVC = mainWindow.contentViewController as? CameraViewController {
                    cameraVC.changeLanguage(to: defaultLanguage)
                    print("AppDelegate: Updated camera view controller with default language: \(defaultLanguage)")
                }
            }
        } else {
            print("AppDelegate: Using saved language preference: \(UserDefaults.standard.string(forKey: "SelectedLanguage") ?? "unknown")")
        }
    }
    
    private func findSignLanguageForSystemLanguage(baseLanguage: String, region: String) -> String? {
        print("AppDelegate: Looking for match - baseLanguage: '\(baseLanguage)', region: '\(region)'")
        
        // Load available sign languages from JSON
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let jsonLanguages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            print("AppDelegate: Failed to load languages.json for locale detection")
            return nil
        }
        
        // Check if any of our sign languages match the system language/region
        for languageDict in jsonLanguages {
            guard let country = languageDict["country"] as? String,
                  let signLanguageCode = languageDict["code"] as? String else { continue }
            
            print("AppDelegate: Comparing with country: '\(country)', signLanguage: '\(signLanguageCode)'")
            // Check if the sign language's country code matches the region
            if country == region {
                print("AppDelegate: Found exact region match: \(country) == \(region) -> \(signLanguageCode)")
                return signLanguageCode
            }
        }
        
        print("AppDelegate: No region match found")
        return nil
    }
    
    private func getDefaultLanguageFromJSON() -> String {
        // Load languages from JSON and return the first available language code
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let jsonLanguages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            print("AppDelegate: Failed to load languages.json for default language")
            return "BSL" // Minimal fallback if JSON loading fails
        }
        
        // Return the first language code from the JSON
        if let firstLanguage = jsonLanguages.first,
           let code = firstLanguage["code"] as? String {
            print("AppDelegate: Using first language from JSON as default: \(code)")
            return code
        }
        
        print("AppDelegate: No languages found in JSON, using BSL as fallback")
        return "BSL" // Minimal fallback if no languages in JSON
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            print("AppDelegate: applicationWillTerminate(_:) called")
            self.hasLaunched = false
        }
    }
    
    @IBAction func showPreferences(_ sender: Any?) {
        print("AppDelegate: Creating Preferences window with crash prevention")
        
        // Create a proper Preferences window with fixed size
        let preferencesWindow = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 600),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: false
        )
        
        // CRASH PREVENTION: Disable problematic features
        preferencesWindow.toolbar = nil
        preferencesWindow.touchBar = nil
        preferencesWindow.isMovableByWindowBackground = false
        preferencesWindow.standardWindowButton(.miniaturizeButton)?.isHidden = true
        preferencesWindow.standardWindowButton(.zoomButton)?.isHidden = true
        
        // Prevent window resizing by using fixed style mask
        preferencesWindow.styleMask = [.titled, .closable]
        preferencesWindow.title = "Preferences"
        preferencesWindow.isReleasedWhenClosed = false
        
        // Create Preferences view controller
        let preferencesVC = PreferencesViewController()
        preferencesVC.view.wantsLayer = false
        
        // Set as content view controller
        preferencesWindow.contentViewController = preferencesVC
        preferencesWindow.delegate = self
        
        // Window size will be enforced in PreferencesViewController
        
        // Center the window on screen
        preferencesWindow.center()
        
        // Show the window
        preferencesWindow.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        
        print("AppDelegate: Preferences window created and shown")
    }
    

    
    // MARK: - NSWindowDelegate
    func windowWillClose(_ notification: Notification) {
        // CRASH PREVENTION: Simple cleanup when preferences window closes
        // Don't modify properties here to avoid memory management conflicts
        print("AppDelegate: Preferences window closing, cleanup complete")
    }
    

}

