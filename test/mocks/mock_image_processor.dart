import 'package:image/image.dart' as img;
import 'package:flutter/material.dart';
import 'package:help_me_sign/models/hand_landmark.dart';
import 'package:help_me_sign/models/gesture_type.dart';

class MockImageProcessor {
  static bool _shouldDetectHands = true;
  static List<HandLandmark> _mockLandmarks = [];
  static GestureType _mockGesture = GestureType.none;
  static bool _shouldThrowError = false;

  static void setShouldDetectHands(bool shouldDetect) {
    _shouldDetectHands = shouldDetect;
  }

  static void setMockLandmarks(List<HandLandmark> landmarks) {
    _mockLandmarks = landmarks;
  }

  static void setMockGesture(GestureType gesture) {
    _mockGesture = gesture;
  }

  static void setShouldThrowError(bool shouldThrow) {
    _shouldThrowError = shouldThrow;
  }

  static Future<List<HandLandmark>> processImage(img.Image image) async {
    await Future.delayed(const Duration(milliseconds: 100));
    
    if (_shouldThrowError) {
      throw Exception('Mock image processing error');
    }
    
    if (!_shouldDetectHands) {
      return [];
    }
    
    return _mockLandmarks;
  }

  static Future<GestureType> classifyGesture(List<HandLandmark> landmarks) async {
    await Future.delayed(const Duration(milliseconds: 50));
    
    if (_shouldThrowError) {
      throw Exception('Mock gesture classification error');
    }
    
    return _mockGesture;
  }

  static List<HandLandmark> generateMockLandmarks({
    double centerX = 100.0,
    double centerY = 100.0,
    double confidence = 0.8,
  }) {
    return [
      HandLandmark(
        type: HandLandmarkType.wrist,
        position: Offset(centerX, centerY),
        confidence: confidence,
      ),
      HandLandmark(
        type: HandLandmarkType.indexTip,
        position: Offset(centerX + 20, centerY - 30),
        confidence: confidence * 0.9,
      ),
      HandLandmark(
        type: HandLandmarkType.thumbTip,
        position: Offset(centerX - 15, centerY - 25),
        confidence: confidence * 0.8,
      ),
    ];
  }

  static void reset() {
    _shouldDetectHands = true;
    _mockLandmarks = [];
    _mockGesture = GestureType.none;
    _shouldThrowError = false;
  }
} 