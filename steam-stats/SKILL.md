---
name: steam-stats
description: Read-only operations for the Steam Web API. Use to retrieve owned games, player stats, achievements, and recently played games for a Steam user.
---

# Steam Stats Skill

This skill allows you to retrieve data from the Steam Web API.

## Setup

To use this skill, the user must provide a **Steam Web API Key** and a **SteamID64**.

### Safe Storage (Recommended)
Store your credentials in a `.env` file, or use your system's secure store:
- **Windows:** `Set-Secret -Name STEAM_API_KEY -Secret "..."` (Requires SecretManagement module)
- **macOS:** `security add-generic-password -s STEAM_API_KEY -w "..."`

Gemini CLI automatically loads environment variables and redacts them. The skill's scripts will fallback to system secure stores if environment variables are missing.

On windows you can use the following commands to set your secrets in the local vault:
```powershell
Set-Secret -Name STEAM_API_KEY -Secret "your_key"
Set-Secret -Name STEAM_ID -Secret "your_id"
```

But this requires the Microsoft.PowerShell.SecretManagement and Microsoft.PowerShell.SecretStore modules to be installed and configured. See the [README](README.md) for instructions.
And a vault to be registered (e.g., `LocalStore`).

On Windows the script will prompt for the users vault password to retrieve the secrets. If the vault is not unlocked, it will prompt the user to unlock it first.
This needs to happen everytime because the Get-Secrets command is run in a subprocess, so the vault state is not shared.

If these variables are not set, you will be prompted to provide them.

### Troubleshooting (April 2026 Process)
- **Steam App Auth:** Creating a new API key requires authentication via the **Steam Mobile App**. This step **does not send a push notification**. The user must open the app, tap the **hamburger menu (three lines)**, and select **Confirmations** to approve the request.
- **Rate Limits:** If the user gets "Too Many Requests," advise them to wait and stop repeated attempts.

## Workflows

### 1. Get Owned Games
Use this to see what games a user owns.
- Call `scripts/steam_query.py IPlayerService GetOwnedGames v1 include_appinfo=true`.
- Reference `references/api_endpoints.md` for more parameters.

### 2. Get Player Stats or Achievements
Use this to check progress in a specific game.
- You will need the `appid` of the game (retrieved from owned games or provided by the user).
- Call `scripts/steam_query.py ISteamUserStats GetPlayerAchievements v1 appid=<appid>`.
- Call `scripts/steam_query.py ISteamUserStats GetUserStatsForGame v2 appid=<appid>`.

### 3. Resolve Vanity URL
If the user provides a profile link or name (e.g., `https://steamcommunity.com/id/example`), resolve it to a SteamID64 first.
- Call `scripts/steam_query.py ISteamUser ResolveVanityURL v1 vanityurl=example`.

## Reference

Detailed endpoint information is available in [references/api_endpoints.md](references/api_endpoints.md).

## Notes
- User profile privacy settings may prevent data retrieval. If an endpoint returns an empty result, inform the user that their profile or game details might be set to "Private".
