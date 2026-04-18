#!/bin/bash

# Steam Stats Skill Installer (Bash)
# This script installs the steam-stats skill for Gemini CLI, Claude, and GitHub Copilot.

SKILL_NAME="steam-stats"
SKILL_PATH="./steam-stats"

echo "🚀 Steam Stats Skill Installer"

# Check if the skill directory exists
if [ ! -d "$SKILL_PATH" ]; then
    echo "❌ Error: $SKILL_PATH directory not found."
    exit 1
fi

# 1. Select Agents
echo ""
echo "Which agents would you like to install for?"
read -p "Install for Gemini CLI? (y/n): " INSTALL_GEMINI
read -p "Install for Claude Code? (y/n): " INSTALL_CLAUDE
read -p "Install for GitHub Copilot? (y/n): " INSTALL_COPILOT

# 2. Select Scope
echo ""
echo "Select installation scope:"
echo "1) Workspace (Local to this folder)"
echo "2) User (Global for all projects)"
read -p "Choice (1 or 2): " SCOPE_CHOICE

if [ "$SCOPE_CHOICE" == "2" ]; then
    SCOPE="user"
    GEMINI_SCOPE="user"
    CLAUDE_BASE="$HOME/.claude/skills"
    COPILOT_BASE="$HOME/.copilot/skills"
    echo "📍 Installing in User (Global) scope..."
else
    SCOPE="workspace"
    GEMINI_SCOPE="workspace"
    CLAUDE_BASE="./.claude/skills"
    COPILOT_BASE="./.github/skills"
    echo "📍 Installing in Workspace (Local) scope..."
fi

# --- Execution ---

# 1. Gemini CLI
if [[ "$INSTALL_GEMINI" =~ ^[Yy]$ ]]; then
    if command -v gemini &> /dev/null; then
        echo "📦 Installing for Gemini CLI..."
        if [ -f "$SKILL_NAME.skill" ]; then
            gemini skills install "$SKILL_NAME.skill" --scope "$GEMINI_SCOPE"
        else
            gemini skills install "$SKILL_PATH" --scope "$GEMINI_SCOPE"
        fi
    else
        echo "⚠️ Gemini CLI not found. Skipping."
    fi
fi

# 2. Claude Code
if [[ "$INSTALL_CLAUDE" =~ ^[Yy]$ ]]; then
    mkdir -p "$CLAUDE_BASE"
    cp -r "$SKILL_PATH" "$CLAUDE_BASE/"
    echo "📦 Installed for Claude Code."
fi

# 3. GitHub Copilot
if [[ "$INSTALL_COPILOT" =~ ^[Yy]$ ]]; then
    mkdir -p "$COPILOT_BASE"
    cp -r "$SKILL_PATH" "$COPILOT_BASE/"
    echo "📦 Installed for GitHub Copilot."
fi

echo ""
echo "✅ Installation process complete!"
echo "💡 Remember to reload your agents to see the new skill."
echo "   - Gemini: /skills reload"
echo "   - Claude/Copilot: Restart your session or project."
