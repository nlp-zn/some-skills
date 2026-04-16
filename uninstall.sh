#!/bin/bash
# Uninstall script for skills in this repository
# Usage: ./uninstall.sh <skill-name>

set -e

SKILL_NAME="$1"
CLAUSE_SKILLS_DIR="$HOME/.claude/skills"

if [ -z "$SKILL_NAME" ]; then
    echo "Usage: $0 <skill-name>"
    exit 1
fi

if [ ! -L "$CLAUSE_SKILLS_DIR/$SKILL_NAME" ]; then
    echo "Error: '$SKILL_NAME' is not installed"
    exit 1
fi

rm "$CLAUSE_SKILLS_DIR/$SKILL_NAME"

echo "✅ Uninstalled '$SKILL_NAME'"
