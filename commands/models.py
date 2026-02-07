import utils
import sys

def run(args):
    """List available authorized models."""
    prov_key = utils.get_provisioning_key()
    
    print("Fetching models...", file=sys.stderr)
    url = f"{utils.BASE_URL}/models"
    
    result = utils.make_request(url, prov_key)
    data = result.get("data", [])
    
    print(f"Found {len(data)} total models.", file=sys.stderr)
    
    # Filter authorized models
    authorized_models = []
    for model in data:
        mid = model.get("id", "")
        normalized_id = mid.lower()
        for auth in utils.AUTHORIZED_PROVIDERS:
            if auth in normalized_id:
                pricing = model.get("pricing", {})
                # Handle string pricing "0" -> 0.0
                try:
                    prompt = float(pricing.get("prompt", "0"))
                    completion = float(pricing.get("completion", "0"))
                except ValueError:
                    prompt = 0.0
                    completion = 0.0
                
                # Calculate cost per 1 Million tokens (Blended: 1M prompt + 1M completion)
                # API returns price per token.
                cost_per_1m = (prompt + completion) * 1_000_000
                
                authorized_models.append({
                    "id": mid,
                    "name": model.get("name", ""),
                    "context": model.get("context_length", 0),
                    "prompt": prompt * 1_000_000,
                    "completion": completion * 1_000_000,
                    "blended_cost_1m": cost_per_1m
                })
                break
    
    # Sort by cost descending (Expensive first)
    # Sort by cost descending (Expensive first) within groups
    authorized_models.sort(key=lambda x: x["blended_cost_1m"], reverse=True)
    
    # Group by Provider
    models_by_provider = {}
    
    for m in authorized_models:
        # Extract provider from ID (e.g. "openai/gpt-4" -> "openai")
        if "/" in m["id"]:
            provider = m["id"].split("/")[0]
        else:
            provider = "other"
            
        if provider not in models_by_provider:
            models_by_provider[provider] = []
        models_by_provider[provider].append(m)

    def print_provider_group(provider_name, models_list):
        if not models_list: return
        print(f"\n--- {provider_name.upper()} ---")
        print(f"{'ID':<45} {'Context':<10} {'Prompt($/1M)':<14} {'Compl($/1M)':<14}")
        print("-" * 87)
        for m in models_list:
            print(f"{m['id']:<45} {m['context']:<10} {m['prompt']:<14.2f} {m['completion']:<14.2f}")

    # Print in alphabetical order of provider
    sorted_providers = sorted(models_by_provider.keys())
    for prov in sorted_providers:
        print_provider_group(prov, models_by_provider[prov])

    print("-" * 87)
    print(f"Listed {len(authorized_models)} authorized models across {len(sorted_providers)} providers.", file=sys.stderr)
