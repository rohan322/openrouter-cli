import utils
import sys
import time
import json

def run(args):
    """Generate a new key."""
    prov_key = utils.get_provisioning_key()
    
    user_conf = utils.load_json_config(utils.USER_CONFIG_FILE)
    if user_conf.get("key_hash"):
        print(f"Warning: A key hash already exists in {utils.USER_CONFIG_FILE}.", file=sys.stderr)
        resp = input("Do you want to generate a new key and overwrite it? [y/N] ").strip().lower()
        if resp != "y":
            print("Aborted.", file=sys.stderr)
            return

    name = args.name or f"cli-key-{int(time.time())}"
    print(f"Generating new key '{name}'...", file=sys.stderr)
    
    url = f"{utils.BASE_URL}/keys"
    payload = {
        "name": name,
        "limit": 100.0 # Default limit of $100
    }
    
    result = utils.make_request(url, prov_key, method="POST", data=payload)
    
    key_data = result.get("data", {})
    new_key = result.get("key")
    if not new_key:
         # Fallback to check inside data
         new_key = key_data.get("key")
    
    if not new_key:
        print("Error: API did not return a key.", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
        
    print("\n" + "="*60)
    print(f"NEW KEY GENERATED: {new_key}")
    print("="*60)
    print("SAVE THIS KEY SECURELY. IT WILL NOT BE SHOWN AGAIN.")
    print("="*60 + "\n")
    
    key_hash = key_data.get("hash") or key_data.get("key_hash")
    
    save_data = {
        "key_hash": key_hash,
        "created_at": time.time(),
        "key_name": name
    }
    utils.save_json_config(utils.USER_CONFIG_FILE, save_data)
    print(f"Key hash saved to {utils.USER_CONFIG_FILE}.", file=sys.stderr)
