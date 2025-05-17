#!/bin/bash

today=$(date +%Y.%m.%d)
cargo_toml="./src-tauri/Cargo.toml"

current_version=$(grep '^version = ' "$cargo_toml" | sed -E 's/version = "(.*)"/\1/')

if [[ "$current_version" == "$today"* ]]; then
  if [[ "$current_version" =~ ^$today\.([0-9]+)$ ]]; then
    suffix=${BASH_REMATCH[1]}
    new_version="$today.$((suffix + 1))"
  else
    new_version="$today.1"
  fi
else
  new_version="$today"
fi

sed -i.bak -E "s/^version = \".*\"/version = \"$new_version\"/" "$cargo_toml"
rm "$cargo_toml.bak"

git add "$cargo_toml"

echo "Set version to $new_version"
