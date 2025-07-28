import Cocoa

class SimplePreferencesViewController: NSViewController {
    
    private var languagePopUp: NSPopUpButton!
    private var handPreferenceSegmentedControl: NSSegmentedControl!
    
    override func loadView() {
        let view = NSView(frame: NSRect(x: 0, y: 0, width: 400, height: 300))
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        
        self.view = view
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    private func setupUI() {
        // Title
        let titleLabel = NSTextField(labelWithString: "Preferences")
        titleLabel.font = NSFont.systemFont(ofSize: 18, weight: .semibold)
        titleLabel.frame = NSRect(x: 20, y: 260, width: 360, height: 30)
        view.addSubview(titleLabel)
        
        // Language selection
        let languageLabel = NSTextField(labelWithString: "Language:")
        languageLabel.frame = NSRect(x: 20, y: 200, width: 100, height: 20)
        view.addSubview(languageLabel)
        
        languagePopUp = NSPopUpButton(frame: NSRect(x: 130, y: 195, width: 150, height: 30))
        languagePopUp.addItems(withTitles: ["ASL", "BSL", "ISL", "JSL", "KSL"])
        languagePopUp.target = self
        languagePopUp.action = #selector(languageChanged)
        view.addSubview(languagePopUp)
        
        // Hand preference
        let handLabel = NSTextField(labelWithString: "Hand Preference:")
        handLabel.frame = NSRect(x: 20, y: 140, width: 100, height: 20)
        view.addSubview(handLabel)
        
        handPreferenceSegmentedControl = NSSegmentedControl(frame: NSRect(x: 130, y: 135, width: 150, height: 30))
        handPreferenceSegmentedControl.segmentCount = 2
        handPreferenceSegmentedControl.setLabel("Left", forSegment: 0)
        handPreferenceSegmentedControl.setLabel("Right", forSegment: 1)
        handPreferenceSegmentedControl.selectedSegment = 1 // Default to Right
        handPreferenceSegmentedControl.target = self
        handPreferenceSegmentedControl.action = #selector(handPreferenceChanged)
        view.addSubview(handPreferenceSegmentedControl)
        
        // Load current settings
        loadCurrentSettings()
    }
    
    private func loadCurrentSettings() {
        // Load current language
        let currentLanguage = UserDefaults.standard.string(forKey: "SelectedLanguage") ?? "ASL"
        if let index = languagePopUp.itemTitles.firstIndex(of: currentLanguage) {
            languagePopUp.selectItem(at: index)
        }
        
        // Load current hand preference
        let currentHand = UserDefaults.standard.string(forKey: "SelectedHand") ?? "Right"
        handPreferenceSegmentedControl.selectedSegment = currentHand == "Left" ? 0 : 1
    }
    
    @objc private func languageChanged() {
        let selectedLanguage = languagePopUp.selectedItem?.title ?? "ASL"
        UserDefaults.standard.set(selectedLanguage, forKey: "SelectedLanguage")
        
        // Update main window after a delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            if let mainWindow = NSApplication.shared.windows.first(where: { $0.title == "HelpMeSign" }),
               let mainWindowController = mainWindow.contentViewController as? MainWindowController {
                mainWindowController.changeLanguage(to: selectedLanguage)
            }
        }
    }
    
    @objc private func handPreferenceChanged() {
        let selectedHand = handPreferenceSegmentedControl.selectedSegment == 0 ? "Left" : "Right"
        UserDefaults.standard.set(selectedHand, forKey: "SelectedHand")
    }
} 