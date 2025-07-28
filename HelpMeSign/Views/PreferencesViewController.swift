import Cocoa

class PreferencesViewController: NSViewController {
    
    // MARK: - UI Components
    private var scrollView: NSScrollView!
    private var contentView: NSView!
    private var searchField: NSSearchField!
    private var languageTableView: NSTableView!
    private var languageArrayController: NSArrayController!
    private var handPreferenceSegmentedControl: NSSegmentedControl!
    
    // MARK: - Data
    private var allLanguages: [LanguageInfo] = []
    private var filteredLanguages: [LanguageInfo] = []
    private var selectedLanguage: String = "ASL"
    private var selectedHand: String = "Right" // Default to right hand
    
    // MARK: - Struct for language data
    struct LanguageInfo {
        let code: String
        let name: String
        let flag: String
        let country: String
        let nativeName: String?
        let speakers: Int?
        let difficulty: String?
        
        init(code: String, name: String, flag: String, country: String, nativeName: String? = nil, speakers: Int? = nil, difficulty: String? = nil) {
            self.code = code
            self.name = name
            self.flag = flag
            self.country = country
            self.nativeName = nativeName
            self.speakers = speakers
            self.difficulty = difficulty
        }
    }
    
    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // CRASH PREVENTION: Disable layer backing on all views
        view.wantsLayer = false
        view.layer?.delegate = nil
        
