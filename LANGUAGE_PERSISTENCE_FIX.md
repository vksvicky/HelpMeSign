# Language Persistence Fix

## Problem
When starting sign language recognition, the language would reset back to BSL (the default) even if the user had previously selected ASL or another language. This happened because:

1. **Language changes weren't properly synced** between the UI and AI system
2. **UserDefaults was being cleared** on app startup, resetting preferences
3. **AI system wasn't being updated** when language changed in preferences
4. **Multiple language change methods** weren't coordinated

## Solution

### 1. **Fixed MainWindowController.changeLanguage()**
**File:** `HelpMeSign/Controllers/MainWindowController.swift`

**Before:**
```swift
func changeLanguage(to language: String?) {
    guard let language = language else {
        return
    }
    
    // Only update UI if views are loaded and on main thread
    DispatchQueue.main.async { [weak self] in
        guard let self = self, self.isViewLoaded else { return }
        // Update the language display
        self.cameraSectionView?.updateLanguageDisplay(language, flag: "🇺🇸")
        
        // Reload alphabet for the new language
        self.alphabetSectionView?.reloadAlphabetForLanguage(language)
    }
    
    // In a real implementation, you would also update the AI system
    // and language engine with the new language
}
```

**After:**
```swift
func changeLanguage(to language: String?) {
    guard let language = language else {
        return
    }
    
    // Update UserDefaults immediately
    UserDefaults.standard.set(language, forKey: "SelectedLanguage")
    
    // Update AI system language
    aiSystem?.changeLanguage(to: language)
    
    // Only update UI if views are loaded and on main thread
    DispatchQueue.main.async { [weak self] in
        guard let self = self, self.isViewLoaded else { return }
        // Update the language display
        self.cameraSectionView?.updateLanguageDisplay(language, flag: "🇺🇸")
        
        // Reload alphabet for the new language
        self.alphabetSectionView?.reloadAlphabetForLanguage(language)
    }
}
```

### 2. **Fixed AppDelegate Language Reset**
**File:** `HelpMeSign/Controllers/AppDelegate.swift`

**Before:**
```swift
private func setDefaultLanguageIfNeeded() {
    // TEMPORARY: Clear existing preference to force locale detection
    UserDefaults.standard.removeObject(forKey: "SelectedLanguage")
    
    // Only set default if no language preference is saved
    if UserDefaults.standard.string(forKey: "SelectedLanguage") == nil {
        // ... rest of method
    }
}
```

**After:**
```swift
private func setDefaultLanguageIfNeeded() {
    // Only set default if no language preference is saved
    if UserDefaults.standard.string(forKey: "SelectedLanguage") == nil {
        // ... rest of method
    }
}
```

### 3. **Fixed PreferencesViewController Language Selection**
**File:** `HelpMeSign/Views/PreferencesViewController.swift`

**Before:**
```swift
private func selectLanguage(_ languageCode: String) {
    // Only update if language actually changed
    if selectedLanguage != languageCode {
        selectedLanguage = languageCode
        
        // Update button appearance
        languageTableView.reloadData()
        
        // Save to UserDefaults
        UserDefaults.standard.set(languageCode, forKey: "SelectedLanguage")
        
        // Post notification
        NotificationCenter.default.post(
            name: NSNotification.Name("LanguageChanged"),
            object: nil,
            userInfo: ["languageCode": languageCode]
        )
        
        // Also update the main window's main window controller directly
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            if let mainWindow = NSApplication.shared.mainWindow,
               let mainWindowController = mainWindow.contentViewController as? MainWindowController {
                mainWindowController.changeLanguage(to: languageCode)
            }
        }
    }
}
```

**After:**
```swift
private func selectLanguage(_ languageCode: String) {
    // Only update if language actually changed
    if selectedLanguage != languageCode {
        selectedLanguage = languageCode
        
        // Update button appearance
        languageTableView.reloadData()
        
        // Save to UserDefaults
        UserDefaults.standard.set(languageCode, forKey: "SelectedLanguage")
        
        // Post notification
        NotificationCenter.default.post(
            name: NSNotification.Name("LanguageChanged"),
            object: nil,
            userInfo: ["languageCode": languageCode]
        )
        
        // Also update the main window's main window controller directly
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            if let mainWindow = NSApplication.shared.mainWindow,
               let mainWindowController = mainWindow.contentViewController as? MainWindowController {
                mainWindowController.changeLanguage(to: languageCode)
            }
        }
        
        // Update AI system directly
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            AIUserExperienceSystem.shared.changeLanguage(to: languageCode)
        }
    }
}
```

### 4. **Fixed SimplePreferencesViewController Language Change**
**File:** `HelpMeSign/Views/SimplePreferencesViewController.swift`

**Before:**
```swift
@objc private func languageChanged() {
    let selectedLanguage = languagePopUp.selectedItem?.title ?? "ASL"
    UserDefaults.standard.set(selectedLanguage, forKey: "SelectedLanguage")
    
    // Update main window after a delay
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
        if let mainWindow = NSApplication.shared.windows.first(where: { $0.title == "HelpMeSign" }),
           let mainWindowController = mainWindow.contentViewController as? MainWindowController {
            mainWindowController.changeLanguage(to: selectedLanguage)
        }
    }
}
```

**After:**
```swift
@objc private func languageChanged() {
    let selectedLanguage = languagePopUp.selectedItem?.title ?? "ASL"
    UserDefaults.standard.set(selectedLanguage, forKey: "SelectedLanguage")
    
    // Update AI system
    AIUserExperienceSystem.shared.changeLanguage(to: selectedLanguage)
    
    // Update main window after a delay
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
        if let mainWindow = NSApplication.shared.windows.first(where: { $0.title == "HelpMeSign" }),
           let mainWindowController = mainWindow.contentViewController as? MainWindowController {
            mainWindowController.changeLanguage(to: selectedLanguage)
        }
    }
}
```

## Key Changes Summary

1. **Always Update UserDefaults**: Every language change now immediately updates UserDefaults
2. **Always Update AI System**: Every language change now calls `AIUserExperienceSystem.shared.changeLanguage(to:)`
3. **Removed UserDefaults Clearing**: App no longer clears language preferences on startup
4. **Coordinated Updates**: All UI components and the AI system are updated together

## Testing the Fix

1. **Change language in preferences** → Should persist across app restarts
2. **Start recognition** → Should use the selected language, not reset to default
3. **Switch languages during recognition** → Should work seamlessly
4. **App restart** → Should remember the last selected language

## Files Modified

- `HelpMeSign/Controllers/MainWindowController.swift`
- `HelpMeSign/Controllers/AppDelegate.swift`
- `HelpMeSign/Views/PreferencesViewController.swift`
- `HelpMeSign/Views/SimplePreferencesViewController.swift`

## Notes

- The AI system's `changeLanguage(to:)` method already properly updates UserDefaults
- The `currentLanguage` computed property in `AIUserExperienceSystem` already reads from UserDefaults
- This fix ensures all components stay in sync and preferences persist correctly 