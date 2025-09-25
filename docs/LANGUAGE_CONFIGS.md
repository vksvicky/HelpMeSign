## Language Config Design

This project separates shared pose vocabulary from language‑specific data to avoid duplication and keep maintenance simple.

### Files and Responsibilities

- `resources/data/pose_generation/universal_config.json`
  - Canonical keywords and rules used by the instruction→pose engine.
  - Contains: actions, body_parts, hand_shapes, modifiers, orientations, and their synonyms.
  - Single source of truth. No per‑sign entries here.

- `resources/data/pose_generation/<lang>_config.json` (optional)
  - Language‑specific overrides/additions only.
  - Examples: extra synonyms, cultural notes, defaults (e.g., hand dominance), or language‑tuned thresholds.
  - Must NOT duplicate universal keywords. If no overrides are needed, the file can be empty/absent.

- `resources/data/signs/<lang>/*.json`
  - Per‑sign dictionaries (letters/numbers/words) with: instruction text, svg, description, metadata.
  - No pose values or engine keywords; the engine derives poses from the instructions using the configs above.

### Inheritance / Merge

1) Load `universal_config.json` as the base.
2) If a `<lang>_config.json` exists, merge it on top (language takes precedence).

This allows new universal keywords to benefit all languages automatically while keeping language‑specific tweaks minimal.

### What goes where?

- Put orientation names like "palm_forward" in `universal_config.json`.
- Put ASL‑specific synonyms or notes (e.g., right‑hand dominance) in `asl_config.json`.
- Put the instruction for sign "B" (and its svg) in `resources/data/signs/asl/...`.

### Rationale

- Prevent data duplication and drift.
- Make it easy to add new languages: start with universal config, add minimal overrides, then provide sign dictionaries (instructions + svgs).


