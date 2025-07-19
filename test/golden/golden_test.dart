import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:help_me_sign/providers/camera_provider.dart';
import 'package:help_me_sign/providers/gesture_provider.dart';

void main() {
  group('Golden Tests', () {
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

    Widget createSimpleTestWidget() {
      return MaterialApp(
        home: Scaffold(
          body: Center(
            child: Container(
              width: 300,
              height: 200,
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(
                child: Text(
                  'Help Me Sign',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ),
      );
    }

    group('Simple Screenshots', () {
      testWidgets('should match basic app layout', (WidgetTester tester) async {
        await tester.pumpWidget(createSimpleTestWidget());
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('basic_app_layout.png'),
        );
      });

      testWidgets('should match light theme', (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.light(),
            home: Scaffold(
              body: Center(
                child: Container(
                  width: 200,
                  height: 100,
                  color: Colors.grey[200],
                  child: const Center(
                    child: Text('Light Theme'),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('light_theme.png'),
        );
      });

      testWidgets('should match dark theme', (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.dark(),
            home: Scaffold(
              body: Center(
                child: Container(
                  width: 200,
                  height: 100,
                  color: Colors.grey[800],
                  child: const Center(
                    child: Text(
                      'Dark Theme',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('dark_theme.png'),
        );
      });
    });

    group('Responsive Design Screenshots', () {
      testWidgets('should match mobile portrait layout', (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(400, 800));
        await tester.pumpWidget(createSimpleTestWidget());
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('mobile_portrait_layout.png'),
        );

        await tester.binding.setSurfaceSize(null);
      });

      testWidgets('should match mobile landscape layout', (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(800, 400));
        await tester.pumpWidget(createSimpleTestWidget());
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('mobile_landscape_layout.png'),
        );

        await tester.binding.setSurfaceSize(null);
      });

      testWidgets('should match tablet layout', (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(1024, 768));
        await tester.pumpWidget(createSimpleTestWidget());
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('tablet_layout.png'),
        );

        await tester.binding.setSurfaceSize(null);
      });

      testWidgets('should match desktop layout', (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(1920, 1080));
        await tester.pumpWidget(createSimpleTestWidget());
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(MaterialApp),
          matchesGoldenFile('desktop_layout.png'),
        );

        await tester.binding.setSurfaceSize(null);
      });
    });

    group('Component Screenshots', () {
      testWidgets('should match button component', (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Center(
                child: ElevatedButton(
                  onPressed: () {},
                  child: const Text('Test Button'),
                ),
              ),
            ),
          ),
        );
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(ElevatedButton),
          matchesGoldenFile('button_component.png'),
        );
      });

      testWidgets('should match card component', (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Center(
                child: Card(
                  child: Container(
                    width: 200,
                    height: 100,
                    padding: const EdgeInsets.all(16),
                    child: const Text('Test Card'),
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.pump(const Duration(milliseconds: 100));

        await expectLater(
          find.byType(Card),
          matchesGoldenFile('card_component.png'),
        );
      });
    });
  });
} 