import re
import urllib.request
import sys
import json
import urllib.parse
import subprocess
import getpass
import os
import difflib

def normalize_name(name):
    """Lowercases and removes common edition suffixes for better matching."""
    if not name:
        return ""
    # Convert to lowercase
    name = name.lower()
    # Remove common 'Edition' suffixes but preserve sequel numbers
    name = re.sub(r'\s*(standard|deluxe|gold|ultimate|definitive|anniversary|enhanced|game of the year|goty)\s+edition', '', name)
    # Remove content in parentheses (usually 'Mac', 'Windows', 'Beta', etc.)
    name = re.sub(r'\s*\(.*?\)', '', name)
    # Collapse multiple spaces
    return " ".join(name.split())

def get_macos_secret(name):
    """Retrieve a secret from macOS Keychain."""
    try:
        cmd = ["security", "find-generic-password", "-s", name, "-w"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return None

def get_windows_secrets(secret_names):
    """Unlocks SecretStore and retrieves secrets in a single session."""
    print(f"[*] Accessing SecretStore for: {', '.join(secret_names)}")
    vault_password = getpass.getpass("Enter SecretStore password: ")

    if not vault_password:
        return {}

    # Escape single quotes for PowerShell
    escaped_password = vault_password.replace("'", "''")

    # We use SecureString to satisfy PowerShell's requirements
    ps_parts = [
        f"$pass = ConvertTo-SecureString '{escaped_password}' -AsPlainText -Force",
        "Unlock-SecretStore -Password $pass -ErrorAction Stop",
        "$results = @{}"
    ]

    for name in secret_names:
        ps_parts.append(f"try {{ $results['{name}'] = Get-Secret -Name '{name}' -AsPlainText }} catch {{}}")

    ps_parts.append("$results | ConvertTo-Json")
    ps_command = "; ".join(ps_parts)

    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_command],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except Exception as e:
        print(f"[!] PowerShell Error: {e}", file=sys.stderr)
        return {}

def get_owned_games(api_key, steam_id):
    """Fetches the full library from Steam API."""
    params = {
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,
        "format": "json"
    }
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data.get("response", {}).get("games", [])
    except Exception as e:
        print(f"[!] Steam API Error: {e}")
        return []

def get_bundle_games_from_url(url):
    """Scrapes game titles from a Humble Bundle URL."""
    print(f"[*] Scraping bundle: {url}")

    # Spoof a real browser to avoid 403 Forbidden errors
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')

            # Humble Bundle uses 'human_name' in their internal JSON blob
            titles = re.findall(r'\"human_name\":\s*\"(.*?)\"', html)

            # Fallback to <span> if the JSON blob structure changes
            if not titles:
                titles = re.findall(r'<span class=\"item-title\">(.*?)</span>', html)

            return sorted(list(set([t.strip() for t in titles if t])))
    except Exception as e:
        print(f"[!] Scraping failed: {e}")
        return []

def get_game_details_from_steam(game_name):
    """Attempts to find a Metacritic score and description using the Steam Store API."""
    details = {"score": "N/A", "description": "No description available."}
    try:
        search_url = f"https://store.steampowered.com/api/storesearch/?term={urllib.parse.quote(game_name)}&l=english&cc=US"
        with urllib.request.urlopen(search_url, timeout=5) as response:
            search_data = json.loads(response.read().decode())
            if search_data.get("total") > 0:
                appid = search_data["items"][0]["id"]
                
                details_url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
                with urllib.request.urlopen(details_url, timeout=5) as details_response:
                    details_data = json.loads(details_response.read().decode())
                    if details_data.get(str(appid), {}).get("success"):
                        data = details_data[str(appid)]["data"]
                        details["score"] = str(data.get("metacritic", {}).get("score", "N/A"))
                        # Clean up HTML tags from description
                        desc = data.get("short_description", "")
                        details["description"] = re.sub(r'<.*?>', '', desc)[:150] + "..." if desc else details["description"]
    except:
        pass
    return details

