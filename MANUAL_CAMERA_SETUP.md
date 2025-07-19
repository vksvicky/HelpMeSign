# Manual Camera Permission Setup for macOS

Since Flutter's camera plugin doesn't support macOS and the app runs in a sandbox, you need to manually add the app to camera permissions.

## Method 1: Manual Addition (Recommended)

1. **Open System Settings > Privacy & Security > Camera**
2. **Click the "+" button** to add an application
3. **Navigate to**: `/Users/vivek/Development/HelpMeSign/build/macos/Build/Products/Debug/`
4. **Select `HelpMeSign.app`** and click "Open"
5. **Toggle the permission ON**

## Method 2: Using Terminal

```bash
# Open camera settings
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Camera"

# Open the app directory
open /Users/vivek/Development/HelpMeSign/build/macos/Build/Products/Debug/
```

Then drag `HelpMeSign.app` to the Camera permissions list.

## Method 3: Run Swift Script Manually

```bash
# Run the camera test script manually
/Users/vivek/Development/HelpMeSign/macos_camera_test.swift
```

This will trigger the camera permission request and register the app.

## Why This is Needed

- Flutter's camera plugin doesn't support macOS
- macOS apps run in sandbox with restricted permissions
- Manual addition is the standard approach for development apps
- The app needs to be registered before it can request camera access

## After Adding Permissions

Once added to the Camera permissions list:
- ✅ The app will appear in System Settings
- ✅ Camera access will work properly
- ✅ No more MissingPluginException errors 