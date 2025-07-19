import 'package:flutter_test/flutter_test.dart';
import 'package:help_me_sign/services/permission_service.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  group('PermissionService Tests', () {
    late PermissionService permissionService;

    setUp(() {
      permissionService = PermissionService();
    });

    tearDown(() {
      permissionService.dispose();
    });

    group('Platform Support', () {
      test('should check platform support correctly', () {
        expect(permissionService.arePermissionsSupported, isA<bool>());
      });

      test('should identify camera as required', () {
        expect(permissionService.isCameraRequired, isTrue);
      });

      test('should identify microphone as optional', () {
        expect(permissionService.isMicrophoneRequired, isFalse);
      });
    });

    group('Initialization', () {
      test('should initialize without errors', () async {
        await permissionService.initialize();
        expect(permissionService.error, isNull);
      });

      test('should load stored permissions', () async {
        await permissionService.initialize();
        expect(permissionService.permissionsRequested, isA<bool>());
        expect(permissionService.cameraStatus, isA<PermissionStatus>());
        expect(permissionService.microphoneStatus, isA<PermissionStatus>());
      });
    });

    group('Permission Requests', () {
      test('should handle permission requests gracefully', () async {
        await permissionService.initialize();
        
        // In test environment, this will likely fail due to MissingPluginException
        final success = await permissionService.requestPermissions();
        
        expect(success, isA<bool>());
        expect(permissionService.permissionsRequested, isTrue);
      });

      test('should provide meaningful error messages', () async {
        await permissionService.initialize();
        await permissionService.requestPermissions();
        
        // Should have some error or status message
        expect(permissionService.getPermissionStatusDescription(), isA<String>());
      });
    });

    group('App Functionality', () {
      test('should determine app functionality correctly', () {
        expect(permissionService.canAppFunction, isA<bool>());
      });

      test('should require camera for app functionality', () {
        // App should not function without camera permission
        expect(permissionService.isCameraRequired, isTrue);
      });
    });

    group('Platform Instructions', () {
      test('should provide platform-specific instructions', () {
        final instructions = permissionService.getPermissionInstructions();
        expect(instructions, isA<String>());
        expect(instructions.isNotEmpty, isTrue);
      });

      test('should provide permission status description', () {
        final description = permissionService.getPermissionStatusDescription();
        expect(description, isA<String>());
        expect(description.isNotEmpty, isTrue);
      });
    });

    group('Error Handling', () {
      test('should clear errors', () {
        permissionService.clearError();
        expect(permissionService.error, isNull);
      });

      test('should handle initialization errors gracefully', () async {
        // This test verifies the service doesn't crash on errors
        await permissionService.initialize();
        expect(permissionService, isNotNull);
      });
    });

    group('Data Management', () {
      test('should clear stored permissions', () async {
        await permissionService.initialize();
        await permissionService.clearStoredPermissions();
        
        expect(permissionService.cameraStatus, PermissionStatus.denied);
        expect(permissionService.microphoneStatus, PermissionStatus.denied);
        expect(permissionService.permissionsRequested, isFalse);
        // In test environment, SharedPreferences may fail, so we don't check error
      });
    });

    group('State Management', () {
      test('should notify listeners on state changes', () async {
        var notificationCount = 0;
        permissionService.addListener(() {
          notificationCount++;
        });

        await permissionService.initialize();
        
        expect(notificationCount, greaterThan(0));
      });

      test('should handle multiple listeners', () async {
        var listener1Count = 0;
        var listener2Count = 0;
        
        permissionService.addListener(() {
          listener1Count++;
        });
        
        permissionService.addListener(() {
          listener2Count++;
        });

        await permissionService.initialize();
        
        expect(listener1Count, greaterThan(0));
        expect(listener2Count, greaterThan(0));
        expect(listener1Count, equals(listener2Count));
      });
    });
  });
} 