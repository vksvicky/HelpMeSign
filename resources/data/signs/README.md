# Sign Language Data Files

This directory contains sign language data files organized by language and hand preference.

## Structure

```
signs/
├── asl/
│   ├── asl_right_hand.json      # Complete ASL alphabet A-Z + numbers 0-9 (right hand)
│   └── asl_left_hand.json       # Complete ASL alphabet A-Z + numbers 0-9 (left hand)
└── README.md
```

## File Format

Each JSON file contains:

### Header Information
- `language`: The sign language code (e.g., "ASL" for American Sign Language)
- `hand`: Which hand the signs are designed for ("right" or "left")
- `version`: File version
- `description`: Brief description of the content

### Alphabet Section
Contains all letters A-Z with:
- `svg`: SVG representation of the sign
- `description`: Text description of the sign
- `instructions`: Step-by-step instructions for performing the sign

### Numbers Section
Contains numbers 0-9 with the same structure as alphabet entries.

### Metadata
- `total_signs`: Total number of signs in the file
- `last_updated`: Last update date
- `hand_preference`: Which hand the signs are optimized for
- `difficulty`: Difficulty level (beginner, intermediate, advanced)

## Example Usage

```json
{
  "language": "ASL",
  "hand": "right",
  "version": "1.0.0",
  "description": "American Sign Language alphabet for right hand",
  "alphabet": {
    "A": {
      "svg": "<svg>...</svg>",
      "description": "ASL letter A - Fist with thumb on the side",
      "instructions": "Make a fist with your right hand, keeping your thumb to the side of your fingers"
    }
  },
  "numbers": {
    "0": {
      "svg": "<svg>...</svg>",
      "description": "ASL number 0 - Closed fist",
      "instructions": "Make a fist with your right hand"
    }
  },
  "metadata": {
    "total_signs": 36,
    "last_updated": "2024-01-15",
    "hand_preference": "right",
    "difficulty": "beginner"
  }
}
```

## Adding New Languages

To add support for a new sign language:

1. Create a new directory under `signs/` for the language code
2. Create separate files for right and left hand variants
3. Follow the established JSON structure
4. Include proper SVG representations for each sign
5. Provide clear descriptions and instructions
6. Update this README with the new language information

## SVG Guidelines

- Use consistent viewBox dimensions (200x200 recommended)
- Keep SVG code clean and optimized
- Use black stroke with appropriate stroke-width
- Ensure signs are clearly recognizable
- Consider accessibility for screen readers

## Hand Preference Considerations

- Right-handed signs are typically the default
- Left-handed variants may be mirror images
- Some signs may be identical for both hands
- Consider cultural and regional variations

## Future Enhancements

- Add support for compound signs
- Include facial expressions and body language
- Add video references for complex signs
- Support for regional variations
- Integration with machine learning models
