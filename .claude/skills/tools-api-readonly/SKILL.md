---
name: tools-api-readonly
description: Read-only access to Elmar Tools API. Provides search and view operations only - no modifications. Use this skill when users need to query the Tools API like "get accommodation details", "lookup customer info", "check baggage allowance", or "find hotel offers for a booking". For write operations (create bookings, reservations, cancellations), use the tools-api skill instead.
---

# Elmar Tools API (Read-Only)

Read-only access to the Elmar Tools API for querying accommodations, products, customers, baggage, transfers, hotels, and lookups.

## Prerequisites

Set the `ELMAR_TOOLS_API_KEY` environment variable with your API key.

```bash
export ELMAR_TOOLS_API_KEY="your-api-key"
```

## Environment

- **Production**: `https://api.elmar.nl/tools/`
- **Acceptance**: `https://api.acc.elmar.nl/tools/`

Use `--env acc` to target acceptance environment.

## Available Scripts

### Content API (`content_api.py`)

Query accommodations, products, geo data, images, and landing pages.

```bash
# List all accommodations (simplified)
python content_api.py accommodations

# Get single accommodation by ID
python content_api.py accommodations --id 143d2940-8f5c-11df-a2df-001c42000009

# Get accommodation by URL path
python content_api.py accommodations --path turkije/antalya/alanya/eftalia_aytur_hotel

# Get accommodation media
python content_api.py accommodations --id 13cf9a60-8f5c-11df-a2df-001c42000009 --media

# List products
python content_api.py products --brand SA

# Get single product
python content_api.py products --brand AL --code VLVARVAR806

# Geo data
python content_api.py airports
python content_api.py countries
python content_api.py countries --code ES
python content_api.py regions
python content_api.py regions --code ES --id tenerife
python content_api.py cities
python content_api.py cities --code ES --id madrid

# Landing pages
python content_api.py landing-pages
python content_api.py landing-pages --url turkije

# Set locale for localized names
python content_api.py countries --locale de
```

### Customer API (`customer_api.py`)

Lookup customer information.

```bash
# Get customer by database ID
python customer_api.py --id a3770c94-cec8-49a8-b16f-76747fa18aff

# Get customer by customer number
python customer_api.py --id C001219087
```

### Baggage API (`baggage_api.py`)

Check baggage allowances.

```bash
# Check hold baggage
python baggage_api.py hold --brand TC --carrier KL --origin AMS --destination JFK \
  --departure 2024-01-01 --arrival 2024-01-02

# Check hand baggage
python baggage_api.py hand --carrier HV

# With optional brand
python baggage_api.py hand --carrier HV --brand AR
```

### Transfer API (`transfer_api.py`)

Check transfer inclusion for products.

```bash
# Check single product
python transfer_api.py --brand AL --product VLVARVAR105

# Check multiple products
python transfer_api.py --products VLVARVAR105.AL,VLVARVAR106.A1

# With departure date for temporal rules
python transfer_api.py --brand AL --product VLVARVAR105 --departure-date 2024-06-15
```

### Hotels API (`hotels_api.py`)

Get hotel offers for bookings.

```bash
# Get hotels for a booking
python hotels_api.py --booking-id f0902d81-a42a-4f14-9828-48a61fe2b56f

# Get hotels from external system
python hotels_api.py --system zeus --booking-id 4729252
```

### Lookup API (`lookup_api.py`)

Lookup refunds, vouchers, tour operators, and recommendations.

```bash
# Get refund details
python lookup_api.py refunds --id 1961

# Get refunds by user service ID
python lookup_api.py refunds --user-service-id 698cbcc9-dcdf-4b41-8673-9a25eee61045

# Get voucher details
python lookup_api.py vouchers --code 714277B2

# Get vouchers by user service ID
python lookup_api.py vouchers --user-service-id 698cbcc9-dcdf-4b41-8673-9a25eee61045

# Get tour operator configuration
python lookup_api.py touroperators

# Get recommendations for a booking
python lookup_api.py recommend --booking-id 3cc41650-ddcf-11e4-9ae3-bc305bedc3f8
```

## Language/Locale Support

Many endpoints support localized content. Use the `--locale` parameter:

```bash
python content_api.py countries --locale de  # German
python content_api.py countries --locale en  # English
python content_api.py countries --locale nl  # Dutch (default)
```

## Output Format

All scripts output JSON to stdout for easy integration with other tools.

## Error Handling

- **401**: Invalid or missing API key
- **403**: API key not authorized for this endpoint
- **404**: Resource not found
- **429**: Rate limited (for bulk geo endpoints with full=true)

## For Write Operations

This skill is read-only. For create, update, or delete operations (bookings, reservations, cancellations), use the `tools-api` skill instead.
