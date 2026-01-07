#!/usr/bin/env python3
"""
Elmar Tools Parking API - Search and manage parking reservations.
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

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def search_parking(booking_id: str, campaign: str | None = None, env: str = "prod") -> dict:
    """
    Search for parking offers for a booking.

    Args:
        booking_id: Booking ID (UUID)
        campaign: Optional campaign ID to override default
        env: Environment (prod, acc, dev)

    Returns:
        List of parking offers with service information flags:
        - valet: Valet parking service
        - overnight_stay: Includes hotel stay
        - taxi: Taxi service (pickup from home)
        - shuttle: Shuttle to airport
        - shuttle_people_included: People included in shuttle (0=paid, 99=unlimited)
        - public_transport: Public transport to airport
        - walking_distance: Within walking distance
        - app_required: Requires Mobian app
        - enclosed: Private enclosed area
        - guarded: 24/7 guards
        - indoor: True=indoor, False=outdoor, null=unknown
        - keep_key: True=keep key, False=hand in, null=unknown
        - open247: Open 24/7
        - security_cameras: Camera surveillance
        - wheelchair_friendly: Wheelchair accessible
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"parking/{booking_id}/search")

    params = {}
    if campaign:
        params["campaign"] = campaign

    try:
        response = requests.get(url, headers=headers, params=params if params else None, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def create_parking_reservation(
    booking_id: str,
    provider: int,
    license_plate: str,
    comment: str | None = None,
    card: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Create a parking reservation for a booking.

    Args:
        booking_id: Booking ID (UUID)
        provider: Provider ID from search results
        license_plate: Vehicle license plate (format: AA-11-BB)
        comment: Optional comment to send to provider
        card: Optional credit card number (used as ID with some providers)
        env: Environment (prod, acc, dev)

    Returns:
        Reservation confirmation
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"parking/{booking_id}")

    data = {
        "provider": provider,
        "license_plate": license_plate,
    }
    if comment:
        data["comment"] = comment
    if card:
        data["card"] = card

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def cancel_parking_reservation(booking_id: str, env: str = "prod") -> dict:
    """
    Cancel a parking reservation for a booking.

    Args:
        booking_id: Booking ID (UUID)
        env: Environment (prod, acc, dev)

    Returns:
        Cancellation confirmation
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"parking/{booking_id}")

    try:
        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json() if response.text else {"status": "cancelled"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Parking API")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default="prod",
                        help="Environment (default: prod)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search
    search_parser = subparsers.add_parser("search", help="Search parking offers")
    search_parser.add_argument("--booking-id", required=True, help="Booking ID (UUID)")
    search_parser.add_argument("--campaign", help="Override default campaign ID")

    # Create
    create_parser = subparsers.add_parser("create", help="Create parking reservation")
    create_parser.add_argument("--booking-id", required=True, help="Booking ID (UUID)")
    create_parser.add_argument("--provider", required=True, type=int,
                               help="Provider ID from search results")
    create_parser.add_argument("--license-plate", required=True,
                               help="Vehicle license plate (e.g., AA-11-BB)")
    create_parser.add_argument("--comment", help="Optional comment to provider")
    create_parser.add_argument("--card", help="Optional credit card number (ID for some providers)")

    # Cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel parking reservation")
    cancel_parser.add_argument("--booking-id", required=True, help="Booking ID (UUID)")

    args = parser.parse_args()

    if args.command == "search":
        result = search_parking(
            args.booking_id,
            campaign=args.campaign,
            env=args.env
        )

    elif args.command == "create":
        result = create_parking_reservation(
            booking_id=args.booking_id,
            provider=args.provider,
            license_plate=args.license_plate,
            comment=args.comment,
            card=args.card,
            env=args.env
        )

    elif args.command == "cancel":
        result = cancel_parking_reservation(args.booking_id, args.env)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
