#!/usr/bin/env python3
"""
Elmar Tools Content API - Read-only access to accommodations, products, geo data, images, and landing pages.
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
        "prod": "https://api.elmar.nl/tools/content/",
        "acc": "https://api.acc.elmar.nl/tools/content/",
        "dev": "http://localhost:4000/content/",
    }
    return urls.get(env, urls["prod"])


def get_headers(locale: str | None = None) -> dict:
    """Get request headers including API key and optional locale."""
    api_key = os.environ.get("ELMAR_TOOLS_API_KEY")
    if not api_key:
        print(json.dumps({"error": "ELMAR_TOOLS_API_KEY environment variable not set"}))
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}
    if locale:
        headers["Accept-Language"] = locale
    return headers


def make_request(url: str, headers: dict, params: dict | None = None) -> dict:
    """Make GET request and return JSON response."""
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def cmd_accommodations(args):
    """Handle accommodations commands."""
    base_url = get_base_url(args.env)
    headers = get_headers(args.locale)

    if args.id and args.media:
        url = urljoin(base_url, f"accommodations/{args.id}/media")
    elif args.id:
        url = urljoin(base_url, f"accommodations/{args.id}")
        params = {"replace": str(args.replace).lower()} if not args.replace else None
        result = make_request(url, headers, params)
    elif args.path:
        url = urljoin(base_url, f"accommodations/{args.path}")
        result = make_request(url, headers)
    elif args.ids:
        url = urljoin(base_url, "accommodations")
        params = {"accommodations": args.ids}
        result = make_request(url, headers, params)
    else:
        url = urljoin(base_url, "accommodations")
        result = make_request(url, headers)

    if 'result' not in locals():
        result = make_request(url, headers)

    print(json.dumps(result, indent=2))


def cmd_products(args):
    """Handle products commands."""
    base_url = get_base_url(args.env)
    headers = get_headers(args.locale)

    if args.brand and args.code:
        url = urljoin(base_url, f"products/{args.brand}/{args.code}")
        params = {}
        if args.live:
            params["live"] = "true"
        if args.departure_date:
            params["departuredate"] = args.departure_date
        result = make_request(url, headers, params if params else None)
    elif args.market:
        url = urljoin(base_url, f"products/list/{args.market}")
        result = make_request(url, headers)
    else:
        url = urljoin(base_url, "products.json")
        params = {}
        if args.brand:
            params["brand"] = args.brand
        if args.touroperator:
            params["touroperator"] = args.touroperator
        result = make_request(url, headers, params if params else None)

    print(json.dumps(result, indent=2))


def cmd_geo(args, geo_type: str):
    """Handle geo commands (airports, countries, regions, cities)."""
    base_url = get_base_url(args.env)
    headers = get_headers(args.locale)

    params = {}
    if hasattr(args, 'full') and args.full:
        params["full"] = "true"

    if hasattr(args, 'code') and args.code:
        if hasattr(args, 'id') and args.id:
            url = urljoin(base_url, f"{geo_type}/{args.code}/{args.id}")
        else:
            url = urljoin(base_url, f"{geo_type}/{args.code}")
    elif hasattr(args, 'id') and args.id:
        url = urljoin(base_url, f"{geo_type}/{args.id}")
    else:
        url = urljoin(base_url, geo_type)

    result = make_request(url, headers, params if params else None)
    print(json.dumps(result, indent=2))


def cmd_landing_pages(args):
    """Handle landing pages commands."""
    base_url = get_base_url(args.env)
    headers = get_headers(args.locale)

    if args.url:
        url = urljoin(base_url, f"landing_pages/{args.url}")
    else:
        url = urljoin(base_url, "landing_pages")

    result = make_request(url, headers)
    print(json.dumps(result, indent=2))


def cmd_marketing(args):
    """Handle marketing content commands."""
    base_url = get_base_url(args.env)
    headers = get_headers(args.locale)

    if args.all:
        url = urljoin(base_url, "marketing/accommodations/all.json")
        params = {"departuredate": args.departure_date}
        if args.boardingtype:
            params["boardingtype"] = args.boardingtype
        if args.transporttype:
            params["transporttype"] = args.transporttype
        if args.countrycode:
            params["countrycode"] = args.countrycode
    else:
        url = urljoin(base_url, "marketing/accommodations")
        params = {"url": args.accommodation_url}
        if args.type:
            params["type"] = args.type
        if args.title:
            params["title"] = args.title
        if args.flag:
            params["flag"] = args.flag
        if args.stars:
            params["stars"] = args.stars
        if args.zoover:
            params["zoover"] = args.zoover

    result = make_request(url, headers, params)
    print(json.dumps(result, indent=2))


def cmd_trust_you(args):
    """Handle Trust You mappings command."""
    base_url = get_base_url(args.env)
    headers = get_headers(args.locale)

    url = urljoin(base_url, "accommodations/trust_you_mappings")
    result = make_request(url, headers)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Content API")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default="prod",
                        help="Environment (default: prod)")
    parser.add_argument("--locale", choices=["nl", "en", "de"], default=None,
                        help="Locale for localized names")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Accommodations
    acco_parser = subparsers.add_parser("accommodations", help="Query accommodations")
    acco_parser.add_argument("--id", help="Accommodation ID")
    acco_parser.add_argument("--ids", help="Comma-separated accommodation IDs")
    acco_parser.add_argument("--path", help="URL-friendly path (country/region/city/name)")
    acco_parser.add_argument("--media", action="store_true", help="Get media for accommodation")
    acco_parser.add_argument("--replace", action="store_true", default=True,
                             help="Replace third party brand names (default: true)")
    acco_parser.set_defaults(func=cmd_accommodations)

    # Products
    prod_parser = subparsers.add_parser("products", help="Query products")
    prod_parser.add_argument("--brand", help="Tour operator brand code")
    prod_parser.add_argument("--code", help="Product code")
    prod_parser.add_argument("--touroperator", help="Filter by tour operator")
    prod_parser.add_argument("--market", help="Market code for simplified list")
    prod_parser.add_argument("--live", action="store_true", help="Refresh from tour operator")
    prod_parser.add_argument("--departure-date", help="Departure date for live descriptions")
    prod_parser.set_defaults(func=cmd_products)

    # Airports
    airports_parser = subparsers.add_parser("airports", help="Query airports")
    airports_parser.add_argument("--full", action="store_true", help="Get full details (slow)")
    airports_parser.set_defaults(func=lambda args: cmd_geo(args, "airports"))

    # Countries
    countries_parser = subparsers.add_parser("countries", help="Query countries")
    countries_parser.add_argument("--code", help="Country code (e.g., ES)")
    countries_parser.add_argument("--full", action="store_true", help="Get full details (slow)")
    countries_parser.set_defaults(func=lambda args: cmd_geo(args, "countries"))

    # Regions
    regions_parser = subparsers.add_parser("regions", help="Query regions")
    regions_parser.add_argument("--code", help="Country code")
    regions_parser.add_argument("--id", help="Region ID or URL-friendly name")
    regions_parser.add_argument("--full", action="store_true", help="Get full details (slow)")
    regions_parser.set_defaults(func=lambda args: cmd_geo(args, "regions"))

    # Cities
    cities_parser = subparsers.add_parser("cities", help="Query cities")
    cities_parser.add_argument("--code", help="Country code")
    cities_parser.add_argument("--id", help="City ID or URL-friendly name")
    cities_parser.add_argument("--full", action="store_true", help="Get full details (slow)")
    cities_parser.set_defaults(func=lambda args: cmd_geo(args, "cities"))

    # Landing pages
    lp_parser = subparsers.add_parser("landing-pages", help="Query landing pages")
    lp_parser.add_argument("--url", help="Landing page URL path")
    lp_parser.set_defaults(func=cmd_landing_pages)

    # Marketing
    mkt_parser = subparsers.add_parser("marketing", help="Query marketing content")
    mkt_parser.add_argument("--accommodation-url", help="VD website URL for accommodation")
    mkt_parser.add_argument("--all", action="store_true", help="Get all accommodations")
    mkt_parser.add_argument("--departure-date", help="Departure date (required for --all)")
    mkt_parser.add_argument("--type", choices=["small", "wide"], help="Block type")
    mkt_parser.add_argument("--title", help="Override title")
    mkt_parser.add_argument("--flag", choices=["yes", "no"], help="Show country flag")
    mkt_parser.add_argument("--stars", choices=["yes", "no"], help="Show star rating")
    mkt_parser.add_argument("--zoover", choices=["no"], help="Disable zoover score")
    mkt_parser.add_argument("--boardingtype", help="Boarding type filter")
    mkt_parser.add_argument("--transporttype", help="Transport type filter")
    mkt_parser.add_argument("--countrycode", help="Country code filter")
    mkt_parser.set_defaults(func=cmd_marketing)

    # Trust You mappings
    ty_parser = subparsers.add_parser("trust-you-mappings", help="Get Trust You ID mappings")
    ty_parser.set_defaults(func=cmd_trust_you)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
