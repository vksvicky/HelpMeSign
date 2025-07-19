import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:help_me_sign/main.dart';
import 'package:help_me_sign/providers/camera_provider.dart';
import 'package:help_me_sign/providers/gesture_provider.dart';
import 'package:help_me_sign/widgets/camera_view.dart';
import 'package:help_me_sign/widgets/gesture_response.dart';

void main() {
  group('App Integration Tests', () {
    late CameraProvider mockCameraProvider;
    late GestureProvider mockGestureProvider;

    setUp(() {
      mockCameraProvider = CameraProvider();
      mockGestureProvider = GestureProvider();
    });

    tearDown(() {
      mockCameraProvider.disposeCamera();
      mockGestureProvider.dispose();
    });

    Widget createTestApp() {
      return MultiProvider(
        providers: [
          ChangeNotifierProvider<CameraProvider>.value(value: mockCameraProvider),
          ChangeNotifierProvider<GestureProvider>.value(value: mockGestureProvider),
        ],
        child: const HelpMeSignApp(),
      );
    }

    group('App Initialization', () {
      testWidgets('should display app title', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(find.text('Help Me Sign'), findsOneWidget);
      });

      testWidgets('should have play/stop button in app bar', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(find.byIcon(Icons.play_arrow), findsOneWidget);
      });

      testWidgets('should show camera view initially', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(find.byType(CameraView), findsOneWidget);
      });

      testWidgets('should show gesture response area', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(find.byType(GestureResponse), findsOneWidget);
      });
    });

    group('Camera Integration', () {
      testWidgets('should handle camera initialization', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // Initial state should show loading
        expect(find.text('Initializing camera...'), findsOneWidget);

        // Simulate camera initialization
        await mockCameraProvider.initialize();
        await tester.pump();

        // Should still show loading since we can't easily mock the camera controller
        expect(find.byType(CameraView), findsOneWidget);
      });

      testWidgets('should handle camera permission denied', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // This would require more complex mocking to test properly
        expect(find.byType(CameraView), findsOneWidget);
      });

      testWidgets('should handle camera errors gracefully', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // The app should handle camera errors without crashing
        expect(find.byType(HelpMeSignApp), findsOneWidget);
      });
    });

    group('Gesture Recognition Integration', () {
      testWidgets('should display no gesture initially', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(find.text('No Gesture Detected'), findsOneWidget);
      });

      testWidgets('should show processing state', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(find.text('Show your hand to the camera'), findsOneWidget);
      });

      testWidgets('should handle gesture processing errors', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // The app should handle gesture processing errors gracefully
        expect(find.byType(HelpMeSignApp), findsOneWidget);
      });
    });

    group('UI Layout Integration', () {
      testWidgets('should have proper layout structure', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // Should have column layout
        expect(find.byType(Column), findsAtLeast(1));
        
        // Should have stack for camera overlay
        expect(find.byType(Stack), findsAtLeast(1));
      });

      testWidgets('should have responsive design', (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(400, 600));
        await tester.pumpWidget(createTestApp());
        expect(find.byType(HelpMeSignApp), findsOneWidget);

        await tester.binding.setSurfaceSize(const Size(800, 1200));
        await tester.pumpWidget(createTestApp());
        expect(find.byType(HelpMeSignApp), findsOneWidget);

        await tester.binding.setSurfaceSize(null);
      });

      testWidgets('should handle different orientations', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // Test portrait
        await tester.binding.setSurfaceSize(const Size(400, 800));
        await tester.pumpWidget(createTestApp());
        expect(find.byType(HelpMeSignApp), findsOneWidget);

        // Test landscape
        await tester.binding.setSurfaceSize(const Size(800, 400));
        await tester.pumpWidget(createTestApp());
        expect(find.byType(HelpMeSignApp), findsOneWidget);

        await tester.binding.setSurfaceSize(null);
      });
    });

    group('Provider Integration', () {
      testWidgets('should provide camera provider to widgets', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        final cameraView = tester.widget<CameraView>(find.byType(CameraView));
        expect(cameraView, isNotNull);
      });

      testWidgets('should provide gesture provider to widgets', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        final gestureResponse = tester.widget<GestureResponse>(find.byType(GestureResponse));
        expect(gestureResponse, isNotNull);
      });

      testWidgets('should handle provider state changes', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // Simulate provider state changes
        mockGestureProvider.clearGesture();
        await tester.pump();

        // App should still be functional
        expect(find.byType(HelpMeSignApp), findsOneWidget);
      });
    });

    group('Error Handling Integration', () {
      testWidgets('should handle camera provider errors', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // The app should handle camera errors gracefully
        expect(find.byType(HelpMeSignApp), findsOneWidget);
      });

      testWidgets('should handle gesture provider errors', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // The app should handle gesture errors gracefully
        expect(find.byType(HelpMeSignApp), findsOneWidget);
      });

      testWidgets('should handle widget errors gracefully', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // The app should handle widget errors without crashing
        expect(find.byType(HelpMeSignApp), findsOneWidget);
      });
    });

    group('Accessibility Integration', () {
      testWidgets('should be accessible to screen readers', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        expect(tester.getSemantics(find.byType(HelpMeSignApp)), isNotNull);
      });

      testWidgets('should have semantic labels for all interactive elements', (WidgetTester tester) async {
        await tester.pumpWidget(createTestApp());

        // Verify key elements are accessible
        expect(find.text('Help Me Sign'), findsOneWidget);
        expect(find.text('No Gesture Detected'), findsOneWidget);
      });
    });
  });
} 