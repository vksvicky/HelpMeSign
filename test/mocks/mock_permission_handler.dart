import 'package:permission_handler/permission_handler.dart';

class MockPermissionHandler {
  static PermissionStatus _cameraPermission = PermissionStatus.denied;
  static bool _shouldGrantPermission = true;

  static void setCameraPermission(PermissionStatus status) {
    _cameraPermission = status;
  }

  static void setShouldGrantPermission(bool shouldGrant) {
    _shouldGrantPermission = shouldGrant;
  }

  static Future<PermissionStatus> requestCameraPermission() async {
    await Future.delayed(const Duration(milliseconds: 50));
    
    if (_shouldGrantPermission) {
      _cameraPermission = PermissionStatus.granted;
    } else {
      _cameraPermission = PermissionStatus.denied;
    }
    
    return _cameraPermission;
  }

  static Future<PermissionStatus> getCameraPermissionStatus() async {
    await Future.delayed(const Duration(milliseconds: 10));
    return _cameraPermission;
  }

  static void reset() {
    _cameraPermission = PermissionStatus.denied;
    _shouldGrantPermission = true;
  }
} 