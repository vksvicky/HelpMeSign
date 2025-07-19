import 'package:flutter/material.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io';
import 'package:flutter/services.dart';

class PermissionService extends ChangeNotifier {
  static const String _cameraPermissionKey = 'camera_permission_status';
  static const String _microphonePermissionKey = 'microphone_permission_status';
  static const String _permissionsRequestedKey = 'permissions_requested';
  
  PermissionStatus _cameraStatus = PermissionStatus.denied;
  PermissionStatus _microphoneStatus = PermissionStatus.denied;
  bool _permissionsRequested = false;
  String? _error;

  PermissionStatus get cameraStatus => _cameraStatus;
  PermissionStatus get microphoneStatus => _microphoneStatus;
  bool get permissionsRequested => _permissionsRequested;
  String? get error => _error;

  /// Check if permissions are supported on current platform
  bool get arePermissionsSupported {
    if (kIsWeb) {
      return true; // Web supports permissions via browser APIs
    }
    if (Platform.isAndroid || Platform.isIOS) {
      return true; // Mobile platforms support permissions
    }
    if (Platform.isMacOS) {
      return true; // macOS supports camera permissions (manual setup required)
    }
    if (Platform.isWindows || Platform.isLinux) {
      return true; // Desktop platforms may support permissions
    }
    return false;
  }

  /// Check if camera is required and available
  bool get isCameraRequired {
    return true; // Camera is required for hand gesture recognition
  }

  /// Check if microphone is required and available
  bool get isMicrophoneRequired {
    return false; // Microphone is optional for this app
  }

  /// Check if app can function with current permissions
  bool get canAppFunction {
    if (!isCameraRequired) return true;
    return _cameraStatus == PermissionStatus.granted;
  }

  /// Open system settings for permissions
  Future<bool> openAppSettings() async {
    try {
      if (kIsWeb) {
        // Web doesn't have system settings, show instructions instead
        return false;
      }
      
      if (Platform.isMacOS) {
        // For macOS, open System Settings to Privacy & Security > Camera
        final result = await Process.run('open', [
          'x-apple.systempreferences:com.apple.preference.security?Privacy_Camera'
        ]);
        return result.exitCode == 0;
      }
      
      if (Platform.isIOS || Platform.isAndroid) {
        // Use permission_handler's openAppSettings for mobile
        return await openAppSettings();
      }
      
      if (Platform.isWindows) {
        // For Windows, open Settings > Privacy & Security > Camera
        final result = await Process.run('start', [
          'ms-settings:privacy-webcam'
        ], runInShell: true);
        return result.exitCode == 0;
      }
      
      if (Platform.isLinux) {
        // For Linux, try to open system settings (varies by distribution)
        final result = await Process.run('xdg-open', [
          'settings://privacy/camera'
        ]);
        return result.exitCode == 0;
      }
      
      return false;
    } catch (e) {
      print('Failed to open app settings: $e');
      return false;
    }
  }

  /// Initialize permission service and load stored status
  Future<void> initialize() async {
    try {
      await _loadStoredPermissions();
      await _checkCurrentPermissions();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to initialize permissions: $e';
      notifyListeners();
    }
  }

  /// Request all required permissions
  Future<bool> requestPermissions() async {
    try {
      _error = null;
      
      if (!arePermissionsSupported) {
        _error = 'Permissions not supported on this platform';
        notifyListeners();
        return false;
      }

      // Request camera permission (required)
      if (isCameraRequired) {
        await _requestCameraPermission();
      }

      // Request microphone permission (optional)
      if (isMicrophoneRequired) {
        await _requestMicrophonePermission();
      }

      _permissionsRequested = true;
      await _savePermissionStatus();
      notifyListeners();

      return canAppFunction;
    } catch (e) {
      _error = 'Failed to request permissions: $e';
      notifyListeners();
      return false;
    }
  }

  /// Request camera permission specifically
  Future<void> _requestCameraPermission() async {
    try {
      // On macOS, use native method channel
      if (Platform.isMacOS) {
        await _requestMacOSCameraPermission();
        return;
      }
      
      final status = await Permission.camera.request();
      _cameraStatus = status;
      
      if (status == PermissionStatus.permanentlyDenied) {
        _error = 'Camera permission permanently denied. Please enable it in settings.';
      }
    } catch (e) {
      if (e.toString().contains('MissingPluginException')) {
        // For macOS, this is expected - we need to guide user to manual setup
        if (Platform.isMacOS) {
          _cameraStatus = PermissionStatus.denied;
          _error = 'Camera access needs to be enabled manually in System Settings. Please go to System Settings > Privacy & Security > Camera and add Help Me Sign to the list.';
        } else {
          _cameraStatus = PermissionStatus.denied;
          _error = 'Camera permissions not available on this platform';
        }
      } else {
        rethrow;
      }
    }
  }

