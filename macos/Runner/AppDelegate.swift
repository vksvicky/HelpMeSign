import Cocoa
import FlutterMacOS
import AVFoundation

@main
class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }
  
  override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
    return true
  }
  
  override func applicationDidFinishLaunching(_ notification: Notification) {
    // Set up method channel for camera permissions
    let controller = mainFlutterWindow?.contentViewController as! FlutterViewController
    let channel = FlutterMethodChannel(name: "help_me_sign/camera_permissions", binaryMessenger: controller.engine.binaryMessenger)
    
    channel.setMethodCallHandler { [weak self] (call, result) in
      if call.method == "requestCameraPermission" {
        self?.triggerCameraPermissionDialog { granted in
          result(granted)
        }
      } else {
        result(FlutterMethodNotImplemented)
      }
    }
    
    super.applicationDidFinishLaunching(notification)
  }
  
  private func triggerCameraPermissionDialog(completion: @escaping (Bool) -> Void = { _ in }) {
    print("HelpMeSign: Triggering camera permission dialog...")
    
    // Check current permission status first
    let status = AVCaptureDevice.authorizationStatus(for: .video)
    print("HelpMeSign: Current camera permission status: \(status.rawValue)")
    
    switch status {
    case .notDetermined:
      // Request permission - this will show the dialog
      AVCaptureDevice.requestAccess(for: .video) { granted in
        DispatchQueue.main.async {
          if granted {
            print("HelpMeSign: Camera permission granted!")
          } else {
            print("HelpMeSign: Camera permission denied")
          }
          completion(granted)
        }
      }
    case .authorized:
      print("HelpMeSign: Camera permission already authorized")
      completion(true)
    case .denied, .restricted:
      print("HelpMeSign: Camera permission denied or restricted")
      completion(false)
    @unknown default:
      print("HelpMeSign: Unknown camera permission status")
      completion(false)
    }
  }
}