def main():
     # 1. Check Environment Variables first
    key = os.environ.get("STEAM_API_KEY")
    steam_id = os.environ.get("STEAM_ID")

    # If missing, try Secure Stores
    needed_from_store = []
    if not key: needed_from_store.append("STEAM_API_KEY")
    if not steam_id: needed_from_store.append("STEAM_ID")

    if needed_from_store:
        if sys.platform == "win32":
            # Batch fetch from Windows
            secrets = get_windows_secrets(needed_from_store)
            key = key or secrets.get("STEAM_API_KEY")
            steam_id = steam_id or secrets.get("STEAM_ID")
        elif sys.platform == "darwin":
            # Fetch individually from macOS
            if not key: key = get_macos_secret("STEAM_API_KEY")
            if not steam_id: steam_id = get_macos_secret("STEAM_ID")

    if not key or not steam_id:
        print("[!] Missing credentials. Exiting.")
        sys.exit(1)

    # 2. Get Steam Library
    print("[*] Fetching your Steam library...")
    library = get_owned_games(key, steam_id)
    if not library:
        print("[!] Library is empty or API failed.")
        sys.exit(1)

    # Map for O(1) lookup
    owned_names_map = {g['name'].lower(): g for g in library}
    
    # Pre-normalize the library for fuzzy matching
    normalized_owned = {}
    for g in library:
        norm = normalize_name(g['name'])
        if norm:
            # Store the original name for the report
            normalized_owned[norm] = g['name']

    # 3. Get Bundle URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("\nPaste Humble Bundle URL: ").strip()
    
    bundle_games = get_bundle_games_from_url(url)

    if not bundle_games:
        print("[!] No games found. Check URL or Humble anti-bot measures.")
        return

    # 4. Cross Reference
    owned = []
    missing = []
    normalized_owned_keys = list(normalized_owned.keys())

    for game in bundle_games:
        # 1. Direct case-insensitive match (fastest)
        if game.lower() in owned_names_map:
            owned.append(game)
            continue
            
        # 2. Match after normalization (handles special chars, 'Deluxe Edition', etc.)
        norm_game = normalize_name(game)
        if norm_game in normalized_owned:
            match_name = normalized_owned[norm_game]
            owned.append(f"{game} (matches: {match_name})")
            continue
            
        # 3. Fuzzy match using difflib (handles typos/slight variations)
        matches = difflib.get_close_matches(norm_game, normalized_owned_keys, n=1, cutoff=0.95)
        if matches:
            match_name = normalized_owned[matches[0]]
            owned.append(f"{game} (fuzzy matches: {match_name})")
        else:
            missing.append(game)

    # 5. Report
    # ANSI Colors
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print("\n" + "="*60)
    print(f"{BOLD} BUNDLE ANALYSIS: {len(bundle_games)} Items Found{RESET}")
    print("="*60)

    if owned:
        print(f"\n{RED}[!] ALREADY OWNED ({len(owned)}):{RESET}")
        for g in owned: 
            clean_name = g.split(" (")[0]
            details = get_game_details_from_steam(clean_name)
            print(f"  {BOLD}- {g}{RESET}")
            print(f"    {CYAN}Metascore:{RESET} {details['score'].rjust(3)} | {details['description']}")

    if missing:
        print(f"\n{GREEN}[+] MISSING / NEW ({len(missing)}):{RESET}")
        for g in missing:
            # Skip items that are clearly not games
            if any(x in g.lower() for x in ["charity", "bundle", "plan", "month-to-month"]):
                print(f"  - {g}")
                continue
                
            details = get_game_details_from_steam(g)
            print(f"  {BOLD}- {g}{RESET}")
            print(f"    {CYAN}Metascore:{RESET} {details['score'].rjust(3)} | {details['description']}")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()