# Help Me Sign

A cross-platform Flutter application that uses real-time camera processing and machine learning to recognize hand gestures and respond with animated hand gestures.

**Developed by [CycleRunCode Club](https://cycleruncode.club)**

**Version:** 1.0.0  
**Website:** https://cycleruncode.club

## Features

- **Cross-platform support**: iOS, Android, macOS, Windows, and Web
- **Real-time camera processing**: Live camera feed with gesture recognition
- **Hand gesture recognition**: Detects various hand gestures using MediaPipe
- **Smooth animations**: Skia-based rendering for fluid gesture responses
- **Modern UI**: Material Design 3 with dark/light theme support

## Supported Gestures

- Open Hand
- Closed Fist
- Waving
- Pointing
- Thumbs Up/Down
- Peace Sign
- OK Sign
- Rock, Paper, Scissors

## Technology Stack

- **Flutter**: Cross-platform UI framework
- **Camera**: Real-time camera access and processing
- **Google ML Kit**: Hand tracking and pose detection
- **TensorFlow Lite**: Machine learning model inference
- **Provider**: State management
- **Lottie**: Smooth animations
- **Skia**: Custom rendering and animations

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/
│   ├── gesture_type.dart     # Gesture type definitions
│   └── hand_landmark.dart    # Hand landmark data model
├── providers/
│   ├── camera_provider.dart  # Camera management
│   └── gesture_provider.dart # Gesture recognition
├── screens/
│   └── home_screen.dart      # Main app screen
└── widgets/
    ├── camera_view.dart      # Camera preview widget
    ├── gesture_overlay.dart  # Hand landmark visualization
    └── gesture_response.dart # Animated gesture responses
```

## Getting Started

### Prerequisites

- Flutter SDK (3.8.1 or higher)
- Dart SDK
- Android Studio / Xcode (for mobile development)
- Visual Studio (for Windows development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd help_me_sign
```

2. Install dependencies:
```bash
flutter pub get
```

3. Run the app:
```bash
# For mobile
flutter run

# For web
flutter run -d chrome

# For desktop
flutter run -d macos  # macOS
flutter run -d windows # Windows
```

# For other environments
flutter run -d ios  # iOS
flutter run -d android # Android
flutter run -d web # Web
```

### For Distribution
# Build universal macOS app (when current build completes)
```
flutter build macos --release
```

# Build for other platforms
```
flutter build ios --release
flutter build apk --release
flutter build web --release
````

## Platform-Specific Setup

### iOS
- Camera permissions are automatically requested
- Minimum iOS version: 12.0

### Android
- Camera permissions are automatically requested
- Minimum Android version: API 21 (Android 5.0)

### macOS
- Camera permissions need to be granted in System Preferences
- Enable camera access for the app

### Windows
- Camera permissions are handled by the system
- Webcam access is required

### Web
- Camera access requires HTTPS in production
- Uses WebRTC for camera access

## Usage

1. **Launch the app** on your preferred platform
2. **Grant camera permissions** when prompted
3. **Position your hand** in front of the camera
4. **Make gestures** and watch the app respond with animations
5. **Use the play/stop button** to control camera streaming

## Development

### Adding New Gestures

1. Add the gesture type to `lib/models/gesture_type.dart`
2. Update the gesture classification logic in `lib/providers/gesture_provider.dart`
3. Add the gesture icon and name in `lib/widgets/gesture_response.dart`

### Customizing Animations

The app uses Flutter's animation system with Skia rendering. You can customize animations by:

1. Modifying animation controllers in `lib/widgets/gesture_response.dart`
2. Creating custom painters for complex animations
3. Using Lottie animations for more sophisticated effects

### Performance Optimization

- Camera resolution can be adjusted in `lib/providers/camera_provider.dart`
- Processing frequency can be controlled to balance accuracy vs performance
- Use `flutter run --profile` for performance testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

© 2025 CycleRunCode Club. All rights reserved.

This project is proprietary software developed by CycleRunCode Club. Unauthorized copying, distribution, or use is strictly prohibited.

For licensing inquiries, please contact us at https://cycleruncode.club

## Acknowledgments

- Google MediaPipe for hand tracking technology
- Flutter team for the amazing framework
- TensorFlow team for ML capabilities

## Future Enhancements

- [ ] Sign language recognition
- [ ] Custom gesture training
- [ ] Voice feedback
- [ ] Gesture recording and playback
- [ ] Multi-hand support
- [ ] Advanced animation effects
- [ ] Cloud-based gesture recognition
- [ ] Accessibility features
