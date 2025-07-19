import 'package:flutter/material.dart';

enum HandLandmarkType {
  wrist,
  thumbTip,
  thumbIp,
  thumbMp,
  thumbMcp,
  indexTip,
  indexDip,
  indexPip,
  indexMcp,
  middleTip,
  middleDip,
  middlePip,
  middleMcp,
  ringTip,
  ringDip,
  ringPip,
  ringMcp,
  pinkyTip,
  pinkyDip,
  pinkyPip,
  pinkyMcp,
  elbow,
  shoulder,
}

class HandLandmark {
  final HandLandmarkType type;
  final Offset position;
  final double confidence;

  const HandLandmark({
    required this.type,
    required this.position,
    required this.confidence,
  });

  @override
  String toString() {
    return 'HandLandmark(type: $type, position: $position, confidence: $confidence)';
  }
} 