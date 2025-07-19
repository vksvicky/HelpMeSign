import 'package:camera/camera.dart';

class MockCameraController {
  bool _isInitialized = false;
  bool _isStreaming = false;
  String? _error;

  bool get isInitialized => _isInitialized;
  bool get isStreaming => _isStreaming;
  String? get error => _error;

  Future<void> initialize() async {
    await Future.delayed(const Duration(milliseconds: 100));
    _isInitialized = true;
    _error = null;
  }

  Future<void> startImageStream(Function(CameraImage) onImage) async {
    if (!_isInitialized) {
      _error = 'Camera not initialized';
      return;
    }
    
    await Future.delayed(const Duration(milliseconds: 50));
    _isStreaming = true;
    _error = null;
  }

  Future<void> stopImageStream() async {
    await Future.delayed(const Duration(milliseconds: 50));
    _isStreaming = false;
  }

  Future<void> dispose() async {
    await Future.delayed(const Duration(milliseconds: 50));
    _isInitialized = false;
    _isStreaming = false;
  }

  CameraDescription get description => const CameraDescription(
        name: 'Mock Camera',
        lensDirection: CameraLensDirection.back,
        sensorOrientation: 0,
      );

  void setError(String error) {
    _error = error;
  }

  void reset() {
    _isInitialized = false;
    _isStreaming = false;
    _error = null;
  }
} 