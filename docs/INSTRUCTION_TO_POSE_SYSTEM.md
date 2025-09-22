# Universal Instruction-to-Pose Generation System

## Table of Contents

1. [Overview](#overview)
2. [Key Benefits](#key-benefits)
3. [How It Works](#how-it-works)
4. [Usage Examples](#usage-examples)
5. [🌍 Adding New Languages](#adding-new-languages) ⭐ **Most Important**
6. [Configuration Structure](#configuration-structure)
7. [Universal Concepts Reference](#universal-concepts-reference)
8. [Integration with GLB Viewer](#integration-with-glb-viewer)
9. [Testing and Validation](#testing-and-validation)

## Overview

> **🚀 Quick Start**: Want to add a new sign language? Jump to [Adding New Languages](#adding-new-languages) - it takes less than 5 minutes!

The Universal Instruction-to-Pose Generation System allows automatic conversion of natural language instructions into 3D character poses. This system is designed to be **language-agnostic** and **easily extensible** for new sign languages.

## Key Benefits

✅ **Universal Design**: Works across different sign languages with minimal changes  
✅ **Keyword-Based**: Uses flexible keyword matching instead of rigid patterns  
✅ **Configurable**: Language-specific configurations via JSON files  
✅ **Scalable**: Easy to add new languages and expand vocabulary  
✅ **No Manual Pose Data**: Eliminates need to manually create pose data for each character  

## How It Works

### 1. Instruction Parsing
The system analyzes natural language instructions and extracts:
- **Actions**: raise, hold, point, curve, curl, etc.
- **Body Parts**: arm, hand, fingers, thumb, index, etc.
- **Hand Shapes**: fist, flat, curved, point, etc.
- **Modifiers**: together, apart, bent, straight, etc.

### 2. Universal Mapping
Extracted keywords are mapped to universal concepts:
```
"raise your arm" → UniversalAction.RAISE + BodyPart.ARM
"make a fist" → UniversalAction.MAKE + UniversalHandShape.FIST
"point index finger" → UniversalAction.POINT + BodyPart.INDEX
```

### 3. Pose Generation
Universal concepts are converted to 3D joint rotations:
```python
# Fist shape applied to all fingers
'fist': {
    'index': [0, 90, 0],  # 90° curl
    'middle': [0, 90, 0],
    'ring': [0, 90, 0],
    'pinky': [0, 90, 0],
    'thumb': [-45, 30, 10]  # Wrap around
}
```

## Usage Examples

### Basic Usage
```python
from instruction_to_pose_generator import UniversalInstructionToPoseGenerator

# Initialize with universal config
generator = UniversalInstructionToPoseGenerator()

# Generate pose from instruction
instruction = "Raise your right arm and make a fist"
pose_data = generator.generate_universal_pose(instruction, hand='right')

# Result: Dictionary of joint_name -> [H, P, R] rotations
print(pose_data)
# {
#   'mixamorig:RightArm': [0, 45, -30],
#   'mixamorig:RightHandIndex1': [0, 90, 0],
#   'mixamorig:RightHandIndex2': [0, 90, 0],
#   ...
# }
```

### Language-Specific Usage
```python
# Load ASL-specific configuration
asl_config_path = "resources/data/pose_generation/asl_config.json"
asl_generator = UniversalInstructionToPoseGenerator(asl_config_path)

# Generate pose using ASL keywords
pose = asl_generator.generate_universal_pose("Point your index finger up")
```

## 🌍 Adding New Languages

### Step 1: Create Language Configuration
```python
from instruction_to_pose_generator import create_language_config_file

# Create template for new language
create_language_config_file(
    language_code="JSL",  # Japanese Sign Language
    language_name="Japanese Sign Language", 
    output_path="resources/data/pose_generation/jsl_config.json"
)
```

### Step 2: Customize Keywords
Edit the generated JSON file to match your language:

```json
{
  "language": "JSL",
  "language_name": "Japanese Sign Language",
  "keywords": {
    "actions": {
      "raise": ["上げる", "持ち上げる", "raise"],
      "hold": ["保持", "持つ", "hold"],
      "point": ["指す", "point"]
    },
    "body_parts": {
      "hand": ["手", "hand"],
      "fingers": ["指", "fingers"],
      "thumb": ["親指", "thumb"]
    }
  }
}
```

### Step 3: Use New Language
```python
jsl_generator = UniversalInstructionToPoseGenerator("path/to/jsl_config.json")
pose = jsl_generator.generate_universal_pose("手を上げる")  # "Raise hand" in Japanese
```

## Configuration Structure

### Language Configuration File
```json
{
  "language": "LANGUAGE_CODE",
  "language_name": "Full Language Name",
  "keywords": {
    "actions": {
      "universal_action": ["synonym1", "synonym2", "synonym3"]
    },
    "body_parts": {
      "universal_part": ["synonym1", "synonym2"]
    },
    "hand_shapes": {
      "universal_shape": ["synonym1", "synonym2"]
    },
    "modifiers": {
      "universal_modifier": ["synonym1", "synonym2"]
    }
  },
  "overrides": {
    "comment": "Language-specific adjustments if needed"
  }
}
```

## Universal Concepts Reference

### Universal Actions
- **raise**: Lift body part up
- **lower**: Move body part down  
- **hold**: Maintain position
- **point**: Extend/direct toward something
- **curve**: Create curved shape
- **curl**: Close/fold inward
- **touch**: Make contact
- **make**: Form a shape
- **move**: Change position
- **bend**: Create angle
- **extend**: Stretch out

### Universal Body Parts
- **arm**: Upper arm
- **forearm**: Lower arm  
- **elbow**: Elbow joint
- **hand**: Hand/wrist
- **fingers**: All fingers
- **thumb**: Thumb
- **index**: Index finger
- **middle**: Middle finger
- **ring**: Ring finger
- **pinky**: Pinky finger

### Universal Hand Shapes
- **fist**: Closed hand
- **flat**: Open palm
- **curved**: C-shaped hand
- **point**: Single finger extended

## Integration with GLB Viewer

The system integrates seamlessly with the GLB viewer:

```python
# In GLB viewer
from instruction_to_pose_generator import UniversalInstructionToPoseGenerator

class GLBViewerWindow:
    def __init__(self):
        self.pose_generator = UniversalInstructionToPoseGenerator()
    
    def apply_instruction_pose(self, instruction: str, hand: str = 'right'):
        """Generate and apply pose from instruction"""
        pose_data = self.pose_generator.generate_universal_pose(instruction, hand)
        
        # Apply to 3D character
        for joint_name, hpr_values in pose_data.items():
            joint = self.character.controlJoint(None, "modelRoot", joint_name)
            if joint and not joint.isEmpty():
                joint.setHpr(hpr_values[0], hpr_values[1], hpr_values[2])
        
        self.character.update()
```

## Benefits for Multi-Language Support

1. **Minimal Code Changes**: Add new languages without touching core logic
2. **Consistent Poses**: Same pose quality across all languages
3. **Easy Maintenance**: Update pose logic once, affects all languages
4. **Cultural Adaptation**: Language configs can include cultural notes
5. **Rapid Expansion**: New languages can be added in minutes

## Testing and Validation

```python
# Test coverage for your language
coverage = generator.analyze_universal_coverage(your_instructions)
print(f"Parseable: {coverage['parseable']}/{coverage['total']}")
print(f"Patterns: {coverage['detected_patterns']}")
```

This system transforms sign language pose generation from a manual, language-specific process into an automated, universal solution that scales effortlessly across languages! 🌍✨
