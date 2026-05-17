#!/usr/bin/env bash
# Render a single PNG frame and open it immediately.
# Usage: ./preview.sh [SceneClass] [SceneFile]
#   SceneClass defaults to AlienMovesPreview
#   SceneFile  defaults to src/scenes/s09_alien_moves.py

SCENE=${1:-AlienMovesPreview}
FILE=${2:-src/scenes/s09_alien_moves.py}

manim -s -ql "$FILE" "$SCENE" && \
  open media/images/"$(basename "$FILE" .py)"/"${SCENE}"_ManimCE_*.png
