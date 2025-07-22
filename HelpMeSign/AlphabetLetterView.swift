//
//  AlphabetLetterView.swift
//  HelpMeSign
//
//  Created by Vivek Krishnan on 22/07/2025.
//

import Cocoa
import Macaw

class AlphabetBarView: NSView {
    // Language-agnostic design - reads character list from SVG file
    var currentLanguage = "ASL" // Default language
    var allItems: [String] = [] // Will be populated from SVG file
    var svgFileName: String = "asl_alphabet_numbers" // Will change based on language
    var svgNode: Node?
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
                do {
                    let svg = try SVGParser.parse(text: svgString)
                    self.svgNode = svg
                    
                    allItems = extractCharacterList(from: svgString)
                    print("Loaded \(allItems.count) characters for \(language): \(allItems)")
                    
                } catch {
                    print("Failed to parse SVG for \(language): \(error)")
                    allItems = []
                }
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
        for columns in 1...count {
            let rows = Int(ceil(Double(count) / Double(columns)))
            let tileWidth = (availableWidth - CGFloat(columns - 1) * spacing) / CGFloat(columns)
            let tileHeight = (availableHeight - CGFloat(rows - 1) * spacing) / CGFloat(rows)
            let tileSize = min(tileWidth, tileHeight)
            if tileSize > bestTileSize {
                bestTileSize = tileSize
                bestColumns = columns
                bestRows = rows
            }
        }
        let tileSize = bestTileSize
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
            let lv = AlphabetLetterView(frame: itemFrame, letter: item, svgNode: svgNode)
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
    let svgNode: Node?
    var macawView: MacawView?
    var macawNode: Node? // Store the node for animation
    let label: NSTextField
    var isHovered = false {
        didSet { animateZoom() }
    }
    
    static var instanceCount = 0
    let instanceId: Int
    
    // Add debugIndex for debugging view order
    var debugIndex: Int?
    
    init(frame: NSRect, letter: String, svgNode: Node?) {
        AlphabetLetterView.instanceCount += 1
        self.instanceId = AlphabetLetterView.instanceCount
        self.letter = letter
        self.svgNode = svgNode
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
        if let svgNode = svgNode, let symbol = svgNode.nodeBy(tag: letter) {
            let macaw = MacawView(node: symbol, frame: self.bounds)
            macaw.backgroundColor = .clear
            self.addSubview(macaw)
            self.macawView = macaw
            self.macawNode = symbol
        } else {
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
        
        // Mouse tracking for hover
        let options: NSTrackingArea.Options = [.mouseEnteredAndExited, .activeInActiveApp, .inVisibleRect]
        let area = NSTrackingArea(rect: self.bounds, options: options, owner: self, userInfo: nil)
        self.addTrackingArea(area)
    }
    
    required init?(coder: NSCoder) { fatalError() }
    
    override func mouseEntered(with event: NSEvent) {
        isHovered = true
    }
    
    override func mouseExited(with event: NSEvent) {
        isHovered = false
    }
    
    func animateZoom() {
        if let node = macawNode {
            // Animate the SVG node directly - more subtle scale for professional look
            let scale = isHovered ? 1.3 : 1.0
            node.placeVar.animation(to: Transform.scale(sx: scale, sy: scale), during: 0.2).play()
        } else {
            // Animate the placeholder view - more subtle scale for professional lookCleanShot 2025-07-22 at 12.09.13@2x.png
            NSAnimationContext.runAnimationGroup { ctx in
                ctx.duration = 0.2
                ctx.timingFunction = CAMediaTimingFunction(name: .easeOut)
                self.animator().layer?.setAffineTransform(isHovered ? .init(scaleX: 1.15, y: 1.15) : .identity)
            }
        }
        
        // Add subtle background color change on hover
        NSAnimationContext.runAnimationGroup { ctx in
            ctx.duration = 0.2
            ctx.timingFunction = CAMediaTimingFunction(name: .easeOut)
            self.animator().layer?.backgroundColor = isHovered ? NSColor.controlAccentColor.withAlphaComponent(0.1).cgColor : NSColor.controlBackgroundColor.cgColor
        }
    }
}
