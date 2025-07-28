//
//  AlphabetLetterView.swift
//  HelpMeSign
//
//  Created by Vivek Krishnan on 22/07/2025.
//

import Cocoa

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
