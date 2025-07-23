//
//  AlphabetLetterView.swift
//  HelpMeSign
//
//  Created by Vivek Krishnan on 22/07/2025.
//

import Cocoa

class AlphabetBarView: NSView {
    // Language-agnostic design - reads character list from SVG file
    var currentLanguage = "ASL" // Default language
    var allItems: [String] = [] // Will be populated from SVG file
    var svgFileName: String = "asl_alphabet_numbers" // Will change based on language
    var svgString: String?
    var letterViews: [AlphabetLetterView] = []

    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        self.wantsLayer = true
        self.layer?.backgroundColor = NSColor.clear.cgColor
        setupLanguage("ASL") // Initialize with default language
    }
    
    // Function to switch languages
    func setupLanguage(_ language: String) {
        currentLanguage = language
        svgFileName = "\(language.lowercased())_alphabet_numbers"
        
        // Clear existing views
        letterViews.forEach { $0.removeFromSuperview() }
        letterViews.removeAll()
        
        // Load SVG file from asset catalog (using imageset)
        print("Attempting to load SVG asset: \(svgFileName)")
        
        // Try to load as data asset first (dataset approach)
        if let dataAsset = NSDataAsset(name: "sign_language_and_numbers") {
            print("Found data asset")
            
            // Try to get data - for data assets, we typically use the main data property
            if let svgString = String(data: dataAsset.data, encoding: .utf8) {
                print("Found data asset, size: \(dataAsset.data.count) bytes")
                print("Successfully decoded SVG string, size: \(svgString.count) characters")
                
                self.svgString = svgString
                print("Successfully stored SVG string")
                
                allItems = extractCharacterList(from: svgString)
                print("Loaded \(allItems.count) characters for \(language): \(allItems)")
                
            } else {
                print("Failed to get data for key 'asl' or decode SVG string")
                allItems = []
            }
        } else {
            print("Data asset not found, trying imageset approach")
            
            // Try to load as image asset (imageset approach)
            if let image = NSImage(named: svgFileName) {
                print("Found image asset")
                // For now, we'll need to extract the SVG data from the image
                // This is a fallback approach
                allItems = []
            } else {
                print("Failed to load SVG asset for \(language): \(svgFileName)")
                allItems = []
            }
        }
        
        setupLetters()
    }
    
    // Extract character list from SVG file by parsing symbol IDs
    func extractCharacterList(from svgString: String) -> [String] {
        var characters: [String] = []
        
        print("SVG content length: \(svgString.count)")
        print("SVG content preview: \(String(svgString.prefix(200)))")
        
        // Simple regex to extract symbol IDs from SVG
        let pattern = #"<symbol id="([^"]+)"# 
        let regex = try? NSRegularExpression(pattern: pattern, options: [])
        
        if let matches = regex?.matches(in: svgString, options: [], range: NSRange(location: 0, length: svgString.count)) {
            print("Found \(matches.count) symbol matches")
            for match in matches {
                if let range = Range(match.range(at: 1), in: svgString) {
                    let character = String(svgString[range])
                    // Only add non-empty characters and avoid duplicates
                    if !character.isEmpty && !characters.contains(character) {
                        characters.append(character)
                        print("Extracted character: \(character)")
                    }
                }
            }
        } else {
            print("No symbol matches found in SVG")
        }
        
        // Sort characters in a language-agnostic way
        let sortedCharacters = characters.sorted { char1, char2 in
            // Check if both are letters or both are numbers
            let isLetter1 = char1.rangeOfCharacter(from: .letters) != nil
            let isLetter2 = char2.rangeOfCharacter(from: .letters) != nil
            let isNumber1 = char1.rangeOfCharacter(from: .decimalDigits) != nil
            let isNumber2 = char2.rangeOfCharacter(from: .decimalDigits) != nil
            
            // If both are letters, sort alphabetically
            if isLetter1 && isLetter2 {
                return char1.localizedCompare(char2) == .orderedAscending
            }
            // If both are numbers, sort numerically
            else if isNumber1 && isNumber2 {
                return char1 < char2
            }
            // Letters come before numbers
            else if isLetter1 && isNumber2 {
                return true
            }
            else if isNumber1 && isLetter2 {
                return false
            }
            // For any other characters, sort alphabetically
            else {
                return char1.localizedCompare(char2) == .orderedAscending
            }
        }
        
        print("Language-agnostic sorted characters: \(sortedCharacters)")
        return sortedCharacters
    }
    required init?(coder: NSCoder) { fatalError() }

    func setupLetters() {
        // Clear existing views completely
        for view in letterViews {
            view.removeFromSuperview()
        }
        letterViews.removeAll()
        
        print("Setting up letters with \(allItems.count) items: \(allItems)")
        
        // Handle empty character list
        guard !allItems.isEmpty else {
            print("No items to display, skipping setup")
            return
        }
        
        // Dynamic grid layout: maximize tile size by choosing optimal columns/rows
        let count = allItems.count
        let spacing: CGFloat = 8
        let margin: CGFloat = 16
        let availableWidth = self.bounds.width - 2 * margin
        let availableHeight = self.bounds.height - 2 * margin
        var bestTileSize: CGFloat = 0
        var bestColumns = 1
        var bestRows = count
        
        // Try all possible column counts to find the configuration with the largest tile size
        // Prioritize single-row layouts when items can fit
        var canFitInOneRow = false
        if count > 0 {
            let singleRowTileWidth = (availableWidth - CGFloat(count - 1) * spacing) / CGFloat(count)
            let singleRowTileHeight = availableHeight
            let singleRowTileSize = min(singleRowTileWidth, singleRowTileHeight)
            canFitInOneRow = singleRowTileSize >= 20 // Minimum viable tile size
        }
        
        for columns in 1...count {
            let rows = Int(ceil(Double(count) / Double(columns)))
            let tileWidth = (availableWidth - CGFloat(columns - 1) * spacing) / CGFloat(columns)
            let tileHeight = (availableHeight - CGFloat(rows - 1) * spacing) / CGFloat(rows)
            let tileSize = min(tileWidth, tileHeight)
            
            // Apply constraints: minimum 20px, maximum 80px
            let constrainedTileSize = max(20, min(80, tileSize))
            
            // Prioritize single-row layout if it can fit all items
            if canFitInOneRow && rows == 1 && constrainedTileSize >= bestTileSize {
                bestTileSize = constrainedTileSize
                bestColumns = columns
                bestRows = rows
                break // Found optimal single-row layout
            } else if !canFitInOneRow && constrainedTileSize > bestTileSize {
                bestTileSize = constrainedTileSize
                bestColumns = columns
                bestRows = rows
            }
        }
        let tileSize = max(20, bestTileSize) // Ensure minimum tile size
        let columns = bestColumns
        let rows = bestRows
        
        // Center the grid
        let totalGridWidth = CGFloat(columns) * tileSize + CGFloat(columns - 1) * spacing
        let totalGridHeight = CGFloat(rows) * tileSize + CGFloat(rows - 1) * spacing
        let startX = margin + (self.bounds.width - 2 * margin - totalGridWidth) / 2
        let startY = margin + (self.bounds.height - 2 * margin - totalGridHeight) / 2
        
        print("=== DYNAMIC GRID LAYOUT DEBUG ===")
        print("Columns: \(columns), Rows: \(rows), Tile size: \(tileSize)")
        print("Start position: (\(startX), \(startY))")
        print("=== CHARACTER ORDER DEBUG ===")
        
        for i in 0..<count {
            let row = i / columns
            let col = i % columns
            // Flip the Y-axis so the first row is at the top
            let x = startX + CGFloat(col) * (tileSize + spacing)
            let y = startY + CGFloat(rows - 1 - row) * (tileSize + spacing)
            let itemFrame = NSRect(x: x, y: y, width: tileSize, height: tileSize)
            let item = allItems[i]
            let lv = AlphabetLetterView(frame: itemFrame, letter: item, svgString: svgString)
            lv.label.stringValue = item
            lv.label.needsDisplay = true
            self.addSubview(lv)
            letterViews.append(lv)
            lv.debugIndex = i
            print("Position \(i): Row \(row), Col \(col) = '\(item)' at frame: \(itemFrame), debugIndex: \(lv.debugIndex ?? -1)")
            // Modern tile style
            lv.layer?.cornerRadius = tileSize * 0.18
            lv.layer?.shadowOpacity = 0.10
            lv.layer?.shadowRadius = 4
            lv.layer?.shadowOffset = CGSize(width: 0, height: 2)
        }
        
        print("=== SUBVIEWS ORDER DEBUG ===")
        for (index, subview) in self.subviews.enumerated() {
            if let letterView = subview as? AlphabetLetterView {
                print("Subview \(index): debugIndex=\(letterView.debugIndex ?? -1), letter='\(letterView.letter)', frame=\(letterView.frame)")
            }
        }
        print("=== END SUBVIEWS DEBUG ===")
        
        // Force correct z-order by setting layer zPosition
        for (index, letterView) in letterViews.enumerated() {
            letterView.layer?.zPosition = CGFloat(index)
        }
        
        print("=== END DEBUG ===")
        
        // Force layout and display updates
        self.needsLayout = true
        self.needsDisplay = true
        self.layout()
        self.display()
        
        print("UI refresh completed - \(letterViews.count) views created and displayed")
    }
}

