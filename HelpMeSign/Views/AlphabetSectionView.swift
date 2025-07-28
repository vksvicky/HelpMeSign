import Cocoa

class AlphabetSectionView: NSView {
    
    // MARK: - UI Elements
    private var divider: NSView!
    private var alphabetBar: AlphabetBarView!
    private var writingSystemSelectorView: WritingSystemSelectorView?
    private var currentWritingSystem: String?
    
    // MARK: - Callbacks
    var onLetterClicked: ((String) -> Void)?
    var onWritingSystemChanged: ((String) -> Void)?
    
    // MARK: - Initialization
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        setupView()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupView()
    }
    
    private func setupView() {
        wantsLayer = true
        layer?.backgroundColor = NSColor.clear.cgColor
        
        setupDivider()
        setupAlphabetBar()
    }
    
    // MARK: - Divider Setup
    private func setupDivider() {
        let width = bounds.width
        let height = bounds.height
        
        // Add divider at the top
        divider = NSView(frame: NSRect(x: width * 0.15, y: height - 2, width: width * 0.7, height: 2))
        divider.wantsLayer = true
        divider.layer?.backgroundColor = NSColor.systemGray.withAlphaComponent(0.13).cgColor
        addSubview(divider)
    }
    
    // MARK: - Alphabet Bar Setup
    private func setupAlphabetBar() {
        let width = bounds.width
        let height = bounds.height
        
        // Add alphabet bar inside the bottom section
        alphabetBar = AlphabetBarView(frame: NSRect(x: 0, y: 0, width: width, height: height))
        addSubview(alphabetBar)
    }
    
    // MARK: - Public Methods
    func reloadAlphabetForLanguage(_ languageCode: String) {
        // Check if this language has multiple writing systems
        if let writingSystemsData = getWritingSystems(for: languageCode) {
            setupWritingSystemSelector(with: writingSystemsData.systems, order: writingSystemsData.order, languageCode: languageCode)
            return
        }
        
        // Hide writing system selector for languages without multiple writing systems
        hideWritingSystemSelector()
        
        // Load handshapes from individual language config file
        loadAlphabetFromConfig(languageCode: languageCode, writingSystem: nil)
    }
    
    // MARK: - Writing System Support
    private func getWritingSystems(for languageCode: String) -> (systems: [String: String], order: [String])? {
        // Load languages.json to check for writing systems
        guard let url = Bundle.main.url(forResource: "languages", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let languages = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return nil
        }
        
        // Find the language
        guard let language = languages.first(where: { ($0["code"] as? String) == languageCode }),
              let writingSystems = language["writingSystems"] as? [String: String] else {
            return nil
        }
        
        // Get the order if available, otherwise use the keys in their original order
        let order = language["writingSystemOrder"] as? [String] ?? Array(writingSystems.keys)
        
        return (systems: writingSystems, order: order)
    }
    
    private func setupWritingSystemSelector(with writingSystems: [String: String], order: [String], languageCode: String) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // Create writing system selector if it doesn't exist
            if self.writingSystemSelectorView == nil {
                self.writingSystemSelectorView = WritingSystemSelectorView()
                self.addSubview(self.writingSystemSelectorView!)
                
                // Position it properly within the bottom section - adjust for larger grids
                NSLayoutConstraint.activate([
                    self.writingSystemSelectorView!.centerXAnchor.constraint(equalTo: self.centerXAnchor),
                    self.writingSystemSelectorView!.topAnchor.constraint(equalTo: self.topAnchor, constant: 5),
                    self.writingSystemSelectorView!.widthAnchor.constraint(equalToConstant: 400)
                ])
            }
            
            // Show the selector
            self.writingSystemSelectorView?.isHidden = false
            
            // Configure the selector with order
            let defaultSystem = order.first ?? "hiragana"
            self.currentWritingSystem = defaultSystem
            
            self.writingSystemSelectorView?.configure(
                with: writingSystems,
                order: order,
                selectedSystem: defaultSystem
            ) { [weak self] selectedSystem in
                self?.currentWritingSystem = selectedSystem
                self?.onWritingSystemChanged?(selectedSystem)
                self?.loadAlphabetFromConfig(languageCode: languageCode, writingSystem: selectedSystem)
            }
            
            // Load the default writing system
            self.loadAlphabetFromConfig(languageCode: languageCode, writingSystem: defaultSystem)
        }
    }
    
    private func hideWritingSystemSelector() {
        DispatchQueue.main.async { [weak self] in
            self?.writingSystemSelectorView?.isHidden = true
        }
    }
    
    // MARK: - Alphabet Loading
    private func loadAlphabetFromConfig(languageCode: String, writingSystem: String?) {
        let resourceName: String
        if let writingSystem = writingSystem {
            resourceName = "\(languageCode.lowercased())_\(writingSystem.lowercased())"
        } else {
            resourceName = languageCode.lowercased()
        }
        
        guard let configURL = Bundle.main.url(forResource: resourceName, withExtension: "json"),
              let data = try? Data(contentsOf: configURL),
              let config = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return
        }
        
        // Extract handshapes from the alphabet section
        guard let alphabet = config["alphabet"] as? [String: Any] else {
            return
        }
        
        // Extract symbols from letters first (A-Z)
        var handshapes: [String] = []
        
        if let letters = alphabet["letters"] as? [[String: Any]] {
            let letterSymbols = letters.compactMap { $0["symbol"] as? String }
            handshapes.append(contentsOf: letterSymbols)
        }
        
        // Extract symbols from numbers second (0-9)
        if let numbers = alphabet["numbers"] as? [[String: Any]] {
            let numberSymbols = numbers.compactMap { $0["symbol"] as? String }
            handshapes.append(contentsOf: numberSymbols)
        }
        
        if handshapes.isEmpty {
            return
        }
        
        // Continue with the existing alphabet display logic
        displayAlphabetGrid(handshapes: handshapes)
    }
    
    // MARK: - Alphabet Grid Display
    private func displayAlphabetGrid(handshapes: [String]) {
        // Find the alphabet bar section and update it
        // Find the alphabet bar section and update it - select the last NSView section (filter out WritingSystemSelectorView)
        let mainSections = self.subviews.filter { !($0 is WritingSystemSelectorView) }
        if mainSections.count >= 1, let bottomSection = mainSections.last {
            // Clean up existing subviews
            let allSubviews = bottomSection.subviews
            
            for subview in allSubviews {
                // Keep only the divider (usually at the bottom)
                if subview.frame.origin.y < 10 && subview.frame.height < 10 {
                    continue
                }
                
                subview.removeFromSuperview()
            }
            
            // Force immediate layout and display updates
            bottomSection.needsLayout = true
            bottomSection.needsDisplay = true
            
            // Force the view to redraw immediately
            bottomSection.layer?.setNeedsDisplay()
            
            // Ensure we're on the main thread and add a small delay for cleanup
            DispatchQueue.main.async {
                // Force another layout pass
                bottomSection.layoutSubtreeIfNeeded()
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    // Create new alphabet grid
                    self.createAlphabetGrid(in: bottomSection, handshapes: handshapes)
                }
            }
        }
    }
    
    private func createAlphabetGrid(in section: NSView, handshapes: [String]) {
        let width = section.frame.width
        let height = section.frame.height
        
        // Use section dimensions for layout (not window dimensions)
        let sectionWidth = width
        let sectionHeight = height
        
        // Calculate grid dimensions within this section - adjust for character count
        let gridTopMargin: CGFloat = handshapes.count == 76 ? 15 : (handshapes.count > 50 ? 85 : 70)  // More space for Kanji
        let gridBottomMargin: CGFloat = 50
        let gridLeftMargin: CGFloat = 25
        let gridRightMargin: CGFloat = 25
        
        let availableGridWidth = sectionWidth - gridLeftMargin - gridRightMargin
        let availableGridHeight = sectionHeight - gridTopMargin - gridBottomMargin
        
        // Calculate optimal button size - better distribution for all character counts
        let totalCharacters = handshapes.count
        // Use specific column counts for better distribution
        let columnsPerRow: Int
        if totalCharacters == 36 { // A-Z, 0-9
            columnsPerRow = 12
        } else if totalCharacters == 46 { // Hiragana
            columnsPerRow = 16
        } else if totalCharacters == 76 { // Kanji
            columnsPerRow = 18
        } else {
            columnsPerRow = min(18, totalCharacters)
        }
        let rows = Int(ceil(Double(totalCharacters) / Double(columnsPerRow)))
        let letterSpacing: CGFloat = 12  // Better spacing for alignment
        
        let letterSize = (availableGridWidth - (CGFloat(columnsPerRow - 1) * letterSpacing)) / CGFloat(columnsPerRow)
        let finalLetterSize = min(letterSize, availableGridHeight / CGFloat(rows))
        
        // Position grid within the bottom section - better centering
        let totalGridWidth = CGFloat(columnsPerRow) * finalLetterSize + CGFloat(columnsPerRow - 1) * letterSpacing
        let startX = gridLeftMargin + (availableGridWidth - totalGridWidth) / 2
        
        let totalGridHeight = CGFloat(rows) * finalLetterSize + CGFloat(rows - 1) * letterSpacing
        let startY = gridTopMargin + (availableGridHeight - totalGridHeight) / 2
        
        // Grid layout calculated successfully
        
        // Create letter buttons in grid layout - fill row by row to maintain JSON order
        for (index, letter) in handshapes.enumerated() {
            // Calculate row and column to fill row by row (left to right, top to bottom)
            let row = index / columnsPerRow
            let column = index % columnsPerRow
            
            let x = startX + CGFloat(column) * (finalLetterSize + letterSpacing)
            // Proper Y positioning from top to bottom - flip the row calculation
            let y = startY + CGFloat(rows - 1 - row) * (finalLetterSize + letterSpacing)
            
            let letterButton = createAlphabetButton(
                letter: letter,
                position: CGPoint(x: x, y: y),
                size: CGSize(width: finalLetterSize, height: finalLetterSize),
                letterSize: finalLetterSize
            )
            
            // Ensure the button is properly added and positioned
            section.addSubview(letterButton)
            letterButton.needsDisplay = true
        }
        
        // Force the section to redraw
        section.needsLayout = true
        section.needsDisplay = true
    }
    
    private func createAlphabetButton(letter: String, position: CGPoint, size: CGSize, letterSize: CGFloat) -> NSButton {
        let button = NSButton(title: letter, target: self, action: #selector(letterButtonClicked(_:)))
        button.frame = NSRect(origin: position, size: size)
        button.wantsLayer = true
        button.isBordered = false
        
        // Style the button
        button.layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.1).cgColor
        button.layer?.cornerRadius = 8
        button.layer?.borderWidth = 1.5
        button.layer?.borderColor = NSColor.systemBlue.withAlphaComponent(0.3).cgColor
        
        // Add shadow
        button.layer?.shadowColor = NSColor.black.cgColor
        button.layer?.shadowOffset = CGSize(width: 0, height: 2)
        button.layer?.shadowOpacity = 0.1
        button.layer?.shadowRadius = 4
        
        // Style the title with larger, more readable font size
        let baseFontSize = min(letterSize * 0.6, 24)  // Larger proportion, max 24pt
        let adaptiveFontSize = max(baseFontSize, 12)  // Minimum 12pt for better readability
        button.font = NSFont.systemFont(ofSize: adaptiveFontSize, weight: .semibold)
        button.contentTintColor = NSColor.systemBlue
        
        // Add tracking area for hover effects
        let trackingArea = NSTrackingArea(
            rect: button.bounds,
            options: [.mouseEnteredAndExited, .activeInActiveApp],
            owner: self,
            userInfo: ["button": button]
        )
        button.addTrackingArea(trackingArea)
        
        return button
    }
    
    // MARK: - Actions
    @objc private func letterButtonClicked(_ sender: NSButton) {
        onLetterClicked?(sender.title)
    }
    
    // MARK: - Mouse Events for Hover Effects
    override func mouseEntered(with event: NSEvent) {
        if let trackingArea = event.trackingArea,
           let button = trackingArea.userInfo?["button"] as? NSButton {
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.2
                context.timingFunction = CAMediaTimingFunction(name: .easeOut)
                
                button.animator().layer?.transform = CATransform3DMakeScale(1.1, 1.1, 1.0)
                button.animator().layer?.shadowOpacity = 0.3
                button.animator().layer?.shadowRadius = 8
                button.animator().layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.2).cgColor
            })
        }
    }
    
    override func mouseExited(with event: NSEvent) {
        if let trackingArea = event.trackingArea,
           let button = trackingArea.userInfo?["button"] as? NSButton {
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.2
                context.timingFunction = CAMediaTimingFunction(name: .easeIn)
                
                button.animator().layer?.transform = CATransform3DIdentity
                button.animator().layer?.shadowOpacity = 0.1
                button.animator().layer?.shadowRadius = 4
                button.animator().layer?.backgroundColor = NSColor.systemBlue.withAlphaComponent(0.1).cgColor
            })
        }
    }
} 