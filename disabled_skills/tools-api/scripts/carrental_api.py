#!/usr/bin/env python3
"""
Elmar Tools Car Rental API - Search and manage car rental reservations.
Supports Sunny Cars (full) and Rentalcars (search only).
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
        "prod": "https://api.elmar.nl/tools/carrental/",
        "acc": "https://api.acc.elmar.nl/tools/carrental/",
        "dev": "http://localhost:4000/carrental/",
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
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def make_post(url: str, headers: dict, params: dict | None = None) -> dict:
    """Make POST request and return JSON response."""
    try:
        response = requests.post(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "status_code": e.response.status_code}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# === AIRPORTS ===

def get_airports(country: str | None = None, env: str = "prod") -> dict:
    """Get list of airports."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "airports")
    params = {"country": country} if country else None
    return make_get(url, headers, params)


def get_airport(code: str, env: str = "prod") -> dict:
    """Get single airport by IATA code."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"airports/{code}")
    return make_get(url, headers)


def get_airport_regions(code: str, env: str = "prod") -> dict:
    """Get regions for an airport."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"airports/{code}/regions")
    return make_get(url, headers)


def get_airport_locations(code: str, env: str = "prod") -> dict:
    """Get locations for an airport."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"airports/{code}/locations")
    return make_get(url, headers)


# === COUNTRIES ===

def get_countries(env: str = "prod") -> dict:
    """Get list of countries."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "countries")
    return make_get(url, headers)


def get_country(code: str, env: str = "prod") -> dict:
    """Get single country."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"countries/{code}")
    return make_get(url, headers)


def get_country_airports(code: str, env: str = "prod") -> dict:
    """Get airports in a country."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"countries/{code}/airports")
    return make_get(url, headers)


def get_country_regions(code: str, env: str = "prod") -> dict:
    """Get regions in a country."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"countries/{code}/regions")
    return make_get(url, headers)


def get_country_locations(code: str, env: str = "prod") -> dict:
    """Get locations in a country."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"countries/{code}/locations")
    return make_get(url, headers)


# === REGIONS ===

def search_regions(name: str, country: str | None = None, env: str = "prod") -> dict:
    """Search regions by name."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "regions")
    params = {"name": name}
    if country:
        params["country"] = country
    return make_get(url, headers, params)


# === VEHICLES ===

def search_vehicles(
    departure_date: str,
    return_date: str,
    airport: str | None = None,
    airport_pickup: str | None = None,
    airport_dropoff: str | None = None,
    region: str | None = None,
    region_pickup: str | None = None,
    region_dropoff: str | None = None,
    location: str | None = None,
    location_pickup: str | None = None,
    location_dropoff: str | None = None,
    departure_time: str | None = None,
    return_time: str | None = None,
    meeting: str | None = None,
    airco: bool = False,
    automatic: bool = False,
    vehicle_type: str | None = None,
    provider: str | None = None,
    env: str = "prod"
) -> dict:
    """Search for vehicles."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "vehicles")

    params = {
        "departuredate": departure_date,
        "returndate": return_date,
    }

    # Location params
    if airport:
        params["airport"] = airport
    if airport_pickup:
        params["airport_pickup"] = airport_pickup
    if airport_dropoff:
        params["airport_dropoff"] = airport_dropoff
    if region:
        params["region"] = region
    if region_pickup:
        params["region_pickup"] = region_pickup
    if region_dropoff:
        params["region_dropoff"] = region_dropoff
    if location:
        params["location"] = location
    if location_pickup:
        params["location_pickup"] = location_pickup
    if location_dropoff:
        params["location_dropoff"] = location_dropoff

    # Optional params
    if departure_time:
        params["departuretime"] = departure_time
    if return_time:
        params["returntime"] = return_time
    if meeting:
        params["meeting"] = meeting
    if airco:
        params["airco"] = "true"
    if automatic:
        params["automatic"] = "true"
    if vehicle_type:
        params["type"] = vehicle_type
    if provider:
        params["provider"] = provider

    return make_get(url, headers, params)


