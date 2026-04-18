---
name: steam-stats
description: Read-only operations for the Steam Web API. Use to retrieve owned games, player stats, achievements, and recently played games for a Steam user.
---

# Steam Stats Skill

This skill allows you to retrieve data from the Steam Web API.

## Setup

To use this skill, the user must provide a **Steam Web API Key** and a **SteamID64**.

### Safe Storage (Recommended)
Store your credentials in a `.env` file in your workspace or user directory (`~/.gemini/.env`):
```env
STEAM_API_KEY=your_api_key_here
STEAM_ID=your_17_digit_id_here
```
Gemini CLI automatically loads these variables and redacts them from logs to ensure they are handled safely.

If these variables are not set, you will be prompted to provide them.

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
