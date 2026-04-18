import sys
import json
import urllib.request
import urllib.parse
import os
import subprocess

def get_secure_secret(name):
    """Retrieve a secret from the system's secure store (SecretStore on Win, Keychain on macOS)."""
    # 1. Try Windows PowerShell SecretStore
    if sys.platform == "win32":
        try:
            # We use powershell to call Get-Secret. This requires SecretManagement module.
            cmd = ["powershell.exe", "-NoProfile", "-Command", f"Get-Secret -Name {name} -AsPlainText"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None

    # 2. Try macOS Keychain
    elif sys.platform == "darwin":
        try:
            # We use the 'security' tool to find a generic password
            cmd = ["security", "find-generic-password", "-s", name, "-w"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None
    
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
    # Priority: 
    # 1. Command line args
    # 2. Environment variables
    # 3. Secure System Store (SecretStore/Keychain)
    
    key = os.environ.get("STEAM_API_KEY")
    steam_id = os.environ.get("STEAM_ID")

    if not key:
        key = get_secure_secret("STEAM_API_KEY")
    if not steam_id:
        steam_id = get_secure_secret("STEAM_ID")

    if len(sys.argv) < 4:
        print("Usage: python steam_query.py <interface> <method> <version> [key] [param1=value1] ...")
        print("Note: 'key' and 'steamid' can be set via env vars or system secure store (STEAM_API_KEY, STEAM_ID).")
        sys.exit(1)

    interface = sys.argv[1]
    method = sys.argv[2]
    version = sys.argv[3]
    
    start_idx = 4
    if len(sys.argv) > 4 and "=" not in sys.argv[4]:
        key = sys.argv[4]
        start_idx = 5
    
    if not key:
        print("Error: Steam Web API Key not found. Provide via argument, env var, or system secure store.")
        sys.exit(1)
    
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
