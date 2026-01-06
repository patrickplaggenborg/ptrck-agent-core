#!/usr/bin/env python3
"""
Elmar Tools Lookup API - Read-only access to refunds, vouchers, tour operators, and recommendations.
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


def make_request(url: str, headers: dict) -> dict:
    """Make GET request and return JSON response."""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_refund(refund_id: str, env: str = "prod") -> dict:
    """
    Get refund details by refund ID.

    Args:
        refund_id: Refund ID
        env: Environment (prod, acc, dev)

    Returns:
        Refund details as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"refunds/{refund_id}")
    return make_request(url, headers)


def get_refunds_by_user_service(user_service_id: str, env: str = "prod") -> dict:
    """
    Get all refunds for a user service ID.

    Args:
        user_service_id: User service UUID
        env: Environment (prod, acc, dev)

    Returns:
        List of refunds as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"refunds/user_service_id/{user_service_id}")
    return make_request(url, headers)


def get_voucher(voucher_code: str, env: str = "prod") -> dict:
    """
    Get voucher details by voucher code.

    Args:
        voucher_code: Voucher code
        env: Environment (prod, acc, dev)

    Returns:
        Voucher details as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"vouchers/{voucher_code}")
    return make_request(url, headers)


def get_vouchers_by_user_service(user_service_id: str, env: str = "prod") -> dict:
    """
    Get all vouchers for a user service ID.

    Args:
        user_service_id: User service UUID
        env: Environment (prod, acc, dev)

    Returns:
        List of vouchers as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"vouchers/user_service_id/{user_service_id}")
    return make_request(url, headers)


def get_touroperators(env: str = "prod") -> dict:
    """
    Get tour operator configuration (names, blacklist, etc).

    Args:
        env: Environment (prod, acc, dev)

    Returns:
        Tour operator configuration as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "touroperators")
    return make_request(url, headers)


def get_recommendations(booking_id: str, env: str = "prod") -> dict:
    """
    Get recommendations for a booking.

    Args:
        booking_id: Booking ID (UUID)
        env: Environment (prod, acc, dev)

    Returns:
        Recommendations as dict
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"recommend/{booking_id}")
    return make_request(url, headers)


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Lookup API")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default="prod",
                        help="Environment (default: prod)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Refunds
    refunds_parser = subparsers.add_parser("refunds", help="Get refund details")
    refunds_parser.add_argument("--id", help="Refund ID")
    refunds_parser.add_argument("--user-service-id", help="User service UUID")

    # Vouchers
    vouchers_parser = subparsers.add_parser("vouchers", help="Get voucher details")
    vouchers_parser.add_argument("--code", help="Voucher code")
    vouchers_parser.add_argument("--user-service-id", help="User service UUID")

    # Tour operators
    subparsers.add_parser("touroperators", help="Get tour operator configuration")

    # Recommendations
    recommend_parser = subparsers.add_parser("recommend", help="Get recommendations for a booking")
    recommend_parser.add_argument("--booking-id", required=True, help="Booking ID (UUID)")

    args = parser.parse_args()

    if args.command == "refunds":
        if args.id:
            result = get_refund(args.id, args.env)
        elif args.user_service_id:
            result = get_refunds_by_user_service(args.user_service_id, args.env)
        else:
            print(json.dumps({"error": "Provide either --id or --user-service-id"}))
            sys.exit(1)
    elif args.command == "vouchers":
        if args.code:
            result = get_voucher(args.code, args.env)
        elif args.user_service_id:
            result = get_vouchers_by_user_service(args.user_service_id, args.env)
        else:
            print(json.dumps({"error": "Provide either --code or --user-service-id"}))
            sys.exit(1)
    elif args.command == "touroperators":
        result = get_touroperators(args.env)
    elif args.command == "recommend":
        result = get_recommendations(args.booking_id, args.env)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
