import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lottie/lottie.dart';
import '../providers/gesture_provider.dart';
import '../models/gesture_type.dart';

class GestureResponse extends StatefulWidget {
  const GestureResponse({super.key});

  @override
  State<GestureResponse> createState() => _GestureResponseState();
}

class _GestureResponseState extends State<GestureResponse>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));
    
    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 0.1,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<GestureProvider>(
      builder: (context, gestureProvider, child) {
        // Trigger animation when gesture changes
        if (gestureProvider.currentGesture != GestureType.none) {
          _animationController.forward().then((_) {
            _animationController.reverse();
          });
        }

        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Gesture icon with animation
              AnimatedBuilder(
                animation: _animationController,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _scaleAnimation.value,
                    child: Transform.rotate(
                      angle: _rotationAnimation.value,
                      child: _buildGestureIcon(gestureProvider.currentGesture),
                    ),
                  );
                },
              ),
              
              const SizedBox(height: 16),
              
              // Gesture name
              Text(
                _getGestureName(gestureProvider.currentGesture),
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              
              const SizedBox(height: 8),
              
              // Status text
              Text(
                gestureProvider.isProcessing 
                    ? 'Processing gesture...' 
                    : 'Show your hand to the camera',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildGestureIcon(GestureType gesture) {
    switch (gesture) {
      case GestureType.open:
        return const Icon(
          Icons.pan_tool,
          size: 64,
          color: Colors.green,
        );
      case GestureType.closed:
        return const Icon(
          Icons.pan_tool,
          size: 64,
          color: Colors.red,
        );
      case GestureType.wave:
        return const Icon(
          Icons.waving_hand,
          size: 64,
          color: Colors.blue,
        );
      case GestureType.point:
        return const Icon(
          Icons.back_hand,
          size: 64,
          color: Colors.orange,
        );
      case GestureType.thumbsUp:
        return const Icon(
          Icons.thumb_up,
          size: 64,
          color: Colors.green,
        );
      case GestureType.thumbsDown:
        return const Icon(
          Icons.thumb_down,
          size: 64,
          color: Colors.red,
        );
      case GestureType.peace:
        return const Icon(
          Icons.favorite,
          size: 64,
          color: Colors.purple,
        );
      case GestureType.ok:
        return const Icon(
          Icons.check_circle,
          size: 64,
          color: Colors.green,
        );
      case GestureType.rock:
        return const Icon(
          Icons.music_note,
          size: 64,
          color: Colors.pink,
        );
      case GestureType.paper:
        return const Icon(
          Icons.description,
          size: 64,
          color: Colors.white,
        );
      case GestureType.scissors:
        return const Icon(
          Icons.content_cut,
          size: 64,
          color: Colors.grey,
        );
      case GestureType.none:
      default:
        return const Icon(
          Icons.handshake,
          size: 64,
          color: Colors.grey,
        );
    }
  }

  String _getGestureName(GestureType gesture) {
    switch (gesture) {
      case GestureType.open:
        return 'Open Hand';
      case GestureType.closed:
        return 'Closed Fist';
      case GestureType.wave:
        return 'Waving';
      case GestureType.point:
        return 'Pointing';
      case GestureType.thumbsUp:
        return 'Thumbs Up';
      case GestureType.thumbsDown:
        return 'Thumbs Down';
      case GestureType.peace:
        return 'Peace Sign';
      case GestureType.ok:
        return 'OK Sign';
      case GestureType.rock:
        return 'Rock On!';
      case GestureType.paper:
        return 'Paper';
      case GestureType.scissors:
        return 'Scissors';
      case GestureType.none:
      default:
        return 'No Gesture Detected';
    }
  }
} 