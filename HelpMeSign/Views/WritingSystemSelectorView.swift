import Cocoa

class WritingSystemSelectorView: NSView {
    
    // MARK: - Properties
    private var writingSystems: [String: String] = [:]
    private var selectedSystem: String?
    private var onSelectionChanged: ((String) -> Void)?
    
    private let titleLabel = NSTextField(labelWithString: "Writing System:")
    private let segmentedControl = NSSegmentedControl()
    private let stackView = NSStackView()
    
    // MARK: - Initialization
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    // MARK: - Public Methods
    func configure(with writingSystems: [String: String], selectedSystem: String? = nil, onSelectionChanged: @escaping (String) -> Void) {
        self.writingSystems = writingSystems
        self.selectedSystem = selectedSystem
        self.onSelectionChanged = onSelectionChanged
        
        updateSegmentedControl()
    }
    
    func setSelectedSystem(_ system: String) {
        selectedSystem = system
        updateSegmentedControl()
    }
    
    // MARK: - Private Methods
    private func setupUI() {
        translatesAutoresizingMaskIntoConstraints = false
        
        // Configure title label
        titleLabel.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        titleLabel.textColor = NSColor.labelColor
        
        // Configure segmented control
        segmentedControl.segmentStyle = .rounded
        segmentedControl.target = self
        segmentedControl.action = #selector(segmentedControlChanged)
        
        // Configure stack view
        stackView.orientation = .horizontal
        stackView.spacing = 8
        stackView.alignment = .centerY
        stackView.addArrangedSubview(titleLabel)
        stackView.addArrangedSubview(segmentedControl)
        
        addSubview(stackView)
        
        // Setup constraints
        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: topAnchor),
            stackView.leadingAnchor.constraint(equalTo: leadingAnchor),
            stackView.trailingAnchor.constraint(equalTo: trailingAnchor),
            stackView.bottomAnchor.constraint(equalTo: bottomAnchor),
            
            heightAnchor.constraint(equalToConstant: 32)
        ])
    }
    
    private func updateSegmentedControl() {
        let systems = Array(writingSystems.keys)
        segmentedControl.segmentCount = systems.count
        
        for (index, system) in systems.enumerated() {
            let displayName = getDisplayName(for: system)
            segmentedControl.setLabel(displayName, forSegment: index)
            segmentedControl.setWidth(80, forSegment: index)
            
            if system == selectedSystem {
                segmentedControl.setSelected(true, forSegment: index)
            }
        }
    }
    
    private func getDisplayName(for system: String) -> String {
        switch system.lowercased() {
        case "hiragana":
            return "ひらがな"
        case "katakana":
            return "カタカナ"
        case "kanji":
            return "漢字"
        case "devanagari":
            return "देवनागरी"
        case "tamil":
            return "தமிழ்"
        case "telugu":
            return "తెలుగు"
        case "bengali":
            return "বাংলা"
        case "gurmukhi":
            return "ਗੁਰਮੁਖੀ"
        case "gujarati":
            return "ગુજરાતી"
        case "odia":
            return "ଓଡ଼ିଆ"
        case "malayalam":
            return "മലയാളം"
        case "kannada":
            return "ಕನ್ನಡ"
        default:
            return system.capitalized
        }
    }
    
    @objc private func segmentedControlChanged() {
        let selectedIndex = segmentedControl.selectedSegment
        let systems = Array(writingSystems.keys)
        
        guard selectedIndex >= 0 && selectedIndex < systems.count else { return }
        
        let selectedSystem = systems[selectedIndex]
        self.selectedSystem = selectedSystem
        onSelectionChanged?(selectedSystem)
    }
} 