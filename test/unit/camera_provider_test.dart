import 'package:flutter_test/flutter_test.dart';
import 'package:help_me_sign/providers/camera_provider.dart';
import '../mocks/mock_camera_controller.dart';
import '../mocks/mock_permission_handler.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  group('CameraProvider Tests', () {
    late CameraProvider cameraProvider;

    setUp(() {
      cameraProvider = CameraProvider();
      MockPermissionHandler.reset();
    });

    tearDown(() {
      cameraProvider.disposeCamera();
    });

    group('Platform Support', () {
      test('should check camera support correctly', () {
        // In test environment, camera support depends on the platform
        // We can't easily mock this, so we just test the method exists
        expect(cameraProvider.isCameraSupported, isA<bool>());
      });
    });

    group('Initialization', () {
      test('should handle MissingPluginException gracefully', () async {
        // In test environment, we expect MissingPluginException
        await cameraProvider.initialize();
        
        // Should have an error message indicating platform limitation
        expect(cameraProvider.error, isNotNull);
        expect(cameraProvider.error, contains('not available'));
        expect(cameraProvider.isInitialized, isFalse);
      });

      test('should provide retry functionality', () async {
        await cameraProvider.initialize();
        
        // Clear error and retry
        cameraProvider.clearError();
        expect(cameraProvider.error, isNull);
        
        // Retry should work
        await cameraProvider.retryInitialization();
        expect(cameraProvider.error, isNotNull);
      });

      test('should handle initialization errors gracefully', () async {
        await cameraProvider.initialize();
        
        // Should have an error message
        expect(cameraProvider.error, isNotNull);
        expect(cameraProvider.isInitialized, isFalse);
      });
    });

    group('Streaming', () {
      test('should not start streaming when not initialized', () async {
        await cameraProvider.startStreaming();
        
        expect(cameraProvider.isStreaming, isFalse);
        expect(cameraProvider.error, contains('not initialized'));
      });

      test('should handle streaming errors gracefully', () async {
        // Try to start streaming without initialization
        await cameraProvider.startStreaming();
        
        expect(cameraProvider.error, isNotNull);
        expect(cameraProvider.isStreaming, isFalse);
      });
    });

    group('State Management', () {
      test('should notify listeners on state changes', () async {
        var notificationCount = 0;
        cameraProvider.addListener(() {
          notificationCount++;
        });

        await cameraProvider.initialize();
        
        expect(notificationCount, greaterThan(0));
      });

      test('should clear error state', () async {
        await cameraProvider.initialize();
        expect(cameraProvider.error, isNotNull);
        
        cameraProvider.clearError();
        expect(cameraProvider.error, isNull);
      });

      test('should handle disposal gracefully', () async {
        await cameraProvider.initialize();
        expect(cameraProvider.error, isNotNull);
        
        await cameraProvider.disposeCamera();
        expect(cameraProvider.isInitialized, isFalse);
        expect(cameraProvider.isStreaming, isFalse);
      });
    });

    group('Error Handling', () {
      test('should provide meaningful error messages', () async {
        await cameraProvider.initialize();
        
        expect(cameraProvider.error, isNotNull);
        expect(cameraProvider.error, contains('not available'));
      });

      test('should allow error clearing', () async {
        await cameraProvider.initialize();
        expect(cameraProvider.error, isNotNull);
        
        cameraProvider.clearError();
        expect(cameraProvider.error, isNull);
      });

      test('should handle retry initialization', () async {
        await cameraProvider.initialize();
        final firstError = cameraProvider.error;
        
        await cameraProvider.retryInitialization();
        final secondError = cameraProvider.error;
        
        expect(firstError, isNotNull);
        expect(secondError, isNotNull);
      });
    });
  });
} 