import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/gesture_provider.dart';
import '../models/hand_landmark.dart';

class GestureOverlay extends StatelessWidget {
  const GestureOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<GestureProvider>(
      builder: (context, gestureProvider, child) {
        if (gestureProvider.handLandmarks.isEmpty) {
          return const SizedBox.shrink();
        }

        return CustomPaint(
          painter: GesturePainter(gestureProvider.handLandmarks),
          child: Container(),
        );
      },
    );
  }
}

class GesturePainter extends CustomPainter {
  final List<HandLandmark> landmarks;

  GesturePainter(this.landmarks);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.green
      ..strokeWidth = 3.0
      ..style = PaintingStyle.fill;

    final linePaint = Paint()
      ..color = Colors.yellow
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    // Draw landmarks
    for (final landmark in landmarks) {
      final position = landmark.position;
      final radius = 8.0 * landmark.confidence;
      
      canvas.drawCircle(position, radius, paint);
      
      // Draw landmark label
      final textPainter = TextPainter(
        text: TextSpan(
          text: landmark.type.name,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(position.dx - textPainter.width / 2, position.dy - 20),
      );
    }

    // Draw connections between landmarks (simplified)
    if (landmarks.length >= 2) {
      for (int i = 0; i < landmarks.length - 1; i++) {
        canvas.drawLine(
          landmarks[i].position,
          landmarks[i + 1].position,
          linePaint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
} 