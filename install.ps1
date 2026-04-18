# Steam Stats Skill Installer (PowerShell)
# This script installs the steam-stats skill for Gemini CLI, Claude, and GitHub Copilot.

$SKILL_NAME = "steam-stats"
$SKILL_PATH = ".\steam-stats"

Write-Host "🚀 Installing $SKILL_NAME skill..." -ForegroundColor Cyan

# Check if the skill directory exists
if (-not (Test-Path $SKILL_PATH)) {
    Write-Error "❌ Error: $SKILL_PATH directory not found."
    exit 1
}

# 1. Gemini CLI Installation
if (Get-Command "gemini" -ErrorAction SilentlyContinue) {
    Write-Host "📦 Installing for Gemini CLI..." -ForegroundColor Green
    # If the .skill file exists, use it, otherwise use the directory
    if (Test-Path "$SKILL_NAME.skill") {
        gemini skills install "$SKILL_NAME.skill" --scope workspace
    } else {
        gemini skills install "$SKILL_PATH" --scope workspace
    }
} else {
    Write-Host "⚠️ Gemini CLI not found. Skipping." -ForegroundColor Yellow
}

# 2. Claude Code Installation
$CLAUDE_SKILLS_DIR = ".\.claude\skills"
if (-not (Test-Path $CLAUDE_SKILLS_DIR)) { New-Item -ItemType Directory -Path $CLAUDE_SKILLS_DIR -Force }
Copy-Item -Path $SKILL_PATH -Destination "$CLAUDE_SKILLS_DIR" -Recurse -Force
Write-Host "📦 Installed for Claude Code (Workspace)." -ForegroundColor Green

# 3. GitHub Copilot Installation
$GITHUB_SKILLS_DIR = ".\.github\skills"
if (-not (Test-Path $GITHUB_SKILLS_DIR)) { New-Item -ItemType Directory -Path $GITHUB_SKILLS_DIR -Force }
Copy-Item -Path $SKILL_PATH -Destination "$GITHUB_SKILLS_DIR" -Recurse -Force
Write-Host "📦 Installed for GitHub Copilot (Workspace)." -ForegroundColor Green

Write-Host "✅ Installation complete!" -ForegroundColor Cyan
Write-Host "💡 Remember to reload your agents to see the new skill."
Write-Host "   - Gemini: /skills reload"
Write-Host "   - Claude/Copilot: Restart your session or project."