class AlphabetLetterView: NSView {
    let letter: String
    let svgString: String?
    var svgImageView: NSImageView?
    let label: NSTextField
    var isHovered = false {
        didSet { animateZoom() }
    }
    
    static var instanceCount = 0
    let instanceId: Int
    
    // Add debugIndex for debugging view order
    var debugIndex: Int?
    
    init(frame: NSRect, letter: String, svgString: String?) {
        AlphabetLetterView.instanceCount += 1
        self.instanceId = AlphabetLetterView.instanceCount
        self.letter = letter
        self.svgString = svgString
        self.label = NSTextField(labelWithString: letter)
        super.init(frame: frame)
        
        print("Creating letter view #\(instanceId) for: '\(letter)'")
        self.wantsLayer = true
        
        // Professional design with subtle styling
        self.layer?.cornerRadius = 6
        self.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        self.layer?.borderWidth = 0.5
        self.layer?.borderColor = NSColor.separatorColor.cgColor
        
        // Subtle shadow for depth
        self.layer?.shadowColor = NSColor.black.cgColor
        self.layer?.shadowOpacity = 0.06
        self.layer?.shadowRadius = 1.5
        self.layer?.shadowOffset = CGSize(width: 0, height: 1)
        
        // Try to extract the symbol for this letter from the SVG
        if let svgString = svgString {
            // Look for a symbol with the letter as ID
            if let symbolSVG = extractSymbol(from: svgString, withId: letter) {
                // Create a simple SVG view using WebKit or convert to image
                if let image = createImageFromSVG(symbolSVG, size: frame.size) {
                    let imageView = NSImageView(frame: self.bounds)
                    imageView.image = image
                    imageView.autoresizingMask = [.width, .height]
                    self.addSubview(imageView)
                    self.svgImageView = imageView
                    
                    print("Added SVG symbol for '\(letter)'")
                } else {
                    setupLabel()
                }
            } else {
                setupLabel()
            }
        } else {
            setupLabel()
        }
        
        // Mouse tracking for hover
        let options: NSTrackingArea.Options = [.mouseEnteredAndExited, .activeInActiveApp, .inVisibleRect]
        let area = NSTrackingArea(rect: self.bounds, options: options, owner: self, userInfo: nil)
        self.addTrackingArea(area)
    }
    
