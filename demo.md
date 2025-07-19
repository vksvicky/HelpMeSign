# Help Me Sign - Demo Guide

## Quick Start

### 1. Run the App

```bash
# For mobile (iOS/Android)
flutter run

# For web
flutter run -d chrome

# For desktop
flutter run -d macos  # macOS
flutter run -d windows # Windows
```

### 2. Grant Camera Permissions

When the app launches, it will request camera permissions:
- **Mobile**: Tap "Allow" when prompted
- **Desktop**: Grant camera access in system settings
- **Web**: Click "Allow" in the browser prompt

### 3. Start Camera Streaming

Tap the play button (▶️) in the app bar to start the camera feed.

### 4. Make Hand Gestures

Position your hand in front of the camera and try these gestures:

- **Open Hand**: Show your palm to the camera
- **Waving**: Wave your hand side to side
- **Pointing**: Point with your index finger
- **Thumbs Up**: Give a thumbs up gesture

### 5. Watch the Response

The app will:
- Display hand landmarks on the camera feed (green dots)
- Show animated gesture responses in the bottom panel
- Display the detected gesture name

## Features Demonstrated

### Real-time Camera Processing
- Live camera feed with gesture detection
- Smooth 60fps processing
- Cross-platform camera access

### Hand Gesture Recognition
- Real-time hand landmark detection
- Multiple gesture types supported
- Confidence scoring for accuracy

### Smooth Animations
- Skia-based rendering for fluid animations
- Elastic animations with rotation effects
- Responsive gesture feedback

### Modern UI
- Material Design 3 components
- Dark/light theme support
- Responsive layout for all screen sizes

## Troubleshooting

### Camera Not Working
1. Check camera permissions in device settings
2. Ensure no other app is using the camera
3. Try restarting the app

### Gestures Not Detected
1. Ensure good lighting conditions
2. Keep your hand clearly visible to the camera
3. Try different hand positions

### Performance Issues
1. Close other apps to free up resources
2. Reduce camera resolution if needed
3. Use a device with good processing power

## Next Steps

This demo shows the basic functionality. For production use, you would:

1. **Integrate MediaPipe**: Replace the mock gesture detection with real MediaPipe hand tracking
2. **Add More Gestures**: Implement additional sign language gestures
3. **Improve Accuracy**: Use trained ML models for better gesture recognition
4. **Add Voice Feedback**: Include audio responses for accessibility
5. **Cloud Integration**: Add cloud-based gesture recognition for better accuracy

## Development Notes

- The current implementation uses mock gesture detection for demonstration
- Real MediaPipe integration would require additional setup and model files
- The app structure is designed to easily swap in real ML models
- All animations use Flutter's built-in animation system with Skia rendering 