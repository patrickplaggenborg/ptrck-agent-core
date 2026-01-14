#!/usr/bin/env python3
"""
Elmar Tools Customer API - Read-only access to customer information.
"""

import argparse
import json
import os
import sys
from urllib.parse import urljoin

import requests


def get_base_url(env: str = "prod") -> str:
    """Get base URL for the specified environment."""
    urls = {
        "prod": "https://api.elmar.nl/tools/",
        "acc": "https://api.acc.elmar.nl/tools/",
        "dev": "http://localhost:4000/",
    }
    return urls.get(env, urls["prod"])


def get_headers() -> dict:
    """Get request headers including API key."""
    api_key = os.environ.get("ELMAR_TOOLS_API_KEY")
    if not api_key:
        print(json.dumps({"error": "ELMAR_TOOLS_API_KEY environment variable not set"}))
        sys.exit(1)

    return {"Authorization": f"Bearer {api_key}"}


def get_customer(customer_id: str, env: str = "prod") -> dict:
    """
    Get customer information by ID.

    Args:
        customer_id: Database ID (UUID) or customer number (e.g., C001219087)
        env: Environment (prod, acc, dev)

    Returns:
        Customer information as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()

    url = urljoin(base_url, f"customers/{customer_id}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Customer API")
    default_env = os.environ.get("ELMAR_TOOLS_API_ENV", "prod")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default=default_env,
                        help=f"Environment (default: {default_env})")
    parser.add_argument("--id", required=True,
                        help="Customer ID (UUID) or customer number (e.g., C001219087)")

    args = parser.parse_args()

    result = get_customer(args.id, args.env)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
