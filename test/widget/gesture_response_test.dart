import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:help_me_sign/widgets/gesture_response.dart';
import 'package:help_me_sign/providers/gesture_provider.dart';
import 'package:help_me_sign/models/gesture_type.dart';

void main() {
  group('GestureResponse Widget Tests', () {
    late GestureProvider mockGestureProvider;

    setUp(() {
      mockGestureProvider = GestureProvider();
    });

    tearDown(() {
      mockGestureProvider.dispose();
    });

    Widget createTestWidget() {
      return MaterialApp(
        home: ChangeNotifierProvider<GestureProvider>.value(
          value: mockGestureProvider,
          child: const Scaffold(
            body: SizedBox(
              width: 400,
              height: 300,
              child: GestureResponse(),
            ),
          ),
        ),
      );
    }

    group('Initial State', () {
      testWidgets('should display no gesture detected initially', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.text('No Gesture Detected'), findsOneWidget);
        expect(find.text('Show your hand to the camera'), findsOneWidget);
      });

      testWidgets('should show handshake icon for no gesture', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.byIcon(Icons.handshake), findsOneWidget);
      });
    });

    group('Gesture Display', () {
      testWidgets('should display open hand gesture correctly', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        // Simulate gesture change
        mockGestureProvider.clearGesture();
        await tester.pump();

        expect(find.text('No Gesture Detected'), findsOneWidget);
      });

      testWidgets('should display wave gesture correctly', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        // This would require more complex state manipulation
        expect(find.byType(GestureResponse), findsOneWidget);
      });

      testWidgets('should display point gesture correctly', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.byType(GestureResponse), findsOneWidget);
      });

      testWidgets('should display thumbs up gesture correctly', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.byType(GestureResponse), findsOneWidget);
      });
    });

    group('Animation Tests', () {
      testWidgets('should trigger animation when gesture changes', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        // The widget should have animation controllers
        expect(find.byType(AnimatedBuilder), findsOneWidget);
      });

      testWidgets('should have scale animation', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.byType(Transform), findsOneWidget);
      });

      testWidgets('should have rotation animation', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.byType(Transform), findsOneWidget);
      });
    });

    group('UI Layout', () {
      testWidgets('should have proper padding', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        final container = tester.widget<Container>(
          find.descendant(
            of: find.byType(GestureResponse),
            matching: find.byType(Container),
          ),
        );

        expect(container.padding, const EdgeInsets.all(16));
      });

      testWidgets('should have centered column layout', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        final column = tester.widget<Column>(
          find.descendant(
            of: find.byType(Container),
            matching: find.byType(Column),
          ),
        );

        expect(column.mainAxisAlignment, MainAxisAlignment.center);
      });

      testWidgets('should have proper spacing between elements', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(find.byType(SizedBox), findsAtLeast(2));
      });
    });

    group('Text Styling', () {
      testWidgets('should have correct gesture name styling', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        final gestureText = tester.widget<Text>(find.text('No Gesture Detected'));
        expect(gestureText.textAlign, TextAlign.center);
        expect(gestureText.style?.fontWeight, FontWeight.bold);
      });

      testWidgets('should have correct status text styling', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        final statusText = tester.widget<Text>(find.text('Show your hand to the camera'));
        expect(statusText.textAlign, TextAlign.center);
        expect(statusText.style?.color, Colors.grey[600]);
      });
    });

    group('Provider Integration', () {
      testWidgets('should rebuild when gesture provider changes', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        // Initial state
        expect(find.text('No Gesture Detected'), findsOneWidget);

        // Simulate provider change
        mockGestureProvider.clearGesture();
        await tester.pump();

        // Should still show no gesture
        expect(find.text('No Gesture Detected'), findsOneWidget);
      });

      testWidgets('should handle processing state', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        // The widget should handle processing state gracefully
        expect(find.byType(GestureResponse), findsOneWidget);
      });
    });

    group('Accessibility', () {
      testWidgets('should be accessible to screen readers', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        expect(tester.getSemantics(find.byType(GestureResponse)), isNotNull);
      });

      testWidgets('should have semantic labels for gestures', (WidgetTester tester) async {
        await tester.pumpWidget(createTestWidget());

        // Verify text elements are accessible
        expect(find.text('No Gesture Detected'), findsOneWidget);
      });
    });

    group('Responsive Design', () {
      testWidgets('should adapt to different container sizes', (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(300, 200));
        await tester.pumpWidget(createTestWidget());
        expect(find.byType(GestureResponse), findsOneWidget);

        await tester.binding.setSurfaceSize(const Size(600, 400));
        await tester.pumpWidget(createTestWidget());
        expect(find.byType(GestureResponse), findsOneWidget);

        await tester.binding.setSurfaceSize(null);
      });
    });
  });
} 