def get_vehicle_location(
    vehicle_id: str,
    servicetype: str,
    airport: str | None = None,
    region: str | None = None,
    env: str = "prod"
) -> dict:
    """Find location of a specific vehicle."""
    base_url = get_base_url(env)
    headers = get_headers()

    if airport:
        url = urljoin(base_url, f"airports/{airport}/vehicles/{vehicle_id}/locations/{servicetype}")
    elif region:
        url = urljoin(base_url, f"regions/{region}/vehicles/{vehicle_id}/locations/{servicetype}")
    else:
        url = urljoin(base_url, "locations")
        params = {"vehicle": vehicle_id, "servicetype": servicetype}
        if airport:
            params["airport"] = airport
        if region:
            params["region"] = region
        return make_get(url, headers, params)

    return make_get(url, headers)


# === ACCESSORIES ===

def get_accessories(location_id: str, departure_date: str, return_date: str, env: str = "prod") -> dict:
    """Get accessories available at a location."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"locations/{location_id}/accessories")
    params = {"departuredate": departure_date, "returndate": return_date}
    return make_get(url, headers, params)


# === VEHICLE INFO ===

def get_vehicle_builds(env: str = "prod") -> dict:
    """Get list of vehicle builds (standard, SUV, etc)."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "vehicles/builds")
    return make_get(url, headers)


def get_vehicle_features(env: str = "prod") -> dict:
    """Get list of vehicle features (4WD, GPS, etc)."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "vehicles/features")
    return make_get(url, headers)


def get_vehicle_services(env: str = "prod") -> dict:
    """Get list of services (fuel policies, insurance, etc)."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "vehicles/services")
    return make_get(url, headers)


def get_vehicle_servicetypes(servicetype_id: str | None = None, env: str = "prod") -> dict:
    """Get servicetypes and what's included."""
    base_url = get_base_url(env)
    headers = get_headers()
    if servicetype_id:
        url = urljoin(base_url, f"vehicles/servicetypes/{servicetype_id}")
    else:
        url = urljoin(base_url, "vehicles/servicetypes")
    return make_get(url, headers)


def get_vehicle_types(env: str = "prod") -> dict:
    """Get list of vehicle types (small car, minivan, etc)."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "vehicles/types")
    return make_get(url, headers)


# === SIMPLIFIED SEARCH ===

def simple_search(
    booking_id: str,
    system: str | None = None,
    meeting_type: str | None = None,
    env: str = "prod"
) -> dict:
    """Simplified search by booking ID."""
    base_url = get_base_url(env)
    headers = get_headers()

    if system and meeting_type:
        url = urljoin(base_url, f"search/{system}/{booking_id}/{meeting_type}")
    elif system:
        url = urljoin(base_url, f"search/{system}/{booking_id}")
    elif meeting_type:
        url = urljoin(base_url, f"search/{booking_id}/{meeting_type}")
    else:
        url = urljoin(base_url, f"search/{booking_id}")

    return make_get(url, headers)


# === RESERVATIONS ===

def book_via_booking_api(booking_id: str, env: str = "prod") -> dict:
    """Book cars registered in a booking via booking API."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"reservations/book/{booking_id}")
    return make_post(url, headers)


