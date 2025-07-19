#!/usr/bin/env swift

import AVFoundation
import Foundation

// Simple camera access test for macOS
// This will trigger the permission request and register the app

func testCameraAccess() {
    let session = AVCaptureSession()
    
    // Try to access the camera
    guard let device = AVCaptureDevice.default(for: .video) else {
        print("No camera device found")
        return
    }
    
    do {
        let input = try AVCaptureDeviceInput(device: device)
        session.addInput(input)
        print("Camera access requested successfully")
    } catch {
        print("Failed to access camera: \(error)")
    }
}

// Run the test
testCameraAccess() 