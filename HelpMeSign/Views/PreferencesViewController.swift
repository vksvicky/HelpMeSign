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
        setupLanguages()
        setupUI()
        setupTableView()
        loadCurrentSelection()
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
            // Fallback to hardcoded languages if JSON fails
            allLanguages = [
                LanguageInfo(code: "ASL", name: "American Sign Language", flag: "🇺🇸", country: "US", speakers: 500000, difficulty: "Intermediate"),
                LanguageInfo(code: "BSL", name: "British Sign Language", flag: "🇬🇧", country: "GB", speakers: 150000, difficulty: "Intermediate"),
                LanguageInfo(code: "ISL", name: "Indian Sign Language", flag: "🇮🇳", country: "IN", speakers: 2000000, difficulty: "Beginner"),
                LanguageInfo(code: "JSL", name: "Japanese Sign Language", flag: "🇯🇵", country: "JP", speakers: 300000, difficulty: "Advanced"),
                LanguageInfo(code: "KSL", name: "Korean Sign Language", flag: "🇰🇷", country: "KR", speakers: 250000, difficulty: "Intermediate")
            ]
        }
        
        // Sort languages by name
        allLanguages.sort { $0.name < $1.name }
        filteredLanguages = allLanguages
    }
    
    private func setupUI() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        
        // Create main container
        let containerView = NSView()
        containerView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(containerView)
        
        // Title
        let titleLabel = NSTextField(labelWithString: "Select Sign Language")
        titleLabel.font = NSFont.boldSystemFont(ofSize: 24)
        titleLabel.textColor = NSColor.labelColor
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        containerView.addSubview(titleLabel)
        
        // Search field
        searchField = NSSearchField()
        searchField.placeholderString = "Search languages..."
        searchField.translatesAutoresizingMaskIntoConstraints = false
        searchField.target = self
        searchField.action = #selector(searchFieldChanged)
        containerView.addSubview(searchField)
        
        // Hand preference section
        let handPreferenceLabel = NSTextField(labelWithString: "Hand Preference")
        handPreferenceLabel.font = NSFont.systemFont(ofSize: 16, weight: .medium)
        handPreferenceLabel.textColor = NSColor.labelColor
        handPreferenceLabel.translatesAutoresizingMaskIntoConstraints = false
        containerView.addSubview(handPreferenceLabel)
        
        // Hand preference segmented control
        handPreferenceSegmentedControl = NSSegmentedControl(labels: ["Left Hand", "Right Hand"], trackingMode: .selectOne, target: self, action: #selector(handPreferenceChanged))
        handPreferenceSegmentedControl.translatesAutoresizingMaskIntoConstraints = false
        handPreferenceSegmentedControl.selectedSegment = 1 // Default to right hand
        containerView.addSubview(handPreferenceSegmentedControl)
        
        // Scroll view for table
        scrollView = NSScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
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
        languageTableView.delegate = self
        languageTableView.dataSource = self
        languageTableView.selectionHighlightStyle = .sourceList
        languageTableView.rowHeight = 60
        languageTableView.intercellSpacing = NSSize(width: 0, height: 5)
        
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
            
            // Post notification
            NotificationCenter.default.post(
                name: NSNotification.Name("LanguageChanged"),
                object: nil,
                userInfo: ["languageCode": languageCode]
            )
            
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
            return flagLabel
            
        case NSUserInterfaceItemIdentifier("name"):
            let nameLabel = NSTextField(labelWithString: language.name)
            nameLabel.font = NSFont.systemFont(ofSize: 14, weight: isSelected ? .semibold : .regular)
            nameLabel.textColor = isSelected ? NSColor.controlAccentColor : NSColor.labelColor
            nameLabel.isEditable = false
            nameLabel.isBordered = false
            nameLabel.backgroundColor = NSColor.clear
            
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
            return difficultyLabel
            
        default:
            return nil
        }
    }
    
    func tableViewSelectionDidChange(_ notification: Notification) {
        let selectedRow = languageTableView.selectedRow
        if selectedRow >= 0 && selectedRow < filteredLanguages.count {
            let selectedLanguage = filteredLanguages[selectedRow]
            self.selectLanguage(selectedLanguage.code)
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