def create_reservation(
    booking: str,
    location: str,
    meeting: str,
    servicetype: str,
    vehicle: str | None = None,
    location_pickup: str | None = None,
    location_dropoff: str | None = None,
    meeting_pickup: str | None = None,
    meeting_dropoff: str | None = None,
    meetinginfo: str | None = None,
    meetinginfo_pickup: str | None = None,
    meetinginfo_dropoff: str | None = None,
    departure_date: str | None = None,
    departure_time: str | None = None,
    return_date: str | None = None,
    return_time: str | None = None,
    driver: str | None = None,
    user: str | None = None,
    flexservice: bool = False,
    accessories: str | None = None,
    check: bool = False,
    env: str = "prod"
) -> dict:
    """Create a direct reservation."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "reservations")

    params = {
        "booking": booking,
        "location": location,
        "meeting": meeting,
        "servicetype": servicetype,
    }

    if vehicle:
        params["vehicle"] = vehicle
    if location_pickup:
        params["location_pickup"] = location_pickup
    if location_dropoff:
        params["location_dropoff"] = location_dropoff
    if meeting_pickup:
        params["meeting_pickup"] = meeting_pickup
    if meeting_dropoff:
        params["meeting_dropoff"] = meeting_dropoff
    if meetinginfo:
        params["meetinginfo"] = meetinginfo
    if meetinginfo_pickup:
        params["meetinginfo_pickup"] = meetinginfo_pickup
    if meetinginfo_dropoff:
        params["meetinginfo_dropoff"] = meetinginfo_dropoff
    if departure_date:
        params["departuredate"] = departure_date
    if departure_time:
        params["departuretime"] = departure_time
    if return_date:
        params["returndate"] = return_date
    if return_time:
        params["returntime"] = return_time
    if driver:
        params["driver"] = driver
    if user:
        params["user"] = user
    if flexservice:
        params["flexservice"] = "true"
    if accessories:
        params["accessories"] = accessories
    if check:
        params["check"] = "true"

    return make_post(url, headers, params)


def get_reservation(reservation_id: str, env: str = "prod") -> dict:
    """Get reservation information."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"reservations/{reservation_id}")
    return make_get(url, headers)


def list_reservations(
    status: str | None = None,
    name: str | None = None,
    reservation_number: str | None = None,
    after_date: str | None = None,
    before_date: str | None = None,
    env: str = "prod"
) -> dict:
    """List reservations with optional filters."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, "reservations")

    params = {}
    if status:
        params["status"] = status
    if name:
        params["name"] = name
    if reservation_number:
        params["reservation_number"] = reservation_number
    if after_date:
        params["after_date"] = after_date
    if before_date:
        params["before_date"] = before_date

    return make_get(url, headers, params if params else None)


def cancel_reservation(reservation_id: str, env: str = "prod") -> dict:
    """Cancel a reservation."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"reservations/{reservation_id}/cancel")
    return make_post(url, headers)


def update_reservation(reservation_id: str, env: str = "prod") -> dict:
    """Update reservation from rental company."""
    base_url = get_base_url(env)
    headers = get_headers()
    url = urljoin(base_url, f"reservations/{reservation_id}/update")
    return make_post(url, headers)