        setupLanguages()
        setupUI()
        setupTableView()
        loadCurrentSelection()
    }
    
    // MARK: - Public Methods
    /// Initialize the preferences view controller without running locale detection
    static func createForPreferences() -> PreferencesViewController {
        let vc = PreferencesViewController()
        // Don't run locale detection for preferences window
        return vc
    }
    
    /// Initialize the preferences view controller with locale detection (for app startup)
    static func createWithLocaleDetection() -> PreferencesViewController {
        let vc = PreferencesViewController()
        // Run locale detection for app startup
        vc.runLocaleDetection()
        return vc
    }
    
    private func runLocaleDetection() {
        setDefaultLanguageBasedOnLocale()
    }
    
    // MARK: - Setup
    private func setupLanguages() {
        // Load languages from JSON file
        if let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let languages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
            
            allLanguages = languages.compactMap { language in
                guard let code = language["code"] as? String,
                      let name = language["name"] as? String,
                      let flag = language["flag"] as? String,
                      let country = language["country"] as? String else {
                    return nil
                }
                
                let nativeName = language["nativeName"] as? String
                let metadata = language["metadata"] as? [String: Any]
                let speakers = metadata?["speakers"] as? Int
                let difficulty = metadata?["difficulty"] as? String
                
                return LanguageInfo(
                    code: code,
                    name: name,
                    flag: flag,
                    country: country,
                    nativeName: nativeName,
                    speakers: speakers,
                    difficulty: difficulty
                )
            }
        } else {
            // Fallback to minimal essential languages if JSON fails
            allLanguages = [
                LanguageInfo(code: "BSL", name: "British Sign Language", flag: "🇬🇧", country: "GB", speakers: 150000, difficulty: "Intermediate")
            ]
            print("PreferencesViewController: JSON loading failed, using minimal fallback")
        }
        
        // Sort languages by name
        allLanguages.sort { $0.name < $1.name }
        filteredLanguages = allLanguages
        
        // Note: setDefaultLanguageBasedOnLocale() is now called separately via runLocaleDetection()
    }
    
    private func setDefaultLanguageBasedOnLocale() {
        // Get user's preferred languages from macOS system settings
        let preferredLanguages = Locale.preferredLanguages
        let currentLocale = Locale.current
        
        print("PreferencesViewController: System preferred languages: \(preferredLanguages)")
        print("PreferencesViewController: Current locale: \(currentLocale.identifier)")
        
        // Try to find a matching sign language based on system language preferences
        var detectedSignLanguage: String?
        
        for languageCode in preferredLanguages {
            let language = Locale(identifier: languageCode)
            let baseLanguage = language.language.languageCode?.identifier ?? ""
            let region = language.region?.identifier ?? ""
            
            print("PreferencesViewController: Checking language: \(baseLanguage), region: \(region)")
            
            // Check if we have a sign language that matches this language/region
            if let matchingLanguage = findSignLanguageForSystemLanguage(baseLanguage: baseLanguage, region: region) {
                detectedSignLanguage = matchingLanguage
                print("PreferencesViewController: Found matching sign language: \(matchingLanguage) for system language: \(languageCode)")
                break
            }
        }
        
        // Set the detected language or fallback to BSL
        if let detected = detectedSignLanguage, allLanguages.contains(where: { $0.code == detected }) {
            selectedLanguage = detected
            print("PreferencesViewController: Set default language to \(detected) based on system preferences")
        } else {
            selectedLanguage = "BSL"
            print("PreferencesViewController: No matching sign language found, defaulting to BSL")
        }
        
        // Save the default language to UserDefaults if no language is currently set
        if UserDefaults.standard.string(forKey: "SelectedLanguage") == nil {
            UserDefaults.standard.set(selectedLanguage, forKey: "SelectedLanguage")
            print("PreferencesViewController: Saved default language \(selectedLanguage) to UserDefaults")
        } else {
            // Use the saved language preference
            selectedLanguage = UserDefaults.standard.string(forKey: "SelectedLanguage") ?? "BSL"
            print("PreferencesViewController: Using saved language preference: \(selectedLanguage)")
        }
    }
    
    private func findSignLanguageForSystemLanguage(baseLanguage: String, region: String) -> String? {
        print("PreferencesViewController: Looking for match - baseLanguage: '\(baseLanguage)', region: '\(region)'")
        
        // Check if any of our sign languages match the system language/region
        for language in allLanguages {
            print("PreferencesViewController: Checking language: \(language.code) (\(language.name), country: \(language.country))")
            
            // Check if the sign language's country code matches the region
            if language.country == region {
                print("PreferencesViewController: Found exact region match: \(language.country) == \(region) -> \(language.code)")
                return language.code
            }
            
            // Check if the sign language name contains the base language (but be more specific)
            let signLanguageName = language.name.lowercased()
            let baseLanguageName = baseLanguage.lowercased()
            
            // Only match if it's a clear language match, not just partial string match
            if baseLanguageName == "en" && signLanguageName.contains("english") {
                print("PreferencesViewController: Found English language match: \(language.code)")
                return language.code
            }
            
            if baseLanguageName == "kn" && signLanguageName.contains("kannada") {
                print("PreferencesViewController: Found Kannada language match: \(language.code)")
                return language.code
            }
        }
        
        print("PreferencesViewController: No match found")
        return nil
    }
    
    private func setupUI() {
        // CRASH PREVENTION: Disable layer backing on all views
        view.wantsLayer = false
        view.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        
        // Create main container
        let containerView = NSView()
        containerView.translatesAutoresizingMaskIntoConstraints = false
        containerView.wantsLayer = false
        view.addSubview(containerView)
        
        // Title
        let titleLabel = NSTextField(labelWithString: "Select Sign Language")
        titleLabel.font = NSFont.boldSystemFont(ofSize: 24)
        titleLabel.textColor = NSColor.labelColor
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        titleLabel.wantsLayer = false
        containerView.addSubview(titleLabel)
        
        // Search field
        searchField = NSSearchField()
        searchField.placeholderString = "Search languages..."
        searchField.translatesAutoresizingMaskIntoConstraints = false
        searchField.wantsLayer = false
        searchField.target = self
        searchField.action = #selector(searchFieldChanged)
        containerView.addSubview(searchField)
        
        // Hand preference section
        let handPreferenceLabel = NSTextField(labelWithString: "Hand Preference")
        handPreferenceLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        handPreferenceLabel.textColor = NSColor.labelColor
        handPreferenceLabel.translatesAutoresizingMaskIntoConstraints = false
        handPreferenceLabel.wantsLayer = false
        containerView.addSubview(handPreferenceLabel)
        
        // Hand preference segmented control
        handPreferenceSegmentedControl = NSSegmentedControl(labels: ["Left Hand", "Right Hand"], trackingMode: .selectOne, target: self, action: #selector(handPreferenceChanged))
        handPreferenceSegmentedControl.translatesAutoresizingMaskIntoConstraints = false
        handPreferenceSegmentedControl.wantsLayer = false
        handPreferenceSegmentedControl.selectedSegment = 1 // Default to right hand
        containerView.addSubview(handPreferenceSegmentedControl)
        
        // Scroll view for table
        scrollView = NSScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.wantsLayer = false
        scrollView.hasVerticalScroller = true
        scrollView.hasHorizontalScroller = false
        scrollView.autohidesScrollers = true
        containerView.addSubview(scrollView)
        
        // Constraints
        NSLayoutConstraint.activate([
            containerView.topAnchor.constraint(equalTo: view.topAnchor, constant: 20),
            containerView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            containerView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            containerView.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -20),
            
            titleLabel.topAnchor.constraint(equalTo: containerView.topAnchor),
            titleLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            titleLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            
            searchField.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 20),
            searchField.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            searchField.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            
            handPreferenceLabel.topAnchor.constraint(equalTo: searchField.bottomAnchor, constant: 20),
            handPreferenceLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            
            handPreferenceSegmentedControl.topAnchor.constraint(equalTo: handPreferenceLabel.bottomAnchor, constant: 8),
            handPreferenceSegmentedControl.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            handPreferenceSegmentedControl.widthAnchor.constraint(equalToConstant: 200),
            
            scrollView.topAnchor.constraint(equalTo: handPreferenceSegmentedControl.bottomAnchor, constant: 15),
            scrollView.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: containerView.bottomAnchor)
        ])
    }
    
    private func setupTableView() {
        // Create table view
        languageTableView = NSTableView()
        languageTableView.translatesAutoresizingMaskIntoConstraints = false
        languageTableView.wantsLayer = false
        languageTableView.delegate = self
        languageTableView.dataSource = self
        languageTableView.style = .sourceList
        languageTableView.rowHeight = 60
        languageTableView.intercellSpacing = NSSize(width: 0, height: 5)
        
        // CRASH PREVENTION: Configure table view for safety
        languageTableView.allowsEmptySelection = true
        languageTableView.allowsMultipleSelection = false
        
        // Add columns
        let flagColumn = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("flag"))
        flagColumn.title = ""
        flagColumn.width = 50
        flagColumn.minWidth = 50
        flagColumn.maxWidth = 50
        
        let nameColumn = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("name"))
        nameColumn.title = "Language"
        nameColumn.width = 200
        nameColumn.minWidth = 150
        
        let codeColumn = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("code"))
        codeColumn.title = "Code"
        codeColumn.width = 80
        codeColumn.minWidth = 60
        codeColumn.maxWidth = 100
        
        let speakersColumn = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("speakers"))
        speakersColumn.title = "Speakers"
        speakersColumn.width = 100
        speakersColumn.minWidth = 80
        speakersColumn.maxWidth = 120
        
        let difficultyColumn = NSTableColumn(identifier: NSUserInterfaceItemIdentifier("difficulty"))
        difficultyColumn.title = "Level"
        difficultyColumn.width = 80
        difficultyColumn.minWidth = 60
        difficultyColumn.maxWidth = 100
        
        languageTableView.addTableColumn(flagColumn)
        languageTableView.addTableColumn(nameColumn)
        languageTableView.addTableColumn(codeColumn)
        languageTableView.addTableColumn(speakersColumn)
        languageTableView.addTableColumn(difficultyColumn)
        
        // Add to scroll view - this automatically handles constraints
        scrollView.documentView = languageTableView
    }
    
    private func loadCurrentSelection() {
        // Find and select the currently selected language
        if let index = filteredLanguages.firstIndex(where: { $0.code == selectedLanguage }) {
            languageTableView.selectRowIndexes(IndexSet(integer: index), byExtendingSelection: false)
        }
        // Don't send notification when window opens, only when user selects a different language
    }
    
    // MARK: - Actions
    @objc private func searchFieldChanged() {
        let searchText = searchField.stringValue.lowercased()
        
        if searchText.isEmpty {
            filteredLanguages = allLanguages
        } else {
            filteredLanguages = allLanguages.filter { language in
                language.name.lowercased().contains(searchText) ||
                language.code.lowercased().contains(searchText) ||
                language.country.lowercased().contains(searchText) ||
                (language.nativeName?.lowercased().contains(searchText) ?? false)
            }
        }
        
        languageTableView.reloadData()
        loadCurrentSelection()
    }
    
    @objc private func handPreferenceChanged() {
        let selectedSegment = handPreferenceSegmentedControl.selectedSegment
        selectedHand = selectedSegment == 0 ? "Left" : "Right"
        
        print("Hand preference changed to: \(selectedHand)")
        
        // Post notification for hand preference change
        NotificationCenter.default.post(
            name: NSNotification.Name("HandPreferenceChanged"),
            object: nil,
            userInfo: ["handPreference": selectedHand]
        )
    }
    
    private func selectLanguage(_ languageCode: String) {
        // Only update if language actually changed
        if selectedLanguage != languageCode {
            selectedLanguage = languageCode
            
            // Update button appearance
            languageTableView.reloadData()
            
            // Save to UserDefaults
            UserDefaults.standard.set(languageCode, forKey: "SelectedLanguage")
            
            // Post notification
            NotificationCenter.default.post(
                name: NSNotification.Name("LanguageChanged"),
                object: nil,
                userInfo: ["languageCode": languageCode]
            )
            
            // Also update the main window's camera view controller directly
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
                if let mainWindow = NSApplication.shared.mainWindow,
                   let cameraVC = mainWindow.contentViewController as? CameraViewController {
                    cameraVC.changeLanguage(to: languageCode)
                }
            }
            
            print("Language selected: \(languageCode)")
        } else {
            print("Language already selected: \(languageCode), no update needed")
        }
    }
}

