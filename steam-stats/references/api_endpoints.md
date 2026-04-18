# Steam Web API Reference (Read-Only)

All requests should be made to `https://api.steampowered.com/`.
Authentication requires a `key` (Steam Web API Key) and usually a `steamid` (SteamID64).

## Core Endpoints

### IPlayerService

#### GetOwnedGames
Returns a list of games a player owns.
- **Endpoint:** `GET /IPlayerService/GetOwnedGames/v1/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `steamid`: SteamID64
    - `include_appinfo` (optional, bool): Include game names and logo hashes.
    - `include_played_free_games` (optional, bool): Include free games played.
    - `format` (optional): `json` (default), `xml`, `vdf`.

#### GetRecentlyPlayedGames
Returns a list of games a player has played in the last two weeks.
- **Endpoint:** `GET /IPlayerService/GetRecentlyPlayedGames/v1/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `steamid`: SteamID64
    - `count` (optional, int): Limit results.

### ISteamUserStats

#### GetPlayerAchievements
Returns a list of achievements for a specific game and user.
- **Endpoint:** `GET /ISteamUserStats/GetPlayerAchievements/v1/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `steamid`: SteamID64
    - `appid`: AppID of the game.
    - `l` (optional): Language for achievement names.

#### GetUserStatsForGame
Returns a list of stats for a specific game and user.
- **Endpoint:** `GET /ISteamUserStats/GetUserStatsForGame/v2/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `steamid`: SteamID64
    - `appid`: AppID of the game.

#### GetSchemaForGame
Returns the "friendly" names for stats and achievements of a game.
- **Endpoint:** `GET /ISteamUserStats/GetSchemaForGame/v2/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `appid`: AppID of the game.

### ISteamUser

#### GetPlayerSummaries
Returns basic profile information (nickname, avatar, etc.).
- **Endpoint:** `GET /ISteamUser/GetPlayerSummaries/v2/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `steamids`: Comma-separated list of SteamID64s.

#### ResolveVanityURL
Converts a vanity URL (e.g., `https://steamcommunity.com/id/vanityname`) to a SteamID64.
- **Endpoint:** `GET /ISteamUser/ResolveVanityURL/v1/`
- **Parameters:**
    - `key`: Steam Web API Key
    - `vanityurl`: The vanity name (the part after `/id/`).
