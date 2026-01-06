#!/usr/bin/env python3
"""
Elmar Tools Booking API - Full CRUD operations for bookings, insurances, payments, and confirmations.
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


def get_headers(locale: str | None = None) -> dict:
    """Get request headers including API key and optional locale."""
    api_key = os.environ.get("ELMAR_TOOLS_API_KEY")
    if not api_key:
        print(json.dumps({"error": "ELMAR_TOOLS_API_KEY environment variable not set"}))
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if locale:
        headers["Accept-Language"] = locale
    return headers


def make_get(url: str, headers: dict, params: dict | None = None) -> dict:
    """Make GET request and return JSON response."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def make_post(url: str, headers: dict, data: dict | None = None) -> dict:
    """Make POST request and return JSON response."""
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def make_put(url: str, headers: dict, data: dict) -> dict:
    """Make PUT request and return JSON response."""
    try:
        response = requests.put(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# === GET Operations ===

def get_booking(booking_id: str, env: str = "prod") -> dict:
    """Get booking by ID or reservation number."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}")
    return make_get(url, headers)


def get_bookings(ids: str, env: str = "prod") -> dict:
    """Get multiple bookings by comma-separated IDs."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "bookings")
    return make_get(url, headers, {"ids": ids})


def get_bookings_by_user_service(user_service_id: str, env: str = "prod") -> dict:
    """Get all bookings for a user service ID."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/user_service_id/{user_service_id}")
    return make_get(url, headers)


def get_booking_status(booking_id: str, env: str = "prod") -> dict:
    """Get booking status per component."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}/status")
    return make_get(url, headers)


# === CREATE/UPDATE Operations ===

def create_booking(data: dict, env: str = "prod") -> dict:
    """Create a new booking."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "bookings")
    return make_post(url, headers, data)


def update_booking(booking_id: str, data: dict, env: str = "prod") -> dict:
    """Update an existing booking."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}")
    return make_put(url, headers, data)


def trigger_bookflow(booking_id: str, env: str = "prod") -> dict:
    """Trigger async bookflow after booking is made."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}/booked")
    return make_put(url, headers, {})


# === CANCELLATION ===

def get_cancel_info(booking_id: str, is_package: bool = False, env: str = "prod") -> dict:
    """Get cancellation information."""
    base_url = get_base_url(env)
    headers = get_headers()
    endpoint = "packages" if is_package else "bookings"
    url = urljoin(base_url, f"{endpoint}/{booking_id}/cancel")
    return make_get(url, headers)


def cancel_booking(booking_id: str, is_package: bool = False, env: str = "prod") -> dict:
    """Cancel a booking or package."""
    base_url = get_base_url(env)
    headers = get_headers()
    endpoint = "packages" if is_package else "bookings"
    url = urljoin(base_url, f"{endpoint}/{booking_id}/cancel")
    return make_post(url, headers)


# === INSURANCES ===

def get_insurance_premiums(
    booking_id: str,
    provider: str = "allianz",
    people: str | None = None,
    show_ev: bool = True,
    show_wintersports: bool = True,
    live: bool = False,
    env: str = "prod"
) -> dict:
    """Get insurance premiums for a booking."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}/insurances")

    params = {
        "provider": provider,
        "show_ev": str(show_ev).lower(),
        "show_wintersports": str(show_wintersports).lower(),
        "live": str(live).lower(),
    }
    if people:
        params["people"] = people

    return make_get(url, headers, params)


def create_insurance_policies(booking_id: str, env: str = "prod") -> dict:
    """Create insurance policies in provider's system."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}/insurances")
    return make_post(url, headers)


# === PAYMENTS ===

def get_payment_link(
    booking_id: str,
    amount: int,
    provider: str = "ogone",
    method: str | None = None,
    success_url: str | None = None,
    error_url: str | None = None,
    env: str = "prod"
) -> dict:
    """Get payment link (Ogone or Adyen)."""
    base_url = get_base_url(env)
    headers = get_headers()

    if provider == "adyen":
        if method:
            url = urljoin(base_url, f"bookings/{booking_id}/adyen_links/{amount}/{method}")
        else:
            url = urljoin(base_url, f"bookings/{booking_id}/adyen_links/{amount}")
    else:
        url = urljoin(base_url, f"bookings/{booking_id}/ogone_links/{amount}")

    params = {}
    if success_url:
        params["successurl"] = success_url
    if error_url:
        params["errorurl"] = error_url

    return make_get(url, headers, params if params else None)


# === CONFIRMATIONS ===

def send_confirmation(booking_id: str, invoice: bool = False, env: str = "prod") -> dict:
    """Send confirmation email to customer."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}/send_confirmation")

    params = {}
    if invoice:
        params["invoice"] = "true"

    return make_post(url, headers) if not params else make_post(
        f"{url}?invoice=true", headers
    )


