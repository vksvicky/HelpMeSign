import Cocoa

class WritingSystemSelectorView: NSView {
    
    // MARK: - Properties
    private var writingSystems: [String: String] = [:]
    private var writingSystemOrder: [String] = []
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
    func configure(with writingSystems: [String: String], order: [String]? = nil, selectedSystem: String? = nil, onSelectionChanged: @escaping (String) -> Void) {
        self.writingSystems = writingSystems
        self.selectedSystem = selectedSystem
        self.onSelectionChanged = onSelectionChanged
        
        // Store the order if provided, otherwise use the keys in their original order
        self.writingSystemOrder = order ?? Array(writingSystems.keys)
        
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
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Configure segmented control
        segmentedControl.segmentStyle = .rounded
        segmentedControl.trackingMode = .selectOne
        segmentedControl.target = self
        segmentedControl.action = #selector(segmentedControlChanged)
        segmentedControl.translatesAutoresizingMaskIntoConstraints = false
        
        // Ensure the control is properly configured for interaction
        segmentedControl.isEnabled = true
        
        // Add a gesture recognizer as a backup
        let clickGesture = NSClickGestureRecognizer(target: self, action: #selector(handleClick(_:)))
        segmentedControl.addGestureRecognizer(clickGesture)
        
        // Configure stack view
        stackView.orientation = .horizontal
        stackView.spacing = 8
        stackView.alignment = .centerY
        stackView.translatesAutoresizingMaskIntoConstraints = false
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
        let systems = writingSystemOrder
        
        segmentedControl.segmentCount = systems.count
        segmentedControl.isEnabled = true
        
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
        let systems = writingSystemOrder
        
        guard selectedIndex >= 0 && selectedIndex < systems.count else { 
            return 
        }
        
        let selectedSystem = systems[selectedIndex]
        
        // Update the internal state
        self.selectedSystem = selectedSystem
        
        // Call the callback on the main thread
        DispatchQueue.main.async { [weak self] in
            self?.onSelectionChanged?(selectedSystem)
        }
    }
    
    @objc private func handleClick(_ gesture: NSClickGestureRecognizer) {
        // Calculate which segment was actually clicked
        let location = gesture.location(in: segmentedControl)
        let segmentWidth = segmentedControl.bounds.width / CGFloat(segmentedControl.segmentCount)
        let clickedIndex = Int(location.x / segmentWidth)
        let systems = writingSystemOrder
        
        guard clickedIndex >= 0 && clickedIndex < systems.count else { 
            return 
        }
        
        let selectedSystem = systems[clickedIndex]
        
        // Update the segmented control selection
        segmentedControl.selectedSegment = clickedIndex
        self.selectedSystem = selectedSystem
        
        DispatchQueue.main.async { [weak self] in
            self?.onSelectionChanged?(selectedSystem)
        }
    }
} 