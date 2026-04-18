import sys
import json
import urllib.request
import urllib.parse
import os

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
    # Priority: Command line args > Environment variables
    key = os.environ.get("STEAM_API_KEY")
    steam_id = os.environ.get("STEAM_ID")

    if len(sys.argv) < 4:
        print("Usage: python steam_query.py <interface> <method> <version> [key] [param1=value1] ...")
        print("Note: 'key' and 'steamid' can be set via STEAM_API_KEY and STEAM_ID env vars.")
        sys.exit(1)

    interface = sys.argv[1]
    method = sys.argv[2]
    version = sys.argv[3]
    
    start_idx = 4
    if len(sys.argv) > 4 and "=" not in sys.argv[4]:
        key = sys.argv[4]
        start_idx = 5
    
    if not key:
        print("Error: Steam Web API Key not found in arguments or STEAM_API_KEY env var.")
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
