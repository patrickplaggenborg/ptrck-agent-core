---
name: tools-api
description: Full CRUD access to Elmar Tools API. Use this skill when users need to create, update, or cancel bookings, car rentals, parking reservations, or perform other write operations. Also includes all read operations. For read-only access (safer, no modifications), use tools-api-readonly instead.
---

# Elmar Tools API (Full CRUD)

Full access to the Elmar Tools API including all read operations plus create, update, and delete capabilities for bookings, car rentals, parking, and more.

## Prerequisites

Set the `ELMAR_TOOLS_API_KEY` environment variable with your API key.

```bash
export ELMAR_TOOLS_API_KEY="your-api-key"
```

## Environment

- **Production**: `https://api.elmar.nl/tools/`
- **Acceptance**: `https://api.acc.elmar.nl/tools/`

Use `--env acc` to target acceptance environment.

## Read-Only Scripts

These scripts are identical to those in `tools-api-readonly`:

- `content_api.py` - Accommodations, products, geo data, images, landing pages
- `customer_api.py` - Customer lookup
- `baggage_api.py` - Baggage allowance info
- `transfer_api.py` - Transfer inclusion checks
- `hotels_api.py` - Hotel offers for bookings
- `lookup_api.py` - Refunds, vouchers, tour operators, recommendations

See `tools-api-readonly` skill documentation for usage details on these scripts.

---

## CRUD Scripts

### Booking API (`booking_api.py`)

Full CRUD operations for bookings, including insurances, payments, and confirmation emails.

```bash
# Get booking by ID or reservation number
python booking_api.py get --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8
python booking_api.py get --id V140049277

# Get multiple bookings
python booking_api.py get --ids ae817a96-a75f-4051-82cc-092989745815,b43c9fcf-aa1a-4044-be44-0016594d4324

# Get bookings by user service ID
python booking_api.py get --user-service-id 70a1bd61-8261-4526-a813-2d84f27352ae

# Get booking status
python booking_api.py status --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8

# Create booking (JSON from stdin)
cat booking.json | python booking_api.py create

# Update booking
cat updates.json | python booking_api.py update --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8

# Trigger async bookflow
python booking_api.py booked --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8

# Get cancellation info
python booking_api.py cancel-info --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8

# Cancel booking/package
python booking_api.py cancel --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8
python booking_api.py cancel --package-id <package-uuid>

# Get insurance premiums
python booking_api.py insurances --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8
python booking_api.py insurances --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8 --provider allianz

# Create insurance policies
python booking_api.py create-insurances --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8

# Get payment links
python booking_api.py payment-link --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8 \
  --amount 50000 --provider ogone
python booking_api.py payment-link --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8 \
  --amount 50000 --provider adyen --method all

# Send confirmation email
python booking_api.py send-confirmation --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8
python booking_api.py send-confirmation --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8 --invoice

# Render confirmation (without sending)
python booking_api.py render-confirmation --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8

# Get parking offers for booking
python booking_api.py parking-search --id 2fd6c830-1398-11e5-93ff-bc305bedc3f8
```

### Car Rental API (`carrental_api.py`)

Search and manage car rental reservations.

```bash
# Search locations
python carrental_api.py airports
python carrental_api.py airports --country NL
python carrental_api.py airports --code AMS
python carrental_api.py airports --code AMS --regions
python carrental_api.py airports --code AMS --locations

python carrental_api.py countries
python carrental_api.py countries --code NL
python carrental_api.py countries --code NL --airports
python carrental_api.py countries --code NL --regions
python carrental_api.py countries --code NL --locations

python carrental_api.py regions --name Amsterdam
python carrental_api.py regions --name Amsterdam --country NL

# Search vehicles
python carrental_api.py vehicles --airport AMS \
  --departure-date 2024-06-01 --return-date 2024-06-08
python carrental_api.py vehicles --region 1234 \
  --departure-date 2024-06-01 --return-date 2024-06-08 \
  --airco --automatic

# Different pickup/dropoff
python carrental_api.py vehicles --airport-pickup AMS --airport-dropoff RTM \
  --departure-date 2024-06-01 --return-date 2024-06-08

# Find vehicle location
python carrental_api.py location --airport AMS --vehicle 12345 --servicetype 151
python carrental_api.py location --region 1234 --vehicle 12345 --servicetype 151

# Get accessories for a location
python carrental_api.py accessories --location 59578 \
  --departure-date 2024-06-01 --return-date 2024-06-08

# Vehicle info
python carrental_api.py vehicle-builds
python carrental_api.py vehicle-features
python carrental_api.py vehicle-services
python carrental_api.py vehicle-servicetypes
python carrental_api.py vehicle-servicetypes --id 151
python carrental_api.py vehicle-types

# Simplified search (by booking)
python carrental_api.py search --booking-id 015d54d2-ed6d-4798-925c-0edbd84d8aac
python carrental_api.py search --system mobis --booking-id VTN-1424782
python carrental_api.py search --booking-id 015d54d2-ed6d-4798-925c-0edbd84d8aac --type airport

# Create reservation (via booking API)
python carrental_api.py book --booking-id 015d54d2-ed6d-4798-925c-0edbd84d8aac

# Create direct reservation
python carrental_api.py reserve --booking 015d54d2-ed6d-4798-925c-0edbd84d8aac \
  --location 59578 --meeting airport --servicetype 151 --vehicle 12345

# Get reservation info
python carrental_api.py reservation --id 12345

# List reservations
python carrental_api.py reservations
python carrental_api.py reservations --status confirmed
python carrental_api.py reservations --name Smith
python carrental_api.py reservations --after-date 2024-06-01 --before-date 2024-12-31

# Cancel reservation
python carrental_api.py cancel-reservation --id 12345

# Update reservation from provider
python carrental_api.py update-reservation --id 12345
```

