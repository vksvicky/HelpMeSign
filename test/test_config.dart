import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:help_me_sign/providers/camera_provider.dart';
import 'package:help_me_sign/providers/gesture_provider.dart';

/// Test configuration and utilities for the Help Me Sign app
class TestConfig {
  static const Duration defaultTimeout = Duration(seconds: 30);
  static const Duration shortTimeout = Duration(seconds: 5);
  static const Duration animationTimeout = Duration(milliseconds: 500);

  /// Common screen sizes for testing
  static const Map<String, Size> screenSizes = {
    'mobile_portrait': Size(400, 800),
    'mobile_landscape': Size(800, 400),
    'tablet': Size(1024, 768),
    'desktop': Size(1920, 1080),
  };

  /// Creates a test app with mocked providers
  static Widget createTestApp({
    CameraProvider? cameraProvider,
    GestureProvider? gestureProvider,
    Widget? child,
  }) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<CameraProvider>.value(
          value: cameraProvider ?? CameraProvider(),
        ),
        ChangeNotifierProvider<GestureProvider>.value(
          value: gestureProvider ?? GestureProvider(),
        ),
      ],
      child: child ?? const MaterialApp(home: Scaffold()),
    );
  }

  /// Sets up test environment with specific screen size
  static Future<void> setupTestEnvironment(
    WidgetTester tester, {
    Size? screenSize,
    Duration? timeout,
  }) async {
    if (screenSize != null) {
      await tester.binding.setSurfaceSize(screenSize);
    }
    
    if (timeout != null) {
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        const MethodChannel('flutter/settings'),
        (MethodCall methodCall) async {
          if (methodCall.method == 'getPlatformVersion') {
            return 'Test Platform';
          }
          return null;
        },
      );
    }
  }

  /// Cleans up test environment
  static Future<void> cleanupTestEnvironment(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(null);
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
      const MethodChannel('flutter/settings'),
      null,
    );
  }

  /// Waits for animations to complete
  static Future<void> waitForAnimations(WidgetTester tester) async {
    await tester.pumpAndSettle(animationTimeout);
  }

  /// Waits for async operations to complete
  static Future<void> waitForAsync(WidgetTester tester) async {
    await tester.pumpAndSettle(shortTimeout);
  }

  /// Finds widget by type with timeout
  static Future<Finder> findWidgetByType<T>(
    WidgetTester tester, {
    Duration? timeout,
  }) async {
    final finder = find.byType(T);
    await tester.pumpAndSettle(timeout ?? shortTimeout);
    return finder;
  }

  /// Finds widget by text with timeout
  static Future<Finder> findWidgetByText(
    WidgetTester tester,
    String text, {
    Duration? timeout,
  }) async {
    final finder = find.text(text);
    await tester.pumpAndSettle(timeout ?? shortTimeout);
    return finder;
  }

  /// Verifies widget exists with timeout
  static Future<void> expectWidgetExists<T>(
    WidgetTester tester, {
    Duration? timeout,
  }) async {
    final finder = await findWidgetByType<T>(tester, timeout: timeout);
    expect(finder, findsOneWidget);
  }

  /// Verifies text exists with timeout
  static Future<void> expectTextExists(
    WidgetTester tester,
    String text, {
    Duration? timeout,
  }) async {
    final finder = await findWidgetByText(tester, text, timeout: timeout);
    expect(finder, findsOneWidget);
  }

  /// Mocks camera permissions
  static void mockCameraPermissions(bool granted) {
    // This would be implemented with actual permission mocking
  }

  /// Mocks gesture detection
  static void mockGestureDetection(bool detected) {
    // This would be implemented with actual gesture mocking
  }

  /// Creates mock image data
  static List<int> createMockImageData({
    int width = 100,
    int height = 100,
  }) {
    // Create a simple mock image data
    final bytes = <int>[];
    for (int i = 0; i < width * height * 4; i++) {
      bytes.add(i % 256);
    }
    return bytes;
  }

  /// Test data for different gestures
  static const Map<String, dynamic> testGestures = {
    'open_hand': {
      'name': 'Open Hand',
      'icon': Icons.pan_tool,
      'color': Colors.green,
    },
    'wave': {
      'name': 'Waving',
      'icon': Icons.waving_hand,
      'color': Colors.blue,
    },
    'point': {
      'name': 'Pointing',
      'icon': Icons.back_hand,
      'color': Colors.orange,
    },
    'thumbs_up': {
      'name': 'Thumbs Up',
      'icon': Icons.thumb_up,
      'color': Colors.green,
    },
  };

  /// Error scenarios for testing
  static const Map<String, String> errorScenarios = {
    'camera_permission_denied': 'Camera permission denied',
    'camera_not_available': 'No cameras available',
    'camera_initialization_failed': 'Failed to initialize camera',
    'gesture_processing_error': 'Error processing image',
    'network_error': 'Network connection error',
    'unknown_error': 'An unknown error occurred',
  };
} 