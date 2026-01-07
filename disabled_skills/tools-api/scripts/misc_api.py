#!/usr/bin/env python3
"""
Elmar Tools Misc API - Newsletter subscription, image operations, voucher refunds.
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


# === NEWSLETTER ===

def subscribe_newsletter(
    email: str,
    firstname: str | None = None,
    surname: str | None = None,
    country: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Subscribe a customer to the VD newsletter.

    Args:
        email: Customer's email address (mandatory)
        firstname: Customer's first name (optional)
        surname: Customer's surname (optional)
        country: Customer's country code of residence (optional)
        env: Environment (prod, acc, dev)

    Returns:
        Subscription confirmation
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "newsletters/subscribe")

    params = {"email": email}
    if firstname:
        params["firstname"] = firstname
    if surname:
        params["surname"] = surname
    if country:
        params["country"] = country

    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json() if response.text else {"status": "subscribed"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# === IMAGE OPERATIONS ===

def compare_images(
    accommodation_id: str | None = None,
    limit: int | None = None,
    env: str = "prod"
) -> dict:
    """
    Run the image comparer for accommodations.

    Args:
        accommodation_id: Specific accommodation ID to compare (optional)
        limit: Number of accommodations to process if no ID specified (default 1)
        env: Environment (prod, acc, dev)

    Returns:
        Comparison results
    """
    base_url = get_base_url(env)
    headers = get_headers()

    if accommodation_id:
        url = urljoin(base_url, f"images/compare/{accommodation_id}")
        params = None
    else:
        url = urljoin(base_url, "images/compare")
        params = {"limit": limit} if limit else None

    try:
        response = requests.get(url, headers=headers, params=params, timeout=120)
        response.raise_for_status()
        return response.json() if response.text else {"status": "completed"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def sync_images(
    accommodation: str | None = None,
    async_mode: bool = False,
    clean: bool = False,
    elmarphotos: bool | None = None,
    force: bool = False,
    geonames: bool = False,
    recheck: int | None = None,
    size: str | None = None,
    touroperators: str | None = None,
    url_to_download: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Synchronize images between database and filesystem.

    Note: This needs to be run on all tools servers as processing is only local.

    Args:
        accommodation: Specific accommodation ID (use with force=True for broken images)
        async_mode: Don't block until finished (ignored for 'clean' and 'size')
        clean: Clean up old images no longer in database
        elmarphotos: True=only elmar photos, False=ignore elmar photos
        force: Redownload already downloaded images
        geonames: Only process geonames images
        recheck: Hours to recheck changed images (default 12)
        size: Reprocess all images for this size (e.g., 520)
        touroperators: Only process specific TO brands (comma-separated)
        url_to_download: Download single image URL
        env: Environment (prod, acc, dev)

    Returns:
        Sync status/results
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "images/sync")

    params = {}
    if accommodation:
        params["accommodation"] = accommodation
    if async_mode:
        params["async"] = "true"
    if clean:
        params["clean"] = "true"
    if elmarphotos is not None:
        params["elmarphotos"] = str(elmarphotos).lower()
    if force:
        params["force"] = "true"
    if geonames:
        params["geonames"] = "true"
    if recheck:
        params["recheck"] = str(recheck)
    if size:
        params["size"] = size
    if touroperators:
        params["touroperators"] = touroperators
    if url_to_download:
        params["url"] = url_to_download

    try:
        response = requests.get(url, headers=headers, params=params if params else None, timeout=300)
        response.raise_for_status()
        return response.json() if response.text else {"status": "completed"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# === VOUCHER REFUND ===

def convert_voucher_to_refund(
    voucher_code: str,
    iban: str | None = None,
    bank_name: str | None = None,
    env: str = "prod"
) -> dict:
    """
    Convert a voucher to a refund.

    Args:
        voucher_code: Voucher code to convert
        iban: Bank account IBAN (if needed, 409 error indicates this is required)
        bank_name: Name on bank account (optional, auto-determined if not specified)
        env: Environment (prod, acc, dev)

    Returns:
        Refund details

    Notes:
        - Either an IBAN or a preexisting non-iDEAL Ogone/Adyen payment is required
        - If neither can be found, a 409 error is returned and the request can be
          retried with a specified IBAN
    """
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"vouchers/{voucher_code}/refund")

    data = {}
    if iban:
        data["iban"] = iban
    if bank_name:
        data["bank_name"] = bank_name

    try:
        response = requests.post(url, headers=headers, json=data if data else None, timeout=30)
        response.raise_for_status()
        return response.json() if response.text else {"status": "refund_created"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            return {
                "error": "No valid payment method found. Provide an IBAN.",
                "status_code": 409
            }
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Misc API")
    default_env = os.environ.get("ELMAR_TOOLS_API_ENV", "prod")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default=default_env,
                        help=f"Environment (default: {default_env})")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Newsletter subscribe
    news_parser = subparsers.add_parser("newsletter-subscribe", help="Subscribe to newsletter")
    news_parser.add_argument("--email", required=True, help="Email address")
    news_parser.add_argument("--firstname", help="First name")
    news_parser.add_argument("--surname", help="Surname")
    news_parser.add_argument("--country", help="Country code")

    # Image compare
    compare_parser = subparsers.add_parser("image-compare", help="Run image comparer")
    compare_parser.add_argument("--accommodation-id", help="Specific accommodation ID")
    compare_parser.add_argument("--limit", type=int, help="Number of accommodations (default 1)")

    # Image sync
    sync_parser = subparsers.add_parser("image-sync", help="Synchronize images")
    sync_parser.add_argument("--accommodation", help="Specific accommodation ID")
    sync_parser.add_argument("--async", dest="async_mode", action="store_true",
                             help="Don't wait for completion")
    sync_parser.add_argument("--clean", action="store_true", help="Clean up old images")
    sync_parser.add_argument("--elmarphotos", choices=["true", "false"],
                             help="Filter elmar photos")
    sync_parser.add_argument("--force", action="store_true", help="Force redownload")
    sync_parser.add_argument("--geonames", action="store_true", help="Only geonames images")
    sync_parser.add_argument("--recheck", type=int, help="Recheck hours (default 12)")
    sync_parser.add_argument("--size", help="Reprocess for size (e.g., 520)")
    sync_parser.add_argument("--touroperators", help="TO brands (comma-separated)")
    sync_parser.add_argument("--url", help="Single image URL to download")

    # Voucher refund
    refund_parser = subparsers.add_parser("voucher-refund", help="Convert voucher to refund")
    refund_parser.add_argument("--code", required=True, help="Voucher code")
    refund_parser.add_argument("--iban", help="Bank account IBAN")
    refund_parser.add_argument("--bank-name", help="Name on bank account")

    args = parser.parse_args()

    if args.command == "newsletter-subscribe":
        result = subscribe_newsletter(
            email=args.email,
            firstname=args.firstname,
            surname=args.surname,
            country=args.country,
            env=args.env
        )

    elif args.command == "image-compare":
        result = compare_images(
            accommodation_id=args.accommodation_id,
            limit=args.limit,
            env=args.env
        )

    elif args.command == "image-sync":
        elmarphotos = None
        if hasattr(args, 'elmarphotos') and args.elmarphotos:
            elmarphotos = args.elmarphotos == "true"

        result = sync_images(
            accommodation=args.accommodation,
            async_mode=args.async_mode,
            clean=args.clean,
            elmarphotos=elmarphotos,
            force=args.force,
            geonames=args.geonames,
            recheck=args.recheck,
            size=args.size,
            touroperators=args.touroperators,
            url_to_download=args.url,
            env=args.env
        )

    elif args.command == "voucher-refund":
        result = convert_voucher_to_refund(
            voucher_code=args.code,
            iban=args.iban,
            bank_name=args.bank_name,
            env=args.env
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
