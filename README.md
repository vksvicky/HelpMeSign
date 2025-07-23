# HelpMeSign

A macOS application for sign language learning and recognition.

## Project Structure

The project has been organized into a clean, modular structure for better maintainability and scalability.

### Main Application (`HelpMeSign/`)

```
HelpMeSign/
├── Controllers/          # View Controllers and App Delegate
│   ├── AppDelegate.swift
│   └── CameraViewController.swift
├── Views/               # UI Components and Custom Views
│   ├── AlphabetLetterView.swift
│   └── PreferencesViewController.swift
├── Models/              # Business Logic and Data Models
│   ├── AIUserExperienceSystem.swift
│   └── LanguageEngine.swift
├── Utils/               # Utilities, Helpers, and Metal Shaders
│   ├── AppDelegateNotificationNames.swift
│   ├── SimpleMTKViewDelegate.swift
│   └── Shaders.metal
├── Resources/           # Assets, Configurations, and Resources
│   ├── Assets.xcassets/
│   └── LanguageConfigs/
├── Base.lproj/          # Localization and Storyboards
├── Info.plist           # Application Configuration
└── HelpMeSign.entitlements
```

### Tests (`Tests/`)

```
Tests/
├── Views/               # Tests for UI Components
│   ├── AlphabetLetterViewTests.swift
│   ├── AlphabetBarViewTests.swift
│   └── PreferencesViewControllerTests.swift
├── Controllers/         # Tests for View Controllers
│   ├── AppDelegateTests.swift
│   └── CameraViewControllerTests.swift
├── Utils/               # Tests for Utilities
│   ├── AppDelegateNotificationNamesTests.swift
│   └── SimpleMTKViewDelegateTests.swift
├── Models/              # Tests for Business Logic (empty for now)
└── HelpMeSignTests.swift
```

### UI Tests (`HelpMeSignUITests/`)

```
HelpMeSignUITests/
├── HelpMeSignUITests.swift
└── HelpMeSignUITestsLaunchTests.swift
```

## Architecture Overview

### Controllers
- **AppDelegate.swift**: Application lifecycle management
- **CameraViewController.swift**: Camera interface and video processing

### Views
- **AlphabetLetterView.swift**: Custom view for displaying sign language alphabet
- **PreferencesViewController.swift**: User preferences and settings interface

### Models
- **AIUserExperienceSystem.swift**: AI/ML integration for user experience
- **LanguageEngine.swift**: Sign language processing and recognition logic

### Utils
- **AppDelegateNotificationNames.swift**: Notification name constants
- **SimpleMTKViewDelegate.swift**: Metal framework integration
- **Shaders.metal**: Metal shader code for graphics processing

### Resources
- **Assets.xcassets**: Images, icons, and visual assets
- **LanguageConfigs**: Configuration files for different sign languages (ASL, BSL, JSL)

## Development Guidelines

1. **File Organization**: Always place new files in the appropriate folder based on their purpose
2. **Naming Conventions**: Use descriptive names that clearly indicate the file's purpose
3. **Testing**: Create corresponding test files in the matching test folder structure
4. **Dependencies**: Keep dependencies minimal and well-documented

## Building and Running

1. Open `HelpMeSign.xcodeproj` in Xcode
2. Select the appropriate target (HelpMeSign, HelpMeSignTests, or HelpMeSignUITests)
3. Build and run the project

## Testing

- **Unit Tests**: Located in `Tests/` folder, organized by component type
- **UI Tests**: Located in `HelpMeSignUITests/` folder
- Run tests using Cmd+U in Xcode or the Test navigator 