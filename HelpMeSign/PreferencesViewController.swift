import Cocoa

class PreferencesViewController: NSViewController {
    @IBOutlet weak var cameraStatusLabel: NSTextField!
    @IBOutlet weak var micStatusLabel: NSTextField!

    override func viewWillAppear() {
        super.viewWillAppear()
        updateStatusLabels()
        NotificationCenter.default.addObserver(self, selector: #selector(updateStatusLabels), name: AppDelegateNotificationNames.permissionStatusChanged, object: nil)
    }
    override func viewWillDisappear() {
        super.viewWillDisappear()
        NotificationCenter.default.removeObserver(self, name: AppDelegateNotificationNames.permissionStatusChanged, object: nil)
    }

    @objc func updateStatusLabels() {
        let cameraStatus = Self.permissionStatus(for: .video)
        let micStatus = Self.permissionStatus(for: .audio)
        cameraStatusLabel.stringValue = "Camera: " + cameraStatus.text
        micStatusLabel.stringValue = "Microphone: " + micStatus.text
        cameraStatusLabel.textColor = cameraStatus.color
        micStatusLabel.textColor = micStatus.color
        cameraStatusLabel.font = NSFont.boldSystemFont(ofSize: 14)
        micStatusLabel.font = NSFont.boldSystemFont(ofSize: 14)
    }

    enum PermissionType { case video, audio }
    struct PermissionStatus {
        let text: String
        let color: NSColor
    }
    static func permissionStatus(for type: PermissionType) -> PermissionStatus {
        let key: String
        switch type {
        case .video: key = "CameraAccessGranted"
        case .audio: key = "MicAccessGranted"
        }
        if UserDefaults.standard.object(forKey: key) == nil {
            return PermissionStatus(text: "Not Requested", color: .systemGray)
        }
        let granted = UserDefaults.standard.bool(forKey: key)
        return granted ?
            PermissionStatus(text: "Allowed ✅", color: .systemGreen) :
            PermissionStatus(text: "Denied ❌", color: .systemRed)
    }

    @IBAction func closePreferences(_ sender: Any?) {
        self.view.window?.sheetParent?.endSheet(self.view.window!)
    }

    @IBAction func openCameraSettings(_ sender: Any?) {
        NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Camera")!)
    }

    @IBAction func openMicrophoneSettings(_ sender: Any?) {
        NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone")!)
    }
    
} 
