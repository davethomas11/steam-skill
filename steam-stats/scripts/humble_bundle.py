import re
import urllib.request
import sys
import json
import urllib.request
import urllib.parse
import subprocess
import getpass
import os

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

    # 3. Get Bundle URL
    url = input("\nPaste Humble Bundle URL: ").strip()
    bundle_games = get_bundle_games_from_url(url)

    if not bundle_games:
        print("[!] No games found. Check URL or Humble anti-bot measures.")
        return

    # 4. Cross Reference
    owned = []
    missing = []

    for game in bundle_games:
        if game.lower() in owned_names_map:
            owned.append(game)
        else:
            missing.append(game)

    # 5. Report
    print("\n" + "="*40)
    print(f" BUNDLE ANALYSIS: {len(bundle_games)} Games Found")
    print("="*40)

    if owned:
        print(f"\n[!] ALREADY OWNED ({len(owned)}):")
        for g in owned: print(f"  - {g}")

    if missing:
        print(f"\n[+] MISSING / NEW ({len(missing)}):")
        for g in missing: print(f"  - {g}")

    print("\n" + "="*40)

if __name__ == "__main__":
    main()