import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../providers/camera_provider.dart';
import '../providers/gesture_provider.dart';
import '../services/permission_service.dart';
import '../widgets/camera_view.dart';
import '../widgets/gesture_overlay.dart';
import '../widgets/gesture_response.dart';
import 'dart:io' show Platform;

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Initialize camera when screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final cameraProvider = context.read<CameraProvider>();
      final gestureProvider = context.read<GestureProvider>();
      final permissionService = context.read<PermissionService>();
      
      // Only initialize camera if permissions are granted
      if (permissionService.canAppFunction) {
        cameraProvider.initialize();
      }
      
      // Connect camera to gesture processing
      cameraProvider.addListener(() {
        if (cameraProvider.isStreaming && cameraProvider.controller != null) {
          // This will be handled by the camera provider's image stream
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Help Me Sign'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          // Permission status indicator
          Consumer<PermissionService>(
            builder: (context, permissionService, child) {
              if (!permissionService.canAppFunction) {
                return IconButton(
                  icon: const Icon(Icons.warning, color: Colors.orange),
                  onPressed: () => _showPermissionStatusDialog(),
                  tooltip: 'Permission Status',
                );
              }
              return const SizedBox.shrink();
            },
          ),
          
          // Camera control button
          Consumer<CameraProvider>(
            builder: (context, cameraProvider, child) {
              final permissionService = context.read<PermissionService>();
              
              // Only show play/stop button if camera is supported and permissions are granted
              if (!permissionService.canAppFunction || cameraProvider.error != null) {
                return const SizedBox.shrink();
              }
              
              return IconButton(
                icon: Icon(
                  cameraProvider.isStreaming ? Icons.stop : Icons.play_arrow,
                ),
                onPressed: () {
                  if (cameraProvider.isStreaming) {
                    cameraProvider.stopStreaming();
                  } else {
                    cameraProvider.startStreaming();
                  }
                },
                tooltip: cameraProvider.isStreaming ? 'Stop Camera' : 'Start Camera',
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 3,
            child: Stack(
              children: [
                // Camera view
                const CameraView(),
                
                // Gesture overlay (only show if camera is working)
                Consumer<CameraProvider>(
                  builder: (context, cameraProvider, child) {
                    if (cameraProvider.isStreaming && cameraProvider.controller != null) {
                      return const GestureOverlay();
                    }
                    return const SizedBox.shrink();
                  },
                ),
                
                // Status indicators
                Positioned(
                  top: 16,
                  left: 16,
                  child: Consumer<CameraProvider>(
                    builder: (context, cameraProvider, child) {
                      if (cameraProvider.error != null) {
                        return Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.red.withOpacity(0.8),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.error, color: Colors.white, size: 16),
                              const SizedBox(width: 4),
                              Flexible(
                                child: Text(
                                  cameraProvider.error!,
                                  style: const TextStyle(color: Colors.white, fontSize: 12),
                                ),
                              ),
                            ],
                          ),
                        );
                      }
                      return const SizedBox.shrink();
                    },
                  ),
                ),
              ],
            ),
          ),
          
          // Gesture response area
          Expanded(
            flex: 1,
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 4,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: const GestureResponse(),
            ),
          ),
        ],
      ),
    );
  }

  void _showPermissionStatusDialog() {
    final permissionService = context.read<PermissionService>();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Permission Status'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPermissionStatusRow(
              'Camera',
              permissionService.cameraStatus,
              Icons.camera_alt,
              isRequired: true,
            ),
            const SizedBox(height: 12),
            _buildPermissionStatusRow(
              'Microphone',
              permissionService.microphoneStatus,
              Icons.mic,
              isRequired: false,
            ),
            const SizedBox(height: 16),
            if (!permissionService.canAppFunction)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Camera access is required for the app to function properly.',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      permissionService.getPermissionInstructions(),
                      style: const TextStyle(fontSize: 14),
                    ),
                  ],
                ),
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
          if (!permissionService.canAppFunction)
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _openAppSettings();
              },
              child: const Text('Open Settings'),
            ),
        ],
      ),
    );
  }

  Widget _buildPermissionStatusRow(
    String permissionName,
    PermissionStatus status,
    IconData icon, {
    required bool isRequired,
  }) {
    Color statusColor;
    String statusText;
    
    switch (status) {
      case PermissionStatus.granted:
        statusColor = Colors.green;
        statusText = 'Granted';
        break;
      case PermissionStatus.denied:
        statusColor = Colors.orange;
        statusText = 'Denied';
        break;
      case PermissionStatus.permanentlyDenied:
        statusColor = Colors.red;
        statusText = 'Permanently Denied';
        break;
      case PermissionStatus.restricted:
        statusColor = Colors.red;
        statusText = 'Restricted';
        break;
      default:
        statusColor = Colors.grey;
        statusText = 'Not Determined';
    }

    return Row(
      children: [
        Icon(icon, size: 20, color: statusColor),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            permissionName,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ),
        if (isRequired)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'Required',
              style: TextStyle(fontSize: 10, color: Colors.blue),
            ),
          ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: statusColor.withOpacity(0.3)),
          ),
          child: Text(
            statusText,
            style: TextStyle(
              fontSize: 12,
              color: statusColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
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
} 