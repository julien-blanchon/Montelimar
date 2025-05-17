#!/bin/bash

cargo_toml="./src-tauri/Cargo.toml"
major_minor="0.1"
today_patch=$(date +%Y%m%d)  # e.g., 20250517
base_version="${major_minor}.${today_patch}"

# Extract the current version
current_version=$(grep '^version = ' "$cargo_toml" | sed -E 's/version = "(.*)"/\1/')

# Check if today’s version is already set
if [[ "$current_version" == "$base_version"* ]]; then
  # If already set, increment suffix (e.g., 0.1.20250517.1)
  if [[ "$current_version" =~ ^$base_version\.([0-9]+)$ ]]; then
    suffix=${BASH_REMATCH[1]}
    new_version="$base_version.$((suffix + 1))"
  else
    new_version="$base_version.1"
  fi
else
  new_version="$base_version"
fi

# Replace version in Cargo.toml
sed -i.bak -E "s/^version = \".*\"/version = \"$new_version\"/" "$cargo_toml"
rm "$cargo_toml.bak"

git add "$cargo_toml"
echo "Set version to $new_version"
