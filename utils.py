"""
utils.py
Common utilities for OpenRouter CLI.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any, Dict, Optional, Tuple

APP_CONFIG_FILE = "app.config"
USER_CONFIG_FILE = "user.config"
BASE_URL = "https://openrouter.ai/api/v1"

# Authorized ZDR providers
AUTHORIZED_PROVIDERS = {
    "azure",
    "google vertex",
    "google",
    "openai",
    "anthropic",
    "amazon bedrock",
    "google ai studio",
    "vertex",
    "bedrock",
}

def load_json_config(filename: str) -> Dict[str, Any]:
    """Load JSON config from file."""
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {filename}: {e}", file=sys.stderr)
        sys.exit(1)

def save_json_config(filename: str, data: Dict[str, Any]) -> None:
    """Save JSON config to file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    except Exception as e:
        print(f"Error writing to {filename}: {e}", file=sys.stderr)
        sys.exit(1)

def get_provisioning_key() -> str:
    """Get the provisioning key from app.config."""
    config = load_json_config(APP_CONFIG_FILE)
    key = config.get("provisioning_key")
    if not key:
        print(f"Error: 'provisioning_key' not found in {APP_CONFIG_FILE}.", file=sys.stderr)
        print(f"Please update {APP_CONFIG_FILE} with your key.", file=sys.stderr)
        sys.exit(1)
    return key

def get_key_hash() -> str:
    """Get the key hash from user.config."""
    config = load_json_config(USER_CONFIG_FILE)
    key_hash = config.get("key_hash")
    if not key_hash:
        print(f"Error: 'key_hash' not found in {USER_CONFIG_FILE}.", file=sys.stderr)
        print("Run 'make-key' to generate a key and store its hash.", file=sys.stderr)
        sys.exit(1)
    return key_hash

def make_request(url: str, api_key: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make an authenticated request to OpenRouter API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status == 204:
                return {}
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        print(f"HTTP error {exc.code} for {url}: {exc.reason}", file=sys.stderr)
        body = exc.read()
        if body:
            print(body.decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Request failed for {url}: {exc}", file=sys.stderr)
        sys.exit(1)
