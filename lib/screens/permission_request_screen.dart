import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../services/permission_service.dart';
import '../widgets/permission_explanation_card.dart';
import 'dart:io' show Platform;
import '../providers/camera_provider.dart';

class PermissionRequestScreen extends StatefulWidget {
  const PermissionRequestScreen({super.key});

  @override
  State<PermissionRequestScreen> createState() => _PermissionRequestScreenState();
}

class _PermissionRequestScreenState extends State<PermissionRequestScreen> {
  bool _isRequesting = false;

  @override
  void initState() {
    super.initState();
    _initializePermissions();
  }

  Future<void> _initializePermissions() async {
    final permissionService = context.read<PermissionService>();
    await permissionService.initialize();
  }

  Future<void> _requestPermissions() async {
    setState(() {
      _isRequesting = true;
    });

    try {
      final permissionService = context.read<PermissionService>();
      final cameraProvider = context.read<CameraProvider>();
      
      // On macOS, force camera access attempt to trigger permission request
      if (Platform.isMacOS) {
        await cameraProvider.forceCameraAccess();
      }
      
      final success = await permissionService.requestPermissions();

      if (success) {
        // Navigate to main app
        if (mounted) {
          Navigator.of(context).pushReplacementNamed('/home');
        }
      } else {
        // Show error or retry options
        if (mounted) {
          _showPermissionErrorDialog();
        }
      }
    } catch (e) {
      if (mounted) {
        _showErrorDialog('Failed to request permissions: $e');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isRequesting = false;
        });
      }
    }
  }

  void _showPermissionErrorDialog() {
    final permissionService = context.read<PermissionService>();
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Camera Permission Required'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Help Me Sign needs camera access to detect hand gestures and provide sign language recognition.',
            ),
            const SizedBox(height: 16),
            Text(
              permissionService.getPermissionInstructions(),
              style: const TextStyle(fontSize: 14, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _openAppSettings();
            },
            child: const Text('Open Settings'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _requestPermissions();
            },
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Future<void> _openAppSettings() async {
    try {
          final permissionService = context.read<PermissionService>();
      final success = await permissionService.openAppSettings();
      
      if (!success && mounted) {
        // If opening settings failed, show instructions dialog
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Open Settings'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Please manually open your system settings to enable camera permissions:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    permissionService.getPermissionInstructions(),
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  child: const Text('OK'),
                ),
              ],
            ),
          );
      }
    } catch (e) {
      if (mounted) {
        // Show error dialog if something went wrong
        final permissionService = context.read<PermissionService>();
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Error Opening Settings'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Unable to open system settings automatically. Please manually enable camera permissions:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                Text(
                  permissionService.getPermissionInstructions(),
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: MediaQuery.of(context).size.height - 
                        MediaQuery.of(context).padding.top - 
                        MediaQuery.of(context).padding.bottom - 48, // 24*2 for padding
            ),
            child: IntrinsicHeight(
          child: Column(
            children: [
              // Header
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 32.0),
                child: Column(
                  children: [
                    Icon(
                      Icons.camera_alt,
                      size: 80,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Welcome to Help Me Sign',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'We need camera access to help you with sign language recognition',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),

              // Permission explanation cards
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16.0),
                child: Column(
                  children: [
                    PermissionExplanationCard(
                      icon: Icons.camera_alt,
                      title: 'Camera Access',
                      description: 'Required to detect hand gestures and provide real-time sign language recognition.',
                      isRequired: true,
                    ),
                    const SizedBox(height: 16),
                    PermissionExplanationCard(
                      icon: Icons.mic,
                      title: 'Microphone Access',
                      description: 'Optional for voice commands and audio feedback (not currently used).',
                      isRequired: false,
                    ),
                  ],
                ),
              ),

                  // Spacer to push content to bottom when there's extra space
                  const Spacer(),

              // Action buttons
                  Padding(
                    padding: const EdgeInsets.only(top: 32.0),
                child: Column(
                  children: [
                    Consumer<PermissionService>(
                      builder: (context, permissionService, child) {
                        if (permissionService.error != null) {
                          return Container(
                            padding: const EdgeInsets.all(12),
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: Colors.red.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.red.withOpacity(0.3)),
                            ),
                            child: Row(
                              children: [
                                Icon(Icons.error, color: Colors.red, size: 20),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    permissionService.error!,
                                    style: TextStyle(color: Colors.red[700]),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }
                        return const SizedBox.shrink();
                      },
                    ),
                    
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _isRequesting ? null : _requestPermissions,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          backgroundColor: Theme.of(context).colorScheme.primary,
                          foregroundColor: Theme.of(context).colorScheme.onPrimary,
                        ),
                        child: _isRequesting
                            ? const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                    ),
                                  ),
                                  SizedBox(width: 12),
                                  Text('Requesting Permissions...'),
                                ],
                              )
                            : const Text(
                                'Grant Permissions',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    TextButton(
                      onPressed: () {
                        // Show more information about permissions
                        _showPermissionInfoDialog();
                      },
                      child: const Text('Learn More About Permissions'),
                    ),
                  ],
                ),
              ),
            ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _showPermissionInfoDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('About Permissions'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Help Me Sign uses the following permissions:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Text(
              '📷 Camera: Required for hand gesture recognition. The app analyzes your hand movements to detect sign language gestures.',
            ),
            SizedBox(height: 8),
            Text(
              '🎤 Microphone: Currently optional and not used. May be used in future updates for voice commands.',
            ),
            SizedBox(height: 16),
            Text(
              'Your privacy is important to us. Camera data is processed locally on your device and is not sent to any servers.',
              style: TextStyle(fontStyle: FontStyle.italic),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
} 