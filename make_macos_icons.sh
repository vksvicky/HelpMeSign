#!/bin/bash

# Usage: ./make_macos_icons_im7.sh icon.png /path/to/AppIcon.appiconset

SRC_ICON="$1"
DEST_DIR="$2"

if [[ -z "$SRC_ICON" || -z "$DEST_DIR" ]]; then
  echo "Usage: $0 icon.png /path/to/AppIcon.appiconset"
  exit 1
fi

mkdir -p "$DEST_DIR"

# Array of sizes and filenames for macOS AppIcon
sizes=(
  "16 AppIcon-16x16@1x.png"
  "32 AppIcon-16x16@2x.png"
  "32 AppIcon-32x32@1x.png"
  "64 AppIcon-32x32@2x.png"
  "128 AppIcon-128x128@1x.png"
  "256 AppIcon-128x128@2x.png"
  "256 AppIcon-256x256@1x.png"
  "512 AppIcon-256x256@2x.png"
  "512 AppIcon-512x512@1x.png"
  "1024 AppIcon-512x512@2x.png"
)

# Array of JSON entries for Contents.json
declare -a json_entries
json_entries+=(
  '{ "idiom": "mac", "size": "16x16", "scale": "1x", "filename": "AppIcon-16x16@1x.png" }'
  '{ "idiom": "mac", "size": "16x16", "scale": "2x", "filename": "AppIcon-16x16@2x.png" }'
  '{ "idiom": "mac", "size": "32x32", "scale": "1x", "filename": "AppIcon-32x32@1x.png" }'
  '{ "idiom": "mac", "size": "32x32", "scale": "2x", "filename": "AppIcon-32x32@2x.png" }'
  '{ "idiom": "mac", "size": "128x128", "scale": "1x", "filename": "AppIcon-128x128@1x.png" }'
  '{ "idiom": "mac", "size": "128x128", "scale": "2x", "filename": "AppIcon-128x128@2x.png" }'
  '{ "idiom": "mac", "size": "256x256", "scale": "1x", "filename": "AppIcon-256x256@1x.png" }'
  '{ "idiom": "mac", "size": "256x256", "scale": "2x", "filename": "AppIcon-256x256@2x.png" }'
  '{ "idiom": "mac", "size": "512x512", "scale": "1x", "filename": "AppIcon-512x512@1x.png" }'
  '{ "idiom": "mac", "size": "512x512", "scale": "2x", "filename": "AppIcon-512x512@2x.png" }'
)

for entry in "${sizes[@]}"; do
  set -- $entry
  SIZE=$1
  FILENAME=$2
  magick "$SRC_ICON" -resize ${SIZE}x${SIZE} "$DEST_DIR/$FILENAME"
  echo "Created $DEST_DIR/$FILENAME ($SIZE x $SIZE)"
done

# Generate Contents.json
cat > "$DEST_DIR/Contents.json" <<EOL
{
  "images" : [
    $(IFS=,; echo "${json_entries[*]}")
  ],
  "info" : { "version": 1, "author": "xcode" }
}
EOL

echo "All icons and Contents.json generated in $DEST_DIR"