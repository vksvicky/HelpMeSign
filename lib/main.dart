import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'screens/home_screen.dart';
import 'screens/permission_request_screen.dart';
import 'providers/gesture_provider.dart';
import 'providers/camera_provider.dart';
import 'services/permission_service.dart';

void main() {
  runApp(const HelpMeSignApp());
}

class HelpMeSignApp extends StatelessWidget {
  const HelpMeSignApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => PermissionService()),
        ChangeNotifierProvider(create: (_) => CameraProvider()),
        ChangeNotifierProvider(create: (_) => GestureProvider()),
      ],
      child: MaterialApp(
        title: 'Help Me Sign',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
          brightness: Brightness.light,
        ),
        darkTheme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
          brightness: Brightness.dark,
        ),
        home: const AppInitializer(),
        routes: {
          '/home': (context) => const HomeScreen(),
          '/permissions': (context) => const PermissionRequestScreen(),
        },
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class AppInitializer extends StatefulWidget {
  const AppInitializer({super.key});

  @override
  State<AppInitializer> createState() => _AppInitializerState();
}

class _AppInitializerState extends State<AppInitializer> {
  bool _isInitializing = true;
  bool _hasPermissions = false;

  @override
  void initState() {
    super.initState();
    _initializeApp();
  }

  Future<void> _initializeApp() async {
    try {
      final permissionService = context.read<PermissionService>();
      await permissionService.initialize();

      // Check if permissions have been requested before
      if (permissionService.permissionsRequested) {
        // If permissions were previously requested, check current status
        if (permissionService.canAppFunction) {
          _hasPermissions = true;
        } else {
          // Permissions were denied, show permission screen
          _hasPermissions = false;
        }
      } else {
        // First time launch, show permission screen
        _hasPermissions = false;
      }
    } catch (e) {
      // Handle initialization errors
      _hasPermissions = false;
    } finally {
      if (mounted) {
        setState(() {
          _isInitializing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isInitializing) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Initializing Help Me Sign...'),
            ],
          ),
        ),
      );
    }

    // Navigate to appropriate screen based on permission status
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_hasPermissions) {
        Navigator.of(context).pushReplacementNamed('/home');
      } else {
        Navigator.of(context).pushReplacementNamed('/permissions');
      }
    });

    // Show loading while navigating
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
