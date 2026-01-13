#!/usr/bin/env python3
"""
Elmar Tools Hotels API - Read-only access to hotel offers for bookings.
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

    return {"X-Api-Key": api_key}


def get_hotel_offers(
    booking_id: str,
    system: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Retrieve hotel offers for a booking.

    Currently supports booking.com as provider.

    Args:
        booking_id: Booking ID (UUID for internal, or external system ID)
        system: External system name (e.g., 'zeus') if using external ID
        env: Environment (prod, acc, dev)

    Returns:
        Hotel offers as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()

    if system:
        url = urljoin(base_url, f"hotels/{system}/{booking_id}")
    else:
        url = urljoin(base_url, f"hotels/{booking_id}")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Hotels API")
    default_env = os.environ.get("ELMAR_TOOLS_API_ENV", "prod")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default=default_env,
                        help=f"Environment (default: {default_env})")
    parser.add_argument("--booking-id", required=True,
                        help="Booking ID (UUID for internal, or external system ID)")
    parser.add_argument("--system", choices=["zeus"],
                        help="External system name (if using external booking ID)")

    args = parser.parse_args()

    result = get_hotel_offers(
        booking_id=args.booking_id,
        system=args.system,
        env=args.env
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
