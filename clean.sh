#!/bin/bash

# Define folders to clean
FOLDER_PATHS=(
    "./static/output_images"
    "./output" 
    "./static/output3"
)
MAX_SIZE_MB=200  # 200MB total
SLEEP_TIME=3600  # 1 hour in seconds
MIN_AGE_MINUTES=119  # ~2 hours

# Create directories if they don't exist
for folder in "${FOLDER_PATHS[@]}"; do
    mkdir -p "$folder"
    touch "$folder/.gitkeep"  # Ensure .gitkeep exists
done

# Calculate total size
total_size=0
size_errors=0

for folder in "${FOLDER_PATHS[@]}"; do
    if [ -d "$folder" ]; then
        # Get folder size in MB, default to 0 if error
        folder_size=$(du -sm "$folder" 2>/dev/null | awk '{print $1}' || echo 0)
        total_size=$((total_size + folder_size))
    else
        echo "Warning: Directory $folder not found" >&2
        size_errors=$((size_errors + 1))
    fi
done

# Clean old files (except .gitkeep)
for folder in "${FOLDER_PATHS[@]}"; do
    if [ -d "$folder" ]; then
        find "$folder" -type f -not -name '.gitkeep' -mmin "+$MIN_AGE_MINUTES" -delete 2>/dev/null
        find "$folder" -type d -empty -not -name '.' -delete 2>/dev/null
    fi
done

# Force cleanup if over size limit (only if we got valid size measurements)
if [ $size_errors -eq 0 ] && [ $total_size -gt $MAX_SIZE_MB ]; then
    echo "Total size ${total_size}MB exceeds limit ${MAX_SIZE_MB}MB - forcing cleanup"
    for folder in "${FOLDER_PATHS[@]}"; do
        if [ -d "$folder" ]; then
            find "$folder" -mindepth 1 -not -name '.gitkeep' -exec rm -rf {} + 2>/dev/null
        fi
    done
fi