def render_confirmation(booking_id: str, env: str = "prod") -> dict:
    """Render confirmation email without sending."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"bookings/{booking_id}/confirmation")
    return make_get(url, headers)


# === PARKING (search only, create/cancel in parking_api.py) ===

def search_parking(booking_id: str, campaign: str | None = None, env: str = "prod") -> dict:
    """Search parking offers for a booking."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"parking/{booking_id}/search")

    params = {}
    if campaign:
        params["campaign"] = campaign

    return make_get(url, headers, params if params else None)


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Booking API")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default="prod",
                        help="Environment (default: prod)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # GET booking
    get_parser = subparsers.add_parser("get", help="Get booking(s)")
    get_parser.add_argument("--id", help="Booking ID or reservation number")
    get_parser.add_argument("--ids", help="Comma-separated booking IDs")
    get_parser.add_argument("--user-service-id", help="User service UUID")

    # GET status
    status_parser = subparsers.add_parser("status", help="Get booking status")
    status_parser.add_argument("--id", required=True, help="Booking ID")

    # CREATE booking
    create_parser = subparsers.add_parser("create", help="Create booking (JSON from stdin)")

    # UPDATE booking
    update_parser = subparsers.add_parser("update", help="Update booking (JSON from stdin)")
    update_parser.add_argument("--id", required=True, help="Booking ID")

    # Trigger bookflow
    booked_parser = subparsers.add_parser("booked", help="Trigger async bookflow")
    booked_parser.add_argument("--id", required=True, help="Booking ID")

    # Cancel info
    cancel_info_parser = subparsers.add_parser("cancel-info", help="Get cancellation info")
    cancel_info_parser.add_argument("--id", help="Booking ID")
    cancel_info_parser.add_argument("--package-id", help="Package ID")

    # Cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel booking/package")
    cancel_parser.add_argument("--id", help="Booking ID")
    cancel_parser.add_argument("--package-id", help="Package ID")

    # Insurances
    ins_parser = subparsers.add_parser("insurances", help="Get insurance premiums")
    ins_parser.add_argument("--id", required=True, help="Booking ID")
    ins_parser.add_argument("--provider", choices=["allianz", "europeesche"], default="allianz")
    ins_parser.add_argument("--people", help="Comma-separated person IDs")
    ins_parser.add_argument("--no-ev", action="store_true", help="Exclude own transport types")
    ins_parser.add_argument("--no-wintersports", action="store_true", help="Exclude wintersports")
    ins_parser.add_argument("--live", action="store_true", help="Use Europeesche endpoint")

    # Create insurances
    create_ins_parser = subparsers.add_parser("create-insurances", help="Create insurance policies")
    create_ins_parser.add_argument("--id", required=True, help="Booking ID")

    # Payment link
    pay_parser = subparsers.add_parser("payment-link", help="Get payment link")
    pay_parser.add_argument("--id", required=True, help="Booking ID")
    pay_parser.add_argument("--amount", required=True, type=int, help="Amount in eurocents")
    pay_parser.add_argument("--provider", choices=["ogone", "adyen"], default="ogone")
    pay_parser.add_argument("--method", help="Payment method (Adyen only, e.g., 'all')")
    pay_parser.add_argument("--success-url", help="Redirect URL on success")
    pay_parser.add_argument("--error-url", help="Redirect URL on error")

    # Send confirmation
    send_conf_parser = subparsers.add_parser("send-confirmation", help="Send confirmation email")
    send_conf_parser.add_argument("--id", required=True, help="Booking ID")
    send_conf_parser.add_argument("--invoice", action="store_true", help="Attach invoice PDF")

    # Render confirmation
    render_conf_parser = subparsers.add_parser("render-confirmation", help="Render confirmation")
    render_conf_parser.add_argument("--id", required=True, help="Booking ID")

    # Parking search
    parking_parser = subparsers.add_parser("parking-search", help="Search parking offers")
    parking_parser.add_argument("--id", required=True, help="Booking ID")
    parking_parser.add_argument("--campaign", help="Override campaign ID")

    args = parser.parse_args()

    result = None

    if args.command == "get":
        if args.id:
            result = get_booking(args.id, args.env)
        elif args.ids:
            result = get_bookings(args.ids, args.env)
        elif args.user_service_id:
            result = get_bookings_by_user_service(args.user_service_id, args.env)
        else:
            result = {"error": "Provide --id, --ids, or --user-service-id"}

    elif args.command == "status":
        result = get_booking_status(args.id, args.env)

    elif args.command == "create":
        data = json.load(sys.stdin)
        result = create_booking(data, args.env)

    elif args.command == "update":
        data = json.load(sys.stdin)
        result = update_booking(args.id, data, args.env)

    elif args.command == "booked":
        result = trigger_bookflow(args.id, args.env)

    elif args.command == "cancel-info":
        if args.package_id:
            result = get_cancel_info(args.package_id, is_package=True, env=args.env)
        elif args.id:
            result = get_cancel_info(args.id, is_package=False, env=args.env)
        else:
            result = {"error": "Provide --id or --package-id"}

    elif args.command == "cancel":
        if args.package_id:
            result = cancel_booking(args.package_id, is_package=True, env=args.env)
        elif args.id:
            result = cancel_booking(args.id, is_package=False, env=args.env)
        else:
            result = {"error": "Provide --id or --package-id"}

    elif args.command == "insurances":
        result = get_insurance_premiums(
            args.id,
            provider=args.provider,
            people=args.people,
            show_ev=not args.no_ev,
            show_wintersports=not args.no_wintersports,
            live=args.live,
            env=args.env
        )

    elif args.command == "create-insurances":
        result = create_insurance_policies(args.id, args.env)

    elif args.command == "payment-link":
        result = get_payment_link(
            args.id,
            args.amount,
            provider=args.provider,
            method=args.method,
            success_url=args.success_url,
            error_url=args.error_url,
            env=args.env
        )

    elif args.command == "send-confirmation":
        result = send_confirmation(args.id, invoice=args.invoice, env=args.env)

    elif args.command == "render-confirmation":
        result = render_confirmation(args.id, args.env)

    elif args.command == "parking-search":
        result = search_parking(args.id, campaign=args.campaign, env=args.env)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
