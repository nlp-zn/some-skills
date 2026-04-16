#!/bin/bash
# Install script for skills in this repository
# Usage: ./install.sh <skill-name>

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"

list_skills() {
    find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d \
        -exec test -f "{}/SKILL.md" \; \
        -exec basename "{}" \; \
        | sort
}

if [ -z "$1" ]; then
    echo "Usage: $0 <skill-name>"
    echo ""
    echo "Available skills:"
    list_skills
    exit 1
fi

SKILL_NAME="$1"
SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: Skill '$SKILL_NAME' not found"
    echo "Available skills:"
    list_skills
    exit 1
fi

# Check if SKILL.md exists
if [ ! -f "$SKILL_PATH/SKILL.md" ]; then
    echo "Error: '$SKILL_NAME' is not an installable skill (SKILL.md missing)"
    echo "Available skills:"
    list_skills
    exit 1
fi

# Create symlink
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
mkdir -p "$CLAUDE_SKILLS_DIR"

ln -sf "$SKILL_PATH" "$CLAUDE_SKILLS_DIR/$SKILL_NAME"

echo "✅ Installed '$SKILL_NAME' to ~/.claude/skills/"
echo ""
echo "You can now use this skill in Claude Code"
