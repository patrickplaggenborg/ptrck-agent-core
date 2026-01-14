#!/usr/bin/env python3
"""
Elmar Tools Baggage API - Read-only access to baggage allowance information.
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


def get_hold_baggage(
    brand: str,
    carrier: str,
    origin: str,
    destination: str,
    departure: str,
    arrival: str,
    env: str = "prod"
) -> dict:
    """
    Get included checked (hold) baggage based on criteria.

    Args:
        brand: Tour operator brand code
        carrier: Carrier IATA/ICAO code
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure: Departure date or datetime
        arrival: Arrival date or datetime
        env: Environment (prod, acc, dev)

    Returns:
        Baggage information as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()

    url = urljoin(base_url, "baggage")
    params = {
        "brand": brand,
        "carrier": carrier,
        "origin": origin,
        "destination": destination,
        "departure": departure,
        "arrival": arrival,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_hand_baggage(carrier: str, brand: str | None = None, env: str = "prod") -> dict:
    """
    Get cabin (hand) baggage for an airline.

    Args:
        carrier: Carrier IATA/ICAO code
        brand: Optional tour operator brand code
        env: Environment (prod, acc, dev)

    Returns:
        Hand baggage information as dict (empty JSON with 404 for unknown carriers)
    """
    base_url = get_base_url(env)
    headers = get_headers()

    url = urljoin(base_url, "handbaggage")
    params = {"carrier": carrier}
    if brand:
        params["brand"] = brand

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"message": "Unknown hand baggage information for this carrier"}
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Baggage API")
    default_env = os.environ.get("ELMAR_TOOLS_API_ENV", "prod")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default=default_env,
                        help=f"Environment (default: {default_env})")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Hold baggage
    hold_parser = subparsers.add_parser("hold", help="Get checked (hold) baggage info")
    hold_parser.add_argument("--brand", required=True, help="Tour operator brand code")
    hold_parser.add_argument("--carrier", required=True, help="Carrier IATA/ICAO code")
    hold_parser.add_argument("--origin", required=True, help="Origin airport IATA code")
    hold_parser.add_argument("--destination", required=True, help="Destination airport IATA code")
    hold_parser.add_argument("--departure", required=True, help="Departure date/datetime")
    hold_parser.add_argument("--arrival", required=True, help="Arrival date/datetime")

    # Hand baggage
    hand_parser = subparsers.add_parser("hand", help="Get cabin (hand) baggage info")
    hand_parser.add_argument("--carrier", required=True, help="Carrier IATA/ICAO code")
    hand_parser.add_argument("--brand", help="Optional tour operator brand code")

    args = parser.parse_args()

    if args.command == "hold":
        result = get_hold_baggage(
            brand=args.brand,
            carrier=args.carrier,
            origin=args.origin,
            destination=args.destination,
            departure=args.departure,
            arrival=args.arrival,
            env=args.env
        )
    elif args.command == "hand":
        result = get_hand_baggage(
            carrier=args.carrier,
            brand=args.brand,
            env=args.env
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
