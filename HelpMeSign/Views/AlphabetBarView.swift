//
//  AlphabetBarView.swift
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
        
        // Try to load as data asset first (dataset approach)
        if let dataAsset = NSDataAsset(name: "sign_language_and_numbers") {
            // Try to get data - for data assets, we typically use the main data property
            if let svgString = String(data: dataAsset.data, encoding: .utf8) {
                self.svgString = svgString
                allItems = extractCharacterList(from: svgString)
            } else {
                allItems = []
            }
        } else {
            // Try to load as image asset (imageset approach)
            if NSImage(named: svgFileName) != nil {
                // For now, we'll need to extract the SVG data from the image
                // This is a fallback approach
                allItems = []
            } else {
                allItems = []
            }
        }
        
        setupLetters()
    }
    
    // Extract character list from SVG file by parsing symbol IDs
    func extractCharacterList(from svgString: String) -> [String] {
        var characters: [String] = []
        
        // Simple regex to extract symbol IDs from SVG
        let pattern = #"<symbol id="([^"]+)"# 
        let regex = try? NSRegularExpression(pattern: pattern, options: [])
        
        if let matches = regex?.matches(in: svgString, options: [], range: NSRange(location: 0, length: svgString.count)) {
            for match in matches {
                if let range = Range(match.range(at: 1), in: svgString) {
                    let character = String(svgString[range])
                    // Only add non-empty characters and avoid duplicates
                    if !character.isEmpty && !characters.contains(character) {
                        characters.append(character)
                    }
                }
            }
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
        
        return sortedCharacters
    }
    
    required init?(coder: NSCoder) { fatalError() }

    func setupLetters() {
        // Clear existing views completely
        for view in letterViews {
            view.removeFromSuperview()
        }
        letterViews.removeAll()
        
        // Handle empty character list
        guard !allItems.isEmpty else {
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
            // Modern tile style
            lv.layer?.cornerRadius = tileSize * 0.18
            lv.layer?.shadowOpacity = 0.10
            lv.layer?.shadowRadius = 4
            lv.layer?.shadowOffset = CGSize(width: 0, height: 2)
        }
        
        // Force correct z-order by setting layer zPosition
        for (index, letterView) in letterViews.enumerated() {
            letterView.layer?.zPosition = CGFloat(index)
        }
        
        // Force layout and display updates
        self.needsLayout = true
        self.needsDisplay = true
        self.layout()
        self.display()
    }
} 