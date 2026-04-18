#!/bin/bash

# Steam Stats Skill Installer (Bash)
# This script installs the steam-stats skill for Gemini CLI, Claude, and GitHub Copilot.

SKILL_NAME="steam-stats"
SKILL_PATH="./steam-stats"

echo "🚀 Installing $SKILL_NAME skill..."

# Check if the skill directory exists
if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ Error: $SKILL_PATH directory not found."
    exit 1
fi

# 1. Gemini CLI Installation
if command -v gemini &> /dev/null; then
    echo "📦 Installing for Gemini CLI..."
    # If the .skill file exists, use it, otherwise use the directory
    if [ -f "$SKILL_NAME.skill" ]; then
        gemini skills install "$SKILL_NAME.skill" --scope workspace
    else
        gemini skills install "$SKILL_PATH" --scope workspace
    fi
else
    echo "⚠️ Gemini CLI not found. Skipping."
fi

# 2. Claude Code Installation
CLAUDE_SKILLS_DIR="./.claude/skills"
mkdir -p "$CLAUDE_SKILLS_DIR"
cp -r "$SKILL_PATH" "$CLAUDE_SKILLS_DIR/"
echo "📦 Installed for Claude Code (Workspace)."

# 3. GitHub Copilot Installation
GITHUB_SKILLS_DIR="./.github/skills"
mkdir -p "$GITHUB_SKILLS_DIR"
cp -r "$SKILL_PATH" "$GITHUB_SKILLS_DIR/"
echo "📦 Installed for GitHub Copilot (Workspace)."

echo "✅ Installation complete!"
echo "💡 Remember to reload your agents to see the new skill."
echo "   - Gemini: /skills reload"
echo "   - Claude/Copilot: Restart your session or project."
