import sys
import json
import urllib.request
import urllib.parse
import os
import subprocess
import getpass

def get_windows_secrets(secret_names):
    """
    Unlocks the SecretStore and retrieves multiple secrets in one single
    PowerShell session to maintain the unlocked state.
    """
    print(f"Windows SecretStore: Attempting to retrieve {', '.join(secret_names)}...")
    vault_password = getpass.getpass("Enter your SecretStore password: ")

    if not vault_password:
        print("Password cannot be empty.", file=sys.stderr)
        return {}

    # Escape single quotes for PowerShell
    escaped_password = vault_password.replace("'", "''")

    # We build a PS script that unlocks the store and creates a hash table of secrets
    # then converts that table to JSON for Python to read easily.
    # We convert the raw string into a SecureString object inside PowerShell
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
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to unlock store or retrieve secrets. \n{e.stderr}", file=sys.stderr)
        return {}
    except json.JSONDecodeError:
        return {}

def get_macos_secret(name):
    """Retrieve a secret from macOS Keychain."""
    try:
        cmd = ["security", "find-generic-password", "-s", name, "-w"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return None

def make_request(interface, method, version, params):
    base_url = f"https://api.steampowered.com/{interface}/{method}/{version}/"
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"

    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            else:
                return {"error": f"HTTP Error {response.status}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    # 1. Check Environment Variables first
    key = os.environ.get("STEAM_API_KEY")
    steam_id = os.environ.get("STEAM_ID")

    # 2. If missing, try Secure Stores
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

    # 3. Parse CLI Arguments
    if len(sys.argv) < 3:
        print("Usage: python steam_query.py <interface> <method> <version> [key] [param1=value1] ...")
        sys.exit(1)

    interface = sys.argv[1]
    method = sys.argv[2]
    if len(sys.argv) > 3:
        version = sys.argv[3]
    else:
        version = "v1"  # Default version if not provided

    # Optional key override in CLI args
    start_idx = 4
    if len(sys.argv) > 4 and "=" not in sys.argv[4]:
        key = sys.argv[4]
        start_idx = 5

    if not key:
        print("Error: STEAM_API_KEY not found in environment, store, or arguments.")
        sys.exit(1)

    # 4. Prepare and execute request
    params = {"key": key}
    if steam_id:
        params["steamid"] = steam_id

    for arg in sys.argv[start_idx:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            params[k] = v

    result = make_request(interface, method, version, params)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()