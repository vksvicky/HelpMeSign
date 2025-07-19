import 'package:flutter_test/flutter_test.dart';
import 'package:help_me_sign/providers/gesture_provider.dart';
import 'package:help_me_sign/models/gesture_type.dart';
import 'package:help_me_sign/models/hand_landmark.dart';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import '../mocks/mock_image_processor.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  
  group('GestureProvider Tests', () {
    late GestureProvider gestureProvider;

    setUp(() {
      gestureProvider = GestureProvider();
      MockImageProcessor.reset();
    });

    tearDown(() {
      gestureProvider.dispose();
    });

    group('Image Processing', () {
      test('should process image successfully', () async {
        final mockLandmarks = MockImageProcessor.generateMockLandmarks();
        MockImageProcessor.setMockLandmarks(mockLandmarks);
        MockImageProcessor.setMockGesture(GestureType.open);

        // Create a mock image
        final mockImage = img.Image(width: 100, height: 100);

        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.handLandmarks, isNotEmpty);
        expect(gestureProvider.currentGesture, GestureType.open);
        expect(gestureProvider.error, isNull);
      });

      test('should handle processing errors', () async {
        MockImageProcessor.setShouldThrowError(true);

        final mockImage = img.Image(width: 100, height: 100);

        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.error, contains('Error processing image'));
      });

      test('should not process when already processing', () async {
        final mockImage = img.Image(width: 100, height: 100);
        
        // Start processing
        final future1 = gestureProvider.processImage(mockImage);
        final future2 = gestureProvider.processImage(mockImage);

        await future1;
        await future2;

        // Should only process once
        expect(gestureProvider.isProcessing, isFalse);
      });

      test('should handle empty image processing', () async {
        MockImageProcessor.setShouldDetectHands(false);

        final mockImage = img.Image(width: 100, height: 100);

        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.handLandmarks, isEmpty);
        expect(gestureProvider.currentGesture, GestureType.none);
      });
    });

    group('Gesture Classification', () {
      test('should classify open gesture', () async {
        final mockLandmarks = MockImageProcessor.generateMockLandmarks();
        MockImageProcessor.setMockLandmarks(mockLandmarks);
        MockImageProcessor.setMockGesture(GestureType.open);

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.currentGesture, GestureType.open);
      });

      test('should classify wave gesture', () async {
        final mockLandmarks = MockImageProcessor.generateMockLandmarks();
        MockImageProcessor.setMockLandmarks(mockLandmarks);
        MockImageProcessor.setMockGesture(GestureType.wave);

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.currentGesture, GestureType.wave);
      });

      test('should classify point gesture', () async {
        final mockLandmarks = MockImageProcessor.generateMockLandmarks();
        MockImageProcessor.setMockLandmarks(mockLandmarks);
        MockImageProcessor.setMockGesture(GestureType.point);

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.currentGesture, GestureType.point);
      });

      test('should handle no gesture detected', () async {
        MockImageProcessor.setShouldDetectHands(false);

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.currentGesture, GestureType.none);
      });
    });

    group('State Management', () {
      test('should notify listeners on state changes', () async {
        var notificationCount = 0;
        gestureProvider.addListener(() {
          notificationCount++;
        });

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(notificationCount, greaterThan(0));
      });

      test('should clear gesture correctly', () {
        gestureProvider.clearGesture();

        expect(gestureProvider.handLandmarks, isEmpty);
        expect(gestureProvider.currentGesture, GestureType.none);
        expect(gestureProvider.error, isNull);
      });

      test('should track processing state', () async {
        expect(gestureProvider.isProcessing, isFalse);

        final mockImage = img.Image(width: 100, height: 100);
        final future = gestureProvider.processImage(mockImage);

        // Should be processing while the future is pending
        expect(gestureProvider.isProcessing, isTrue);

        await future;

        expect(gestureProvider.isProcessing, isFalse);
      });
    });

    group('Landmark Data', () {
      test('should store landmark data correctly', () async {
        final mockLandmarks = MockImageProcessor.generateMockLandmarks(
          centerX: 150.0,
          centerY: 200.0,
          confidence: 0.9,
        );
        MockImageProcessor.setMockLandmarks(mockLandmarks);

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.handLandmarks.length, 3);
        expect(gestureProvider.handLandmarks.first.type, HandLandmarkType.wrist);
        expect(gestureProvider.handLandmarks.first.confidence, 0.9);
      });

      test('should handle multiple landmarks', () async {
        final mockLandmarks = [
          HandLandmark(
            type: HandLandmarkType.wrist,
            position: const Offset(100, 100),
            confidence: 0.8,
          ),
          HandLandmark(
            type: HandLandmarkType.indexTip,
            position: const Offset(120, 70),
            confidence: 0.7,
          ),
          HandLandmark(
            type: HandLandmarkType.thumbTip,
            position: const Offset(85, 75),
            confidence: 0.6,
          ),
        ];
        MockImageProcessor.setMockLandmarks(mockLandmarks);

        final mockImage = img.Image(width: 100, height: 100);
        await gestureProvider.processImage(mockImage);

        expect(gestureProvider.handLandmarks.length, 3);
        expect(gestureProvider.handLandmarks.map((l) => l.type).toSet().length, 3);
      });
    });
  });
} 