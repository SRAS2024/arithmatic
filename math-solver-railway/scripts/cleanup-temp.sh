#!/bin/bash
# Cleanup temporary files older than 1 hour
TEMP_DIR="${TEMP_DIR:-./server/temp}"
echo "[cleanup] Cleaning temp files in $TEMP_DIR..."
find "$TEMP_DIR" -type f -not -name '.gitkeep' -mmin +60 -delete 2>/dev/null || true
echo "[cleanup] Done."