def main():
    parser = argparse.ArgumentParser(description="Elmar Tools Car Rental API")
    default_env = os.environ.get("ELMAR_TOOLS_API_ENV", "prod")
    parser.add_argument("--env", choices=["prod", "acc", "dev"], default=default_env,
                        help=f"Environment (default: {default_env})")
    parser.add_argument("--locale", choices=["nl", "en", "de"],
                        help="Language for localized content")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Airports
    airports_p = subparsers.add_parser("airports", help="Query airports")
    airports_p.add_argument("--country", help="Filter by country code")
    airports_p.add_argument("--code", help="Get single airport by IATA code")
    airports_p.add_argument("--regions", action="store_true", help="Get regions for airport")
    airports_p.add_argument("--locations", action="store_true", help="Get locations for airport")

    # Countries
    countries_p = subparsers.add_parser("countries", help="Query countries")
    countries_p.add_argument("--code", help="Country code")
    countries_p.add_argument("--airports", action="store_true", help="Get airports in country")
    countries_p.add_argument("--regions", action="store_true", help="Get regions in country")
    countries_p.add_argument("--locations", action="store_true", help="Get locations in country")

    # Regions
    regions_p = subparsers.add_parser("regions", help="Search regions")
    regions_p.add_argument("--name", required=True, help="Search by name")
    regions_p.add_argument("--country", help="Filter by country code")

    # Vehicles
    vehicles_p = subparsers.add_parser("vehicles", help="Search vehicles")
    vehicles_p.add_argument("--departure-date", required=True, help="Pickup date (yyyy-mm-dd)")
    vehicles_p.add_argument("--return-date", required=True, help="Return date (yyyy-mm-dd)")
    vehicles_p.add_argument("--airport", help="Airport code")
    vehicles_p.add_argument("--airport-pickup", help="Pickup airport code")
    vehicles_p.add_argument("--airport-dropoff", help="Dropoff airport code")
    vehicles_p.add_argument("--region", help="Region ID")
    vehicles_p.add_argument("--location", help="Location ID")
    vehicles_p.add_argument("--departure-time", help="Pickup time (HH:MM)")
    vehicles_p.add_argument("--return-time", help="Return time (HH:MM)")
    vehicles_p.add_argument("--meeting", choices=["airport", "address", "counter"])
    vehicles_p.add_argument("--airco", action="store_true", help="Require airconditioning")
    vehicles_p.add_argument("--automatic", action="store_true", help="Require automatic transmission")
    vehicles_p.add_argument("--type", help="Vehicle type ID")
    vehicles_p.add_argument("--provider", choices=["sunny_cars", "rentalcars"])

    # Location
    location_p = subparsers.add_parser("location", help="Find vehicle location")
    location_p.add_argument("--vehicle", required=True, help="Vehicle ID")
    location_p.add_argument("--servicetype", required=True, help="Service type ID")
    location_p.add_argument("--airport", help="Airport code")
    location_p.add_argument("--region", help="Region ID")

    # Accessories
    acc_p = subparsers.add_parser("accessories", help="Get location accessories")
    acc_p.add_argument("--location", required=True, help="Location ID")
    acc_p.add_argument("--departure-date", required=True, help="Pickup date")
    acc_p.add_argument("--return-date", required=True, help="Return date")

    # Vehicle info commands
    subparsers.add_parser("vehicle-builds", help="Get vehicle builds")
    subparsers.add_parser("vehicle-features", help="Get vehicle features")
    subparsers.add_parser("vehicle-services", help="Get vehicle services")

    st_p = subparsers.add_parser("vehicle-servicetypes", help="Get servicetypes")
    st_p.add_argument("--id", help="Servicetype ID")

    subparsers.add_parser("vehicle-types", help="Get vehicle types")

    # Simple search
    search_p = subparsers.add_parser("search", help="Simplified search by booking")
    search_p.add_argument("--booking-id", required=True, help="Booking ID")
    search_p.add_argument("--system", help="External system (zeus, mobis, flygstolen)")
    search_p.add_argument("--type", choices=["airport", "counter", "address"])

    # Book via booking API
    book_p = subparsers.add_parser("book", help="Book cars via booking API")
    book_p.add_argument("--booking-id", required=True, help="Booking ID")

    # Create reservation
    reserve_p = subparsers.add_parser("reserve", help="Create direct reservation")
    reserve_p.add_argument("--booking", required=True, help="Booking ID")
    reserve_p.add_argument("--location", required=True, help="Location ID")
    reserve_p.add_argument("--meeting", required=True, choices=["airport", "address", "counter"])
    reserve_p.add_argument("--servicetype", required=True, help="Servicetype ID")
    reserve_p.add_argument("--vehicle", help="Vehicle ID")
    reserve_p.add_argument("--departure-date", help="Pickup date")
    reserve_p.add_argument("--departure-time", help="Pickup time")
    reserve_p.add_argument("--return-date", help="Return date")
    reserve_p.add_argument("--return-time", help="Return time")
    reserve_p.add_argument("--driver", help="Driver person ID")
    reserve_p.add_argument("--user", help="User ID making reservation")
    reserve_p.add_argument("--flexservice", action="store_true", help="Add flex service")
    reserve_p.add_argument("--accessories", help="Comma-separated accessory IDs")
    reserve_p.add_argument("--check", action="store_true", help="Check only, don't book")

    # Get reservation
    res_p = subparsers.add_parser("reservation", help="Get reservation info")
    res_p.add_argument("--id", required=True, help="Reservation ID")

    # List reservations
    list_p = subparsers.add_parser("reservations", help="List reservations")
    list_p.add_argument("--status", choices=["confirmed", "requested", "cancelled"])
    list_p.add_argument("--name", help="Search by driver surname")
    list_p.add_argument("--reservation-number", help="Reservation number")
    list_p.add_argument("--after-date", help="Pickup date after (yyyy-mm-dd)")
    list_p.add_argument("--before-date", help="Dropoff date before (yyyy-mm-dd)")

    # Cancel reservation
    cancel_p = subparsers.add_parser("cancel-reservation", help="Cancel reservation")
    cancel_p.add_argument("--id", required=True, help="Reservation ID")

    # Update reservation
    update_p = subparsers.add_parser("update-reservation", help="Update from provider")
    update_p.add_argument("--id", required=True, help="Reservation ID")

    args = parser.parse_args()

    result = None

    if args.command == "airports":
        if args.code:
            if args.regions:
                result = get_airport_regions(args.code, args.env)
            elif args.locations:
                result = get_airport_locations(args.code, args.env)
            else:
                result = get_airport(args.code, args.env)
        else:
            result = get_airports(args.country, args.env)

    elif args.command == "countries":
        if args.code:
            if args.airports:
                result = get_country_airports(args.code, args.env)
            elif args.regions:
                result = get_country_regions(args.code, args.env)
            elif args.locations:
                result = get_country_locations(args.code, args.env)
            else:
                result = get_country(args.code, args.env)
        else:
            result = get_countries(args.env)

    elif args.command == "regions":
        result = search_regions(args.name, args.country, args.env)

    elif args.command == "vehicles":
        result = search_vehicles(
            departure_date=args.departure_date,
            return_date=args.return_date,
            airport=args.airport,
            airport_pickup=args.airport_pickup,
            airport_dropoff=args.airport_dropoff,
            region=args.region,
            location=args.location,
            departure_time=args.departure_time,
            return_time=args.return_time,
            meeting=args.meeting,
            airco=args.airco,
            automatic=args.automatic,
            vehicle_type=args.type,
            provider=args.provider,
            env=args.env
        )

    elif args.command == "location":
        result = get_vehicle_location(
            args.vehicle,
            args.servicetype,
            airport=args.airport,
            region=args.region,
            env=args.env
        )

    elif args.command == "accessories":
        result = get_accessories(
            args.location,
            args.departure_date,
            args.return_date,
            args.env
        )

    elif args.command == "vehicle-builds":
        result = get_vehicle_builds(args.env)

    elif args.command == "vehicle-features":
        result = get_vehicle_features(args.env)

    elif args.command == "vehicle-services":
        result = get_vehicle_services(args.env)

    elif args.command == "vehicle-servicetypes":
        result = get_vehicle_servicetypes(args.id, args.env)

    elif args.command == "vehicle-types":
        result = get_vehicle_types(args.env)

    elif args.command == "search":
        result = simple_search(
            args.booking_id,
            system=args.system,
            meeting_type=args.type,
            env=args.env
        )

    elif args.command == "book":
        result = book_via_booking_api(args.booking_id, args.env)

    elif args.command == "reserve":
        result = create_reservation(
            booking=args.booking,
            location=args.location,
            meeting=args.meeting,
            servicetype=args.servicetype,
            vehicle=args.vehicle,
            departure_date=args.departure_date,
            departure_time=args.departure_time,
            return_date=args.return_date,
            return_time=args.return_time,
            driver=args.driver,
            user=args.user,
            flexservice=args.flexservice,
            accessories=args.accessories,
            check=args.check,
            env=args.env
        )

    elif args.command == "reservation":
        result = get_reservation(args.id, args.env)

    elif args.command == "reservations":
        result = list_reservations(
            status=args.status,
            name=args.name,
            reservation_number=args.reservation_number,
            after_date=args.after_date,
            before_date=args.before_date,
            env=args.env
        )

    elif args.command == "cancel-reservation":
        result = cancel_reservation(args.id, args.env)

    elif args.command == "update-reservation":
        result = update_reservation(args.id, args.env)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