    private func extractSymbol(from svgString: String, withId id: String) -> String? {
        // Simple regex to extract symbol content
        let pattern = #"<symbol id="\#(id)"[^>]*>(.*?)</symbol>"#
        let regex = try? NSRegularExpression(pattern: pattern, options: [.dotMatchesLineSeparators])
        
        if let match = regex?.firstMatch(in: svgString, options: [], range: NSRange(location: 0, length: svgString.count)) {
            if let range = Range(match.range(at: 1), in: svgString) {
                let symbolContent = String(svgString[range])
                // Create a complete SVG with the symbol content
                return """
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
                \(symbolContent)
                </svg>
                """
            }
        }
        return nil
    }
    
    private func createImageFromSVG(_ svgString: String, size: NSSize) -> NSImage? {
        // Guard against zero or negative sizes
        guard size.width > 0 && size.height > 0 else {
            print("Cannot create image with zero or negative size: \(size)")
            return nil
        }
        
        // For now, create a simple placeholder image
        // In a real implementation, you would use WebKit or a proper SVG renderer
        let image = NSImage(size: size)
        image.lockFocus()
        
        // Draw a simple placeholder
        NSColor.systemBlue.setFill()
        NSBezierPath(ovalIn: NSRect(x: size.width * 0.2, y: size.height * 0.2, 
                                   width: size.width * 0.6, height: size.height * 0.6)).fill()
        
        // Draw the letter
        let attributes: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: size.width * 0.3, weight: .bold),
            .foregroundColor: NSColor.white
        ]
        let letterString = NSAttributedString(string: letter, attributes: attributes)
        let letterSize = letterString.size()
        let letterRect = NSRect(x: (size.width - letterSize.width) / 2,
                               y: (size.height - letterSize.height) / 2,
                               width: letterSize.width,
                               height: letterSize.height)
        letterString.draw(in: letterRect)
        
        image.unlockFocus()
        return image
    }
    
    private func setupLabel() {
        // Professional placeholder with better typography
        self.layer?.backgroundColor = NSColor.controlBackgroundColor.cgColor
        
        // Use system font with appropriate weight
        let fontSize = frame.width < 50 ? 16 : 20
        label.font = NSFont.systemFont(ofSize: CGFloat(fontSize), weight: .medium)
        label.alignment = .center
        label.textColor = NSColor.labelColor
        label.frame = NSRect(x: 0, y: (frame.height-CGFloat(fontSize+4))/2, width: frame.width, height: CGFloat(fontSize+4))
        self.addSubview(label)
        
        print("Added label for '\(letter)' with text: '\(label.stringValue)'")
    }
    
    required init?(coder: NSCoder) { fatalError() }
    
    override func mouseEntered(with event: NSEvent) {
        isHovered = true
    }
    
    override func mouseExited(with event: NSEvent) {
        isHovered = false
    }
    
    func animateZoom() {
        // Animate the SVG view or placeholder view
        NSAnimationContext.runAnimationGroup { ctx in
            ctx.duration = 0.2
            ctx.timingFunction = CAMediaTimingFunction(name: .easeOut)
            self.animator().layer?.setAffineTransform(isHovered ? .init(scaleX: 1.15, y: 1.15) : .identity)
        }
        
        // Add subtle background color change on hover
        NSAnimationContext.runAnimationGroup { ctx in
            ctx.duration = 0.2
            ctx.timingFunction = CAMediaTimingFunction(name: .easeOut)
            self.animator().layer?.backgroundColor = isHovered ? NSColor.controlAccentColor.withAlphaComponent(0.1).cgColor : NSColor.controlBackgroundColor.cgColor
        }
    }
}
