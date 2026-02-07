#!/usr/bin/env python3
"""
OpenRouter CLI
==============

A command-line tool to manage OpenRouter API keys and check usage/credits.
Works with a `app.config` (Provisioning Key) and restricts user key storage to a hash in `user.config`.

Commands:
  models    List authorized ZDR models available to your org.
  make-key  Generate a new API key using the provisioning key.
  usage     Check credit usage and remaining balance (using stored key hash).

Configuration:
  app.config   - MUST contain valid JSON: {"provisioning_key": "sk-or-prov-..."}
  user.config  - Usage data: {"key_hash": "..."} (Managed by make-key)
"""

import argparse
from commands import models, make_key, usage

def main():
    parser = argparse.ArgumentParser(description="OpenRouter CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Models
    subparsers.add_parser("models", help="List available models")
    
    # Make Key
    mk_parser = subparsers.add_parser("make-key", help="Generate a new API key")
    mk_parser.add_argument("--name", help="Name for the new key")
    
    # Usage
    subparsers.add_parser("usage", help="Check usage for stored key")
    
    args = parser.parse_args()
    
    if args.command == "models":
        models.run(args)
    elif args.command == "make-key":
        make_key.run(args)
    elif args.command == "usage":
        usage.run(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