// MARK: - NSTableViewDataSource
extension PreferencesViewController: NSTableViewDataSource {
    func numberOfRows(in tableView: NSTableView) -> Int {
        return filteredLanguages.count
    }
}

// MARK: - NSTableViewDelegate
extension PreferencesViewController: NSTableViewDelegate {
    func tableView(_ tableView: NSTableView, viewFor tableColumn: NSTableColumn?, row: Int) -> NSView? {
        guard row < filteredLanguages.count else { return nil }
        
        let language = filteredLanguages[row]
        let isSelected = language.code == selectedLanguage
        
        switch tableColumn?.identifier {
        case NSUserInterfaceItemIdentifier("flag"):
            let flagLabel = NSTextField(labelWithString: language.flag)
            flagLabel.font = NSFont.systemFont(ofSize: 24)
            flagLabel.alignment = .center
            flagLabel.isEditable = false
            flagLabel.isBordered = false
            flagLabel.backgroundColor = NSColor.clear
            flagLabel.wantsLayer = false
            return flagLabel
            
        case NSUserInterfaceItemIdentifier("name"):
            let nameLabel = NSTextField(labelWithString: language.name)
            nameLabel.font = NSFont.systemFont(ofSize: 14, weight: isSelected ? .semibold : .regular)
            nameLabel.textColor = isSelected ? NSColor.controlAccentColor : NSColor.labelColor
            nameLabel.isEditable = false
            nameLabel.isBordered = false
            nameLabel.backgroundColor = NSColor.clear
            nameLabel.wantsLayer = false
            
            if let nativeName = language.nativeName {
                nameLabel.stringValue = "\(language.name)\n\(nativeName)"
            }
            
            return nameLabel
            
        case NSUserInterfaceItemIdentifier("code"):
            let codeLabel = NSTextField(labelWithString: language.code)
            codeLabel.font = NSFont.monospacedSystemFont(ofSize: 12, weight: .medium)
            codeLabel.textColor = isSelected ? NSColor.controlAccentColor : NSColor.secondaryLabelColor
            codeLabel.alignment = .center
            codeLabel.isEditable = false
            codeLabel.isBordered = false
            codeLabel.backgroundColor = NSColor.clear
            codeLabel.wantsLayer = false
            return codeLabel
            
        case NSUserInterfaceItemIdentifier("speakers"):
            let speakersText = language.speakers != nil ? formatSpeakers(language.speakers!) : "Unknown"
            let speakersLabel = NSTextField(labelWithString: speakersText)
            speakersLabel.font = NSFont.systemFont(ofSize: 12)
            speakersLabel.textColor = NSColor.secondaryLabelColor
            speakersLabel.alignment = .center
            speakersLabel.isEditable = false
            speakersLabel.isBordered = false
            speakersLabel.backgroundColor = NSColor.clear
            speakersLabel.wantsLayer = false
            return speakersLabel
            
        case NSUserInterfaceItemIdentifier("difficulty"):
            let difficultyText = language.difficulty ?? "Unknown"
            let difficultyLabel = NSTextField(labelWithString: difficultyText)
            difficultyLabel.font = NSFont.systemFont(ofSize: 12)
            difficultyLabel.textColor = getDifficultyColor(difficultyText)
            difficultyLabel.alignment = .center
            difficultyLabel.isEditable = false
            difficultyLabel.isBordered = false
            difficultyLabel.backgroundColor = NSColor.clear
            difficultyLabel.wantsLayer = false
            return difficultyLabel
            
        default:
            return nil
        }
    }
    
    func tableViewSelectionDidChange(_ notification: Notification) {
        // CRASH PREVENTION: Wrap in async to prevent Core Animation issues
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            let selectedRow = self.languageTableView.selectedRow
            if selectedRow >= 0 && selectedRow < self.filteredLanguages.count {
                let selectedLanguage = self.filteredLanguages[selectedRow]
                self.selectLanguage(selectedLanguage.code)
            }
        }
    }
    
    // MARK: - Helper Methods
    private func formatSpeakers(_ count: Int) -> String {
        if count >= 1_000_000 {
            return String(format: "%.1fM", Double(count) / 1_000_000)
        } else if count >= 1_000 {
            return String(format: "%.1fK", Double(count) / 1_000)
        } else {
            return "\(count)"
        }
    }
    
    private func getDifficultyColor(_ difficulty: String) -> NSColor {
        switch difficulty.lowercased() {
        case "beginner":
            return NSColor.systemGreen
        case "intermediate":
            return NSColor.systemOrange
        case "advanced":
            return NSColor.systemRed
        default:
            return NSColor.secondaryLabelColor
        }
    }
} 