  /// Request camera permission using native macOS method channel
  Future<void> _requestMacOSCameraPermission() async {
    try {
      const platform = MethodChannel('help_me_sign/camera_permissions');
      final bool granted = await platform.invokeMethod('requestCameraPermission');
      
      if (granted) {
        _cameraStatus = PermissionStatus.granted;
        print('HelpMeSign: Camera permission granted via native method');
      } else {
        _cameraStatus = PermissionStatus.denied;
        print('HelpMeSign: Camera permission denied via native method');
      }
    } catch (e) {
      print('HelpMeSign: Failed to request camera permission via native method: $e');
      _cameraStatus = PermissionStatus.denied;
    }
  }

  /// Request microphone permission specifically
  Future<void> _requestMicrophonePermission() async {
    try {
      final status = await Permission.microphone.request();
      _microphoneStatus = status;
    } catch (e) {
      if (e.toString().contains('MissingPluginException')) {
        _microphoneStatus = PermissionStatus.denied;
        // Don't set error for microphone as it's optional
      } else {
        rethrow;
      }
    }
  }

  /// Check current permission status without requesting
  Future<void> _checkCurrentPermissions() async {
    try {
      if (arePermissionsSupported) {
        _cameraStatus = await Permission.camera.status;
        _microphoneStatus = await Permission.microphone.status;
      }
    } catch (e) {
      // Handle MissingPluginException gracefully
      if (e.toString().contains('MissingPluginException')) {
        if (Platform.isMacOS) {
          // On macOS, MissingPluginException is expected - permissions need manual setup
          _cameraStatus = PermissionStatus.denied;
          _microphoneStatus = PermissionStatus.denied;
          // Don't set error here - let the user request permissions first
        } else {
        _cameraStatus = PermissionStatus.denied;
        _microphoneStatus = PermissionStatus.denied;
        }
      }
    }
  }

  /// Load stored permission status from SharedPreferences
  Future<void> _loadStoredPermissions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _permissionsRequested = prefs.getBool(_permissionsRequestedKey) ?? false;
      
      // Load stored status if available
      final cameraStatusIndex = prefs.getInt(_cameraPermissionKey);
      if (cameraStatusIndex != null) {
        _cameraStatus = PermissionStatus.values[cameraStatusIndex];
      }
      
      final microphoneStatusIndex = prefs.getInt(_microphonePermissionKey);
      if (microphoneStatusIndex != null) {
        _microphoneStatus = PermissionStatus.values[microphoneStatusIndex];
      }
    } catch (e) {
      // If SharedPreferences fails, use default values
      _permissionsRequested = false;
      _cameraStatus = PermissionStatus.denied;
      _microphoneStatus = PermissionStatus.denied;
    }
  }

  /// Save permission status to SharedPreferences
  Future<void> _savePermissionStatus() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_permissionsRequestedKey, _permissionsRequested);
      await prefs.setInt(_cameraPermissionKey, _cameraStatus.index);
      await prefs.setInt(_microphonePermissionKey, _microphoneStatus.index);
    } catch (e) {
      // Log error but don't fail the app
      print('Failed to save permission status: $e');
    }
  }

  /// Get platform-specific permission instructions
  String getPermissionInstructions() {
    if (kIsWeb) {
      return 'Please allow camera access when prompted by your browser. Click the camera icon in the address bar if needed.';
    }
    
    if (Platform.isIOS) {
      return 'Go to Settings > Privacy & Security > Camera > Help Me Sign and enable camera access.';
    }
    
    if (Platform.isAndroid) {
      return 'Go to Settings > Apps > Help Me Sign > Permissions and enable Camera permission.';
    }
    
    if (Platform.isMacOS) {
      return 'Go to System Settings > Privacy & Security > Camera and add Help Me Sign to the list. If the app is not in the list, you may need to first try to use the camera in the app, then return to System Settings.';
    }
    
    if (Platform.isWindows) {
      return 'Go to Settings > Privacy & Camera and ensure camera access is enabled for Help Me Sign.';
    }
    
    if (Platform.isLinux) {
      return 'Camera permissions are typically handled by your desktop environment. Check your system settings.';
    }
    
    return 'Please check your system settings to enable camera permissions.';
  }

  /// Get permission status description
  String getPermissionStatusDescription() {
    if (!arePermissionsSupported) {
      return 'Permissions not supported on this platform';
    }
    
    if (_cameraStatus == PermissionStatus.granted) {
      return 'Camera access granted';
    }
    
    if (_cameraStatus == PermissionStatus.denied) {
      return 'Camera access denied';
    }
    
    if (_cameraStatus == PermissionStatus.permanentlyDenied) {
      return 'Camera access permanently denied';
    }
    
    if (_cameraStatus == PermissionStatus.restricted) {
      return 'Camera access restricted';
    }
    
    return 'Camera access not determined';
  }

  /// Clear stored permissions (for testing or reset)
  Future<void> clearStoredPermissions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_cameraPermissionKey);
      await prefs.remove(_microphonePermissionKey);
      await prefs.remove(_permissionsRequestedKey);
      
      _cameraStatus = PermissionStatus.denied;
      _microphoneStatus = PermissionStatus.denied;
      _permissionsRequested = false;
      _error = null;
      
      notifyListeners();
    } catch (e) {
      _error = 'Failed to clear stored permissions: $e';
      notifyListeners();
    }
  }

  /// Reset error state
  void clearError() {
    _error = null;
    notifyListeners();
  }
} 