### Parking API (`parking_api.py`)

Search and manage parking reservations.

```bash
# Search parking offers
python parking_api.py search --booking-id 3cc41650-ddcf-11e4-9ae3-bc305bedc3f8
python parking_api.py search --booking-id 3cc41650-ddcf-11e4-9ae3-bc305bedc3f8 --campaign SUMMER2024

# Create parking reservation
python parking_api.py create --booking-id 3cc41650-ddcf-11e4-9ae3-bc305bedc3f8 \
  --provider 123 --license-plate AA-11-BB

# With optional fields
python parking_api.py create --booking-id 3cc41650-ddcf-11e4-9ae3-bc305bedc3f8 \
  --provider 123 --license-plate AA-11-BB \
  --comment "Please park near elevator" --card 1234-5678-8765-4321

# Cancel parking reservation
python parking_api.py cancel --booking-id 3cc41650-ddcf-11e4-9ae3-bc305bedc3f8
```

### Misc API (`misc_api.py`)

Newsletter subscription, image operations, voucher refunds.

```bash
# Subscribe to newsletter
python misc_api.py newsletter-subscribe --email customer@example.com
python misc_api.py newsletter-subscribe --email customer@example.com \
  --firstname John --surname Doe --country NL

# Image comparison
python misc_api.py image-compare --accommodation-id 143d2940-8f5c-11df-a2df-001c42000009
python misc_api.py image-compare --limit 10

# Image sync (runs locally on tools servers)
python misc_api.py image-sync
python misc_api.py image-sync --accommodation 143d2940-8f5c-11df-a2df-001c42000009 --force
python misc_api.py image-sync --clean
python misc_api.py image-sync --size 520
python misc_api.py image-sync --touroperators HI
python misc_api.py image-sync --url "https://example.com/image.jpg"

# Convert voucher to refund
python misc_api.py voucher-refund --code 714277B2
python misc_api.py voucher-refund --code 714277B2 --iban NL91ABNA0417164300 --bank-name "John Doe"
```

---

## Booking JSON Structure

When creating or updating bookings, use the following JSON structure:

```json
{
    "id": "710ff857-327f-40b1-ad2b-828a676b8476",
    "label": "vd",
    "status": "pending",
    "customer_comments": "test booking",
    "user_service_id": "70a1bd61-8261-4526-a813-2d84f27352ae",
    "packages": [...],
    "travelparty": [...],
    "customer": {...},
    "emergency_contact": {...},
    "priceitems": [...],
    "insurances": [...],
    "rental_cars": [...],
    "parking": [...],
    "surcharges": [...],
    "paid": [...],
    "messages": [...],
    "g7": [...],
    "vto": {...}
}
```

See the API documentation for full field descriptions.

## Booking Statuses

| Status | Meaning |
|--------|---------|
| new | Unfinished booking (Booking Admin) |
| pending | Customer in booking steps |
| processing | Customer on external payment form |
| finalizing | Booking process finished, being booked at TO |
| confirmed | Successfully completed |
| option | Confirmed but in option status |
| onrequest | On request at tour operator |
| cancelled | Booking was cancelled |
| exception | Technical error, manual action needed |

## Error Handling

- **401**: Invalid or missing API key
- **403**: API key not authorized for this endpoint
- **404**: Resource not found
- **409**: Conflict (e.g., voucher refund without valid payment)
- **422**: Processing error (e.g., cancellation failed)

## For Read-Only Access

If you only need read operations and want to avoid accidental modifications, use the `tools-api-readonly` skill instead.
