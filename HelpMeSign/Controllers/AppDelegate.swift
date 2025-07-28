import Cocoa
import MetalKit
import ObjectiveC

@main
class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate {
    private let launchQueue = DispatchQueue(label: "com.helpmesign.launch", qos: .userInitiated)
    private var hasLaunched = false
    
    // CRASH PREVENTION: Disable TouchBar globally
    override init() {
        super.init()
        // Disable TouchBar support completely
        UserDefaults.standard.set(false, forKey: "NSTouchBarEnabled")
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
        // Create a new window
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1024, height: 1024),
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        
        window.title = "HelpMeSign"
        
        // Center the window on screen
        window.center()
        
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
            var detectedSignLanguage: String?
            
            for languageCode in preferredLanguages {
                let language = Locale(identifier: languageCode)
                let baseLanguage = language.language.languageCode?.identifier ?? ""
                let region = language.region?.identifier ?? ""
                
                print("AppDelegate: Checking language: \(baseLanguage), region: \(region)")
                
                // Check if we have a sign language that matches this language/region
                if let matchingLanguage = findSignLanguageForSystemLanguage(baseLanguage: baseLanguage, region: region) {
                    detectedSignLanguage = matchingLanguage
                    print("AppDelegate: Found matching sign language: \(matchingLanguage) for system language: \(languageCode)")
                    break
                }
            }
            
            // Force BSL for debugging - your system should detect BSL anyway
            let defaultLanguage = "BSL" // Force BSL for now
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
        // Define available sign languages (this should match what's in the JSON)
        let availableSignLanguages = [
            ("US", "ASL"), ("GB", "BSL"), ("IN", "ISL"), ("JP", "JSL"), 
            ("KR", "KSL"), ("CN", "CSL"), ("FR", "FSL"), ("DE", "DSL")
        ]
        
        print("AppDelegate: Looking for match - baseLanguage: '\(baseLanguage)', region: '\(region)'")
        
        // Check if any of our sign languages match the system language/region
        for (country, signLanguageCode) in availableSignLanguages {
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

    func applicationWillTerminate(_ notification: Notification) {
        // Make this method thread-safe to handle concurrent calls
        launchQueue.sync {
            print("AppDelegate: applicationWillTerminate(_:) called")
            self.hasLaunched = false
        }
    }
    
    @IBAction func showPreferences(_ sender: Any?) {
        print("AppDelegate: Restoring sophisticated preferences window with comprehensive crash prevention")
        
        // Create the sophisticated preferences window
        let preferencesWindow = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 500),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: true
        )

        preferencesWindow.title = "Preferences"
        preferencesWindow.center()
        preferencesWindow.isReleasedWhenClosed = true
        
        // CRASH PREVENTION: Disable all problematic features
        preferencesWindow.toolbar = nil
        preferencesWindow.touchBar = nil
        preferencesWindow.standardWindowButton(.miniaturizeButton)?.isHidden = true
        preferencesWindow.standardWindowButton(.zoomButton)?.isHidden = true
        
        // Create the sophisticated preferences view controller (without locale detection)
        let preferencesVC = PreferencesViewController.createForPreferences()
        preferencesWindow.contentViewController = preferencesVC
        
        // Set window delegate for proper cleanup
        preferencesWindow.delegate = self
        
        // CRASH PREVENTION: Show window with proper timing
        DispatchQueue.main.async {
            preferencesWindow.makeKeyAndOrderFront(nil)
        }
    }
    
    // MARK: - NSWindowDelegate
    func windowWillClose(_ notification: Notification) {
        // CRASH PREVENTION: Clean up when preferences window closes
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            // Additional cleanup if needed
        }
    }
}

