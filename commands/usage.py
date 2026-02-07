import utils
import sys

def run(args):
    """Check usage for the stored key hash."""
    prov_key = utils.get_provisioning_key()
    # We load key_hash here
    try:
        key_hash = utils.get_key_hash()
    except SystemExit:
        # If get_key_hash exits, we let it exit.
        # But wait, get_key_hash calls sys.exit(1).
        # That's fine for a CLI tool.
        return
        
    print(f"Checking usage for key hash: {key_hash[:8]}...", file=sys.stderr)
    
    url = f"{utils.BASE_URL}/keys/{key_hash}"
    
    try:
        result = utils.make_request(url, prov_key)
        data = result.get("data", {})
        
        limit = data.get("limit")
        usage = data.get("usage", 0)
        limit_str = f"${limit}" if limit is not None else "Unlimited"
        
        print(f"\nUsage Stats for Key ({key_hash[:8]}...)")
        print("-" * 40)
        print(f"Usage:   ${usage}")
        print(f"Limit:   {limit_str}")
        print("-" * 40)
        
    except SystemExit:
        print("Failed to fetch key details. Is the hash correct?", file=sys.stderr)
        sys.exit(1)
