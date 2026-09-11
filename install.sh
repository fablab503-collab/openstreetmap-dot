#!/bin/sh
# Copy the skills in this repo into Claude Code's skills folder.
# Safe to re-run: it overwrites files with the same name and deletes nothing.
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"

mkdir -p "$DEST"
for skill in "$REPO_DIR"/skills/*/; do
  name="$(basename "$skill")"
  mkdir -p "$DEST/$name"
  cp -R "$skill". "$DEST/$name/"
  echo "installed $name -> $DEST/$name"
done
