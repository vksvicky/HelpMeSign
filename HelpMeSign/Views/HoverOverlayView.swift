//
//  HoverOverlayView.swift
//  HelpMeSign
//
//  Created by Vivek Krishnan on 22/07/2025.
//

import Cocoa

class HoverOverlayView: NSView {
    var onHoverChanged: ((Bool) -> Void)?
    
    override func updateTrackingAreas() {
        super.updateTrackingAreas()
        self.trackingAreas.forEach { self.removeTrackingArea($0) }
        let options: NSTrackingArea.Options = [.mouseEnteredAndExited, .activeInActiveApp, .inVisibleRect]
        let area = NSTrackingArea(rect: self.bounds, options: options, owner: self, userInfo: nil)
        self.addTrackingArea(area)
    }
    
    override func mouseEntered(with event: NSEvent) {
        onHoverChanged?(true)
    }
    
    override func mouseExited(with event: NSEvent) {
        onHoverChanged?(false)
    }
} 