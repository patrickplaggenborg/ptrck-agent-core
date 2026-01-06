#!/usr/bin/env python3
"""
Elmar Tools Transfer API - Read-only access to transfer inclusion checks.
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


def check_single_transfer(
    brand: str,
    product_id: str,
    departure_date: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Check if a single product has transfer included.

    Args:
        brand: Tour operator brand code
        product_id: Product ID
        departure_date: Optional departure date for temporal rules
        env: Environment (prod, acc, dev)

    Returns:
        Transfer information as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()

    url = urljoin(base_url, f"transfer/{brand}/{product_id}")
    params = {}
    if departure_date:
        params["departure_date"] = departure_date

    try:
        response = requests.get(url, headers=headers, params=params if params else None, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def check_multiple_transfers(
    products: str | None = None,
    departure_date: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Check multiple products for transfer inclusion.

    Args:
        products: Comma-separated product codes (e.g., VLVARVAR105.AL,VLVARVAR106.A1)
                  Omit to check all products.
        departure_date: Optional departure date for temporal rules
        env: Environment (prod, acc, dev)

    Returns:
        Transfer information for multiple products as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()

    url = urljoin(base_url, "transfer")
    params = {}
    if products:
        params["products"] = products
    if departure_date:
        params["departure_date"] = departure_date

    try:
        response = requests.get(url, headers=headers, params=params if params else None, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Transfer API")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default="prod",
                        help="Environment (default: prod)")
    parser.add_argument("--departure-date", help="Departure date for temporal transfer rules")

    # Single product check
    parser.add_argument("--brand", help="Tour operator brand code (for single product)")
    parser.add_argument("--product", help="Product ID (for single product)")

    # Multiple products check
    parser.add_argument("--products",
                        help="Comma-separated product codes with brand suffix "
                             "(e.g., VLVARVAR105.AL,VLVARVAR106.A1)")

    args = parser.parse_args()

    if args.brand and args.product:
        result = check_single_transfer(
            brand=args.brand,
            product_id=args.product,
            departure_date=args.departure_date,
            env=args.env
        )
    elif args.products or (not args.brand and not args.product):
        result = check_multiple_transfers(
            products=args.products,
            departure_date=args.departure_date,
            env=args.env
        )
    else:
        print(json.dumps({"error": "Provide either --brand and --product, or --products"}))
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
