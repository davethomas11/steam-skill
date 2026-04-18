# Steam Stats Skill Installer (PowerShell)
# This script installs the steam-stats skill for Gemini CLI, Claude, and GitHub Copilot.

$SKILL_NAME = "steam-stats"
$SKILL_PATH = ".\steam-stats"

Write-Host "🚀 Steam Stats Skill Installer" -ForegroundColor Cyan

# Check if the skill directory exists
if (-not (Test-Path $SKILL_PATH)) {
    Write-Error "❌ Error: $SKILL_PATH directory not found."
    exit 1
}

# 1. Select Agents
Write-Host "`nWhich agents would you like to install for?"
$installGemini = Read-Host "Install for Gemini CLI? (y/n)"
$installClaude = Read-Host "Install for Claude Code? (y/n)"
$installCopilot = Read-Host "Install for GitHub Copilot? (y/n)"

# 2. Select Scope
Write-Host "`nSelect installation scope:"
Write-Host "1) Workspace (Local to this folder)"
Write-Host "2) User (Global for all projects)"
$scopeChoice = Read-Host "Choice (1 or 2)"

if ($scopeChoice -eq "2") {
    $geminiScope = "user"
    $claudeBase = Join-Path $HOME ".claude\skills"
    $copilotBase = Join-Path $HOME ".copilot\skills"
    Write-Host "📍 Installing in User (Global) scope..." -ForegroundColor Yellow
} else {
    $geminiScope = "workspace"
    $claudeBase = ".\.claude\skills"
    $copilotBase = ".\.github\skills"
    Write-Host "📍 Installing in Workspace (Local) scope..." -ForegroundColor Yellow
}

# --- Execution ---

# 1. Gemini CLI
if ($installGemini -match "y") {
    if (Get-Command "gemini" -ErrorAction SilentlyContinue) {
        Write-Host "📦 Installing for Gemini CLI..." -ForegroundColor Green
        if (Test-Path "$SKILL_NAME.skill") {
            gemini skills install "$SKILL_NAME.skill" --scope $geminiScope
        } else {
            gemini skills install "$SKILL_PATH" --scope $geminiScope
        }
    } else {
        Write-Host "⚠️ Gemini CLI not found. Skipping." -ForegroundColor DarkYellow
    }
}

# 2. Claude Code
if ($installClaude -match "y") {
    if (-not (Test-Path $claudeBase)) { New-Item -ItemType Directory -Path $claudeBase -Force }
    Copy-Item -Path $SKILL_PATH -Destination $claudeBase -Recurse -Force
    Write-Host "📦 Installed for Claude Code." -ForegroundColor Green
}

# 3. GitHub Copilot
if ($installCopilot -match "y") {
    if (-not (Test-Path $copilotBase)) { New-Item -ItemType Directory -Path $copilotBase -Force }
    Copy-Item -Path $SKILL_PATH -Destination $copilotBase -Recurse -Force
    Write-Host "📦 Installed for GitHub Copilot." -ForegroundColor Green
}

Write-Host "`n✅ Installation process complete!" -ForegroundColor Cyan
Write-Host "💡 Remember to reload your agents to see the new skill."
Write-Host "   - Gemini: /skills reload"
Write-Host "   - Claude/Copilot: Restart your session or project."
