import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:image/image.dart' as img;
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

class CameraProvider extends ChangeNotifier {
  CameraController? _controller;
  List<CameraDescription> _cameras = [];
  bool _isInitialized = false;
  bool _isStreaming = false;
  String? _error;

  CameraController? get controller => _controller;
  List<CameraDescription> get cameras => _cameras;
  bool get isInitialized => _isInitialized;
  bool get isStreaming => _isStreaming;
  String? get error => _error;

  /// Check if camera is supported on current platform
  bool get isCameraSupported {
    if (kIsWeb) {
      return true; // Web supports camera via WebRTC
    }
    if (Platform.isAndroid || Platform.isIOS) {
      return true; // Mobile platforms support camera
    }
    if (Platform.isMacOS) {
      return true; // macOS supports camera via web or manual setup
    }
    if (Platform.isWindows || Platform.isLinux) {
      return true; // Desktop platforms may support camera
    }
    return false;
  }

  Future<void> initialize() async {
    try {
      // Check if camera is supported on this platform
      if (!isCameraSupported) {
        _error = 'Camera is not supported on this platform';
        notifyListeners();
        return;
      }

      // Request camera permission with proper error handling
      PermissionStatus status;
      try {
        status = await Permission.camera.request();
      } catch (e) {
        // Handle MissingPluginException for permission_handler
        if (e.toString().contains('MissingPluginException')) {
          if (Platform.isMacOS) {
            // On macOS, continue without permission_handler - the camera plugin will handle permissions
            status = PermissionStatus.denied; // We'll try anyway
          } else {
          _error = 'Camera permissions not available on this platform';
          notifyListeners();
          return;
        }
        } else {
        rethrow;
        }
      }

      // On macOS, try to access camera even if permission_handler failed
      if (status != PermissionStatus.granted && !Platform.isMacOS) {
        _error = 'Camera permission denied';
        notifyListeners();
        return;
      }

      // Get available cameras with proper error handling
      try {
        _cameras = await availableCameras();
      } catch (e) {
        if (e.toString().contains('MissingPluginException')) {
          if (Platform.isMacOS) {
            _error = 'Camera access needs to be enabled in System Settings. Please go to System Settings > Privacy & Security > Camera and add Help Me Sign to the list.';
          } else {
          _error = 'Camera plugin not available on this platform';
          }
          notifyListeners();
          return;
        }
        rethrow;
      }

      if (_cameras.isEmpty) {
        if (Platform.isMacOS) {
          _error = 'No cameras found. Please ensure camera access is enabled in System Settings > Privacy & Security > Camera.';
        } else {
        _error = 'No cameras available';
        }
        notifyListeners();
        return;
      }

      // Initialize camera controller with proper error handling
      try {
        _controller = CameraController(
          _cameras.first,
          ResolutionPreset.high,
          enableAudio: false,
          imageFormatGroup: ImageFormatGroup.bgra8888,
        );

        await _controller!.initialize();
        _isInitialized = true;
        _error = null;
        notifyListeners();
      } catch (e) {
        if (e.toString().contains('MissingPluginException')) {
          if (Platform.isMacOS) {
            _error = 'Camera access needs to be enabled in System Settings. Please go to System Settings > Privacy & Security > Camera and add Help Me Sign to the list.';
          } else {
          _error = 'Camera initialization not supported on this platform';
          }
        } else {
          _error = 'Failed to initialize camera: $e';
        }
        notifyListeners();
      }
    } catch (e) {
      _error = 'Failed to initialize camera: $e';
      notifyListeners();
    }
  }

  Future<void> startStreaming() async {
    if (!_isInitialized || _controller == null) {
      _error = 'Camera not initialized';
      notifyListeners();
      return;
    }

    try {
      await _controller!.startImageStream((image) {
        // Process the image for hand gesture recognition
        _processImage(image);
      });
      _isStreaming = true;
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = 'Failed to start streaming: $e';
      notifyListeners();
    }
  }

  Future<void> stopStreaming() async {
    if (_controller != null && _isStreaming) {
      try {
        await _controller!.stopImageStream();
        _isStreaming = false;
        _error = null;
        notifyListeners();
      } catch (e) {
        _error = 'Failed to stop streaming: $e';
        notifyListeners();
      }
    }
  }

  void _processImage(CameraImage image) {
    // Convert CameraImage to img.Image for processing
    final img.Image? processedImage = _convertCameraImageToImage(image);
    if (processedImage != null) {
      // Send to gesture recognition service
      // This will be connected to the gesture provider
    }
  }

  img.Image? _convertCameraImageToImage(CameraImage cameraImage) {
    try {
      if (cameraImage.format.group == ImageFormatGroup.bgra8888) {
        // Create a simple RGB image from the camera data
        final image = img.Image.fromBytes(
          width: cameraImage.width,
          height: cameraImage.height,
          bytes: cameraImage.planes[0].bytes.buffer,
        );
        return image;
      }
      return null;
    } catch (e) {
      print('Error converting camera image: $e');
      return null;
    }
  }

  Future<void> disposeCamera() async {
    try {
      await stopStreaming();
      await _controller?.dispose();
      _controller = null;
      _isInitialized = false;
      _isStreaming = false;
      _error = null;
      notifyListeners();
    } catch (e) {
      print('Error disposing camera: $e');
    }
  }

  /// Clear any error state
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Retry camera initialization
  Future<void> retryInitialization() async {
    await disposeCamera();
    await initialize();
  }

  /// Force camera access attempt (useful for triggering permissions on macOS)
  Future<void> forceCameraAccess() async {
    try {
      if (!isCameraSupported) {
        return;
      }

      // Try to get available cameras - this will trigger permission request on macOS
      try {
        _cameras = await availableCameras();
        if (_cameras.isNotEmpty) {
          // Try to initialize a camera controller
          _controller = CameraController(
            _cameras.first,
            ResolutionPreset.low, // Use low resolution for permission test
            enableAudio: false,
          );
          
          // This will trigger the permission request
          await _controller!.initialize();
          
          // If we get here, permission was granted
          _isInitialized = true;
          _error = null;
          
          // Clean up the test controller
          await _controller!.dispose();
          _controller = null;
          _isInitialized = false;
        }
      } catch (e) {
        // This is expected on macOS if permissions aren't granted
        print('Camera access test completed: $e');
      }
      
      notifyListeners();
    } catch (e) {
      print('Error in forceCameraAccess: $e');
    }
  }

  @override
  void dispose() {
    disposeCamera();
    super.dispose();
  }
} 