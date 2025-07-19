import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import '../models/hand_landmark.dart';
import '../models/gesture_type.dart';

class GestureProvider extends ChangeNotifier {
  List<HandLandmark> _handLandmarks = [];
  GestureType _currentGesture = GestureType.none;
  bool _isProcessing = false;
  String? _error;

  List<HandLandmark> get handLandmarks => _handLandmarks;
  GestureType get currentGesture => _currentGesture;
  bool get isProcessing => _isProcessing;
  String? get error => _error;

  Future<void> processImage(img.Image image) async {
    if (_isProcessing) return;

    _isProcessing = true;
    notifyListeners();

    try {
      // Simulate hand landmark detection
      // In a real app, this would use MediaPipe or ML Kit
      await _simulateHandDetection(image);
      _error = null;
    } catch (e) {
      _error = 'Error processing image: $e';
    } finally {
      _isProcessing = false;
      notifyListeners();
    }
  }

  Future<void> _simulateHandDetection(img.Image image) async {
    // Simulate processing delay
    await Future.delayed(const Duration(milliseconds: 100));
    
    // Generate mock landmarks based on image center
    final centerX = image.width / 2;
    final centerY = image.height / 2;
    
    _handLandmarks = [
      HandLandmark(
        type: HandLandmarkType.wrist,
        position: Offset(centerX, centerY),
        confidence: 0.8,
      ),
      HandLandmark(
        type: HandLandmarkType.indexTip,
        position: Offset(centerX + 20, centerY - 30),
        confidence: 0.7,
      ),
      HandLandmark(
        type: HandLandmarkType.thumbTip,
        position: Offset(centerX - 15, centerY - 25),
        confidence: 0.6,
      ),
    ];

    // Simple gesture classification
    _classifyGesture();
  }

  void _classifyGesture() {
    if (_handLandmarks.isEmpty) {
      _currentGesture = GestureType.none;
      return;
    }

    // Simple classification based on landmark positions
    final wrist = _handLandmarks.firstWhere(
      (landmark) => landmark.type == HandLandmarkType.wrist,
      orElse: () => _handLandmarks.first,
    );

    // Mock gesture classification
    final gestures = [GestureType.open, GestureType.wave, GestureType.point];
    _currentGesture = gestures[DateTime.now().millisecond % gestures.length];
  }

  void clearGesture() {
    _handLandmarks = [];
    _currentGesture = GestureType.none;
    _error = null;
    notifyListeners();
  }

  @override
  void dispose() {
    super.dispose();
  }
} 