#!/bin/bash

# Ensure the script exits on errors
set -e

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is not installed. Please install it and try again."
    exit 1
fi

# Parse command-line arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_image> <output_directory> <number_of_frames>"
    exit 1
fi

INPUT_IMAGE="$1"
OUTPUT_DIR="$2"
FRAMES="$3"
BASENAME=$(basename "$INPUT_IMAGE" | cut -d. -f1)

# Validate input image
if [ ! -f "$INPUT_IMAGE" ]; then
    echo "Input image file ($INPUT_IMAGE) not found. Please provide a valid file."
    exit 1
fi

# Validate number of frames
if ! [[ "$FRAMES" =~ ^[0-9]+$ ]] || [ "$FRAMES" -le 0 ]; then
    echo "Invalid number of frames. Please enter a positive integer."
    exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Calculate the angle step
ANGLE_STEP=$((360 / FRAMES))

echo "Generating $FRAMES frames in $OUTPUT_DIR..."

# Generate frames
for i in $(seq 0 $((FRAMES-1))); do
    ANGLE=$((i * ANGLE_STEP))
    FRAME_FILE=$(printf "$OUTPUT_DIR/%02d_${BASENAME}.png" $i)
    convert "$INPUT_IMAGE" -background none -distort SRT $ANGLE "$FRAME_FILE"
    echo "Frame $i: Rotated $ANGLE degrees"
done

echo "Frames generated in $OUTPUT_DIR."
