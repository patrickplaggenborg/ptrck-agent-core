
[Tools API](../Tools%20API.md)

# Booking API

- [Booking API](#booking-api)
  - [Retrieving bookings](#retrieving-bookings)
  - [Submitting bookings](#submitting-bookings)
    - [General notes](#general-notes)
    - [Create notes](#create-notes)
    - [Update notes](#update-notes)
    - [VTO data](#vto-data)
    - [Codes](#codes)
      - [Statuses](#statuses)
      - [Boarding types](#boarding-types)
      - [Accommodation types](#accommodation-types)
      - [Transport types](#transport-types)
    - [Example request JSON](#example-request-json)
  - [Asynchronous bookflow](#asynchronous-bookflow)
  - [Cancellations](#cancellations)
    - [Response codes for cancellations](#response-codes-for-cancellations)
    - [Supported suppliers for cancellation](#supported-suppliers-for-cancellation)
  - [Insurances](#insurances)
    - [Calculating premiums](#calculating-premiums)
    - [Registering insurance selection](#registering-insurance-selection)
    - [Creating policies in the insurance provider's system](#creating-policies-in-the-insurance-provider-s-system)
  - [Rental Cars](#rental-cars)
  - [Parking](#parking)
    - [Searching for offers](#searching-for-offers)
    - [Service information flags](#service-information-flags)
  - [Payments](#payments)
  - [Confirmation emails](#confirmation-emails)
    - [Sending](#sending)
    - [Rendering](#rendering)

# Booking API

## Retrieving bookings

|  API call                            |  function                                                                                       |  examples                                                                                                                   |
|:-------------------------------------|:------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|
| GET /bookings/<id>                   | Retrieve booking information (by database/booking ID or reservation number).                    | <https://api.elmar.nl/tools/bookings/2fd6c830-1398-11e5-93ff-bc305bedc3f8> <https://api.elmar.nl/tools/bookings/V140049277> |
| GET /bookings/<id>/status            | Retrieve booking status per component by booking id (payment, package and carrental).           | <https://api.elmar.nl/tools/bookings/2fd6c830-1398-11e5-93ff-bc305bedc3f8/status>                                           |
| GET /bookings                        | Retrieve multiple bookings simultaneously. Specify ID's in parameter 'ids' separated by commas. | <https://api.acc.elmar.nl/tools/bookings?ids=ae817a96-a75f-4051-82cc-092989745815,b43c9fcf-aa1a-4044-be44-0016594d4324>     |
| GET /bookings/user\_service\_id/<id> | Retrieve all bookings belonging to the specified user\_service\_id.                             | <https://api.acc.elmar.nl/tools/bookings/user_service_id/70a1bd61-8261-4526-a813-2d84f27352ae>                              |

## Submitting bookings

Bookings are submitted as json (see example below).  
The output is the same as for a GET request when retrieving a booking. From this output the new booking ID and reservation number can be retrieved when creating new bookings.

|  API call          |  function                                             |
|:-------------------|:------------------------------------------------------|
| POST /bookings     | Create a new booking                                  |
| PUT /bookings/<id> | Update a booking by database ID or reservation number |

### General notes

- Unknown fields in the json are ignored
- The ID may be specified in the create request. Only valid UUID's are accepted, and Tools will throw an error if the UUID is in use. A random ID will be generated if not specified or the value is invalid. Even though it's technically possible, please refrain from using sequential UUID's (e.g. 0000...001) and use real random UUID's instead.
- Supported values for label: 'vd', 'vdbe', 'fd', 'elmar'
- Supported values for status: 'confirmed', 'option', 'onrequest', 'cancelled', 'processing', 'finalizing', 'exception', 'new', 'pending'
- Country in packages is ignored if accommodation id is present and valid (accommodation country id is used instead)
- The format for date/datetime fields can be any format supported by ruby Date.parse, the values in the example below are examples but not required (e.g. '2015/05/13 11:45' is fine too)
- All monetary values are in eurocents
- Specifying ID for people is optional and only supported for new additions. Only UUID format is accepted. A random ID will be generated if not specified or valid.
- Gender: 0/M = male, 1/F/V = female
- Messages are TO errata and can be either a string or a hash. For strings the current time is used as a timestamp. Different formats can be mixed.
- Commission is calculated internally. There is no field to specify this. Packages/payment/undiscounted\_price is an optional field, but highly recommended. If this is not present, the undiscounted price will be calculated internally, with possible discrepancies.
- Customer is the main booker if this person also appears in the travel party (matched by full name and birthdate). If the customer is not in the travel party (e.g. a customer booking on behalf of someone else), the first person in the travelparty will become the main booker.
- Surcharges are price elements that are not part of packages, e.g. elmar.nl administrative costs. Prices can be negative (in case of discounts). Items with an amount of 0 will be ignored. Valid types are: 'administrative', 'baggage', 'discount', 'seat', 'tax', 'transfer', 'visa'
- Paid payments should only be added when they are confirmed to have been paid (not future payments).
- Some additional restrictions apply to ensure data integrity (e.g. 'VL' transport type needs to have flight information, touroperator brand needs to exist, etc). An error will be returned with an explanation and a 400 http status if restrictions are broken.
- When submitting price absorption, send the original amount as usual (in the travel\_fare field), and send the difference (positive or negative) in the price\_absorption field. Summed up they should match the price shown to the customer.

### Create notes

- Many information is mandatory on creation of new bookings: label, status, customer, at least 1 package, at least 1 person in travelparty

### Update notes

- Some fields can not be changed after creation, e.g. 'label', booking date or the reservation number. Create a new booking instead when these need to be modified.
- It is not necessary to specify the full booking to submit updates, but if a root section is included, the full section needs to be included. For example: { "status": "confirmed" } is a full, accepted json and will only update the booking status.
- An empty array is not the same as a missing section, e.g. { "payments": [] } will remove all payments
- G7 messages should not be submitted multiple times. For example, do not submit the same G7 log on update that was submitted during creation. This is to allow collecting them for multiple booking attempts (e.g. rebooks) without having to know the full history.
- Vouchers will be ignored until status 'finalizing'/'confirmed'. This is because we only want to deduct the voucher after all amounts are fixed, since it can only be done once. Therefore, even though you can update a status by specifying only the status field in the json, if there is no voucher information in this call, no voucher will be deducted, even if it was specified at an earlier stage, since this information was not saved anywhere before.

### VTO data

- "book\_id" is InventoryTransactionKey, "ref" is TransactionNumber
- "price" is NetAmount, "margin" is CalcInfo/Factor. Margin can be added per component, and on top of the total. These are all independent of eachother, even though at the time of writing the margins per component are all 1.0. If global CalcInfo is not present for whatever reason, it should be calculated from the other amount data, not left blank.
- If a component is not present, set its values to null.
- Flight brand is not the airline, but the supplier. These can be the same, but not always (e.g. for aggregators, or when brand and supplier code differ).
- Brand codes should be Tools codes, not the raw values from the XML, as Peakwork makes a mess of brand codes.

### Codes

#### Statuses

|  Status    |  Meaning                                                                                                                                                                                                |
|:-----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| new        | Don't use. Used by Booking Admin for unfinished bookings that a travel agent is working on.                                                                                                             |
| pending    | The customer is currently going through the booking steps. The booking will not show up in Booking Admin. This is generally used to store booking details after filling in the travellers details form. |
| processing | The customer has been redirected to a payment form outside of our website and is now untraceable until redirected back to us.                                                                           |
| finalizing | The booking process is finished, customer has paid, and the booking is (or should) now being booked at the touroperator.                                                                                |
| confirmed  | Booking process is finished successfully. The booking has been created at the touroperator and there is nothing left to be done.                                                                        |
| option     | Like 'confirmed', but the booking is in option status (customer needs to give approval before finalizing the reservation at the touroperator)                                                           |
| onrequest  | Like 'confirmed', but the booking is in 'on request' status at the touroperator. The customer is finished but the travel agency still has manual work left to do.                                       |
| cancelled  | The booking was cancelled. This can either mean a failed attempt, and the attempt was cancelled, or the booking was completed, and then cancelled on the customer's request.                            |
| exception  | Something went wrong and the booking can not be completed due to technical reasons. Manual action has to be taken to recover this booking.                                                              |

#### Boarding types

[^AB: American breakfast]:  
[^AI: All inclusive]  
[^BB: English breakfast]  
[^BR: Brunch]  
[^CB: Continental breakfast]  
[^DV: Miscellaneous]  
[^HP: Half board]  
[^LG: Lodging]  
[^LO: Lodging + breakfast]  
[^UA: Ultra all inclusive]  
[^VB: See description]  
[^VP: Full board]

#### Accommodation types

[^ALB: Albergaria]:  
[^APO: Apartotel]  
[^APP: Apartment]  
[^BNB: Bed & Breakfast]  
[^BNG: Bungalow]  
[^BRY: Farm]  
[^CAM: Camping]  
[^CAR: Caravan]  
[^CHA: Chalet]  
[^CPR: Camper]  
[^CRU: Cruise]  
[^EST: Estalgem]  
[^GHF: Inn]  
[^GUE: Guesthouse]  
[^HOS: Hostel]  
[^HOT: Hotel]  
[^HUI: House]  
[^KAS: Castle]  
[^MAI: Maisonnette]  
[^MOT: Motel]  
[^PEN: Pension]  
[^RES: Residencial]  
[^RON: Tour]  
[^SCH: Boat]  
[^TNT: Tent]  
[^VAK: Holiday park]  
[^VIL: Villa]  
[^WNG: Home]

#### Transport types

[^AV: Flight only]:  
[^BO: Boat]  
[^BU: Bus]  
[^EV: Accommodation only (a.k.a. "own transport")]  
[^FE: Ferry]  
[^TF: Transfer]  
[^TR: Train]  
[^VL: Package (acco + flight)]

### Example request JSON

```js
{
    "id": "710ff857-327f-40b1-ad2b-828a676b8476"
    "label": "vd",
    "status": "pending",
    "customer_comments": "test booking",
    "rebook": false,
    "user_service_id": "70a1bd61-8261-4526-a813-2d84f27352ae",
    "packages": [
        {
            "country": "ES",
            "transport_type": "VL",
            "departure_date": "2018-05-13",
            "return_date": "2018-05-27",
            "transfer": false,
            "touroperator": {
                "brand": "AR",
                "book_id": "BKYP50",
                "product": {
                    "code": "HI00X2LPA0111190",
                    "brand": "AR"
                }
            },
            "accommodation": {
                "id": "087c95f0-8f5c-11df-a2df-001c42000009",
                "type": "HOT",
                "boarding_type": "HP",
                "rooms": [
                    {
                        "id": "2PKA",
                        "type": "2PK",
                        "description": "2-persoonskamer"
                    }
                ]
            },
            "flights": {
                "outbound": {
                    "departure_airport": "AMS",
                    "arrival_airport": "LPA",
                    "departure_datetime": "2015-05-13T00:00:00",
                    "arrival_datetime": "2015-05-13T00:00:00",
                    "flight_class": {
                        "code": "E",
                        "name": "Economy"
                    },
                    "tariff": "Standard",
                    "carrier": "HV",
                    "flight_number": "HV1234",
                    "seats": 2,
                    "pnr": "AAA111",
                    "supplier_source": "GDS",
                    "included_baggage": {
                        "size": "30x40x50",
                        "weight": 20
                    },
                    "segments": [
                        {
                            "departure_airport": "AMS",
                            "arrival_airport": "LPA",
                            "departure_datetime": "2015-05-13T00:00:00",
                            "arrival_datetime": "2015-05-13T00:00:00",
                            "flight_class": {
                                "code": "E",
                                "name": "Economy"
                            },
                            "carrier": "HV",
                            "flight_number": "HV1234"
                        }
                    ]
                },
                "inbound": {
                    "departure_airport": "LPA",
                    "arrival_airport": "AMS",
                    "departure_datetime": "2018-05-27T00:00:00",
                    "arrival_datetime": "2018-05-27T00:00:00",
                    "flight_class": {
                        "code": "E",
                        "name": "Economy"
                    },
                    "carrier": "HV",
                    "flight_number": "HV1235",
                    "seats": 2,
                    "pnr": "AAA111",
                    "included_baggage": {
                        "size": "40x50x60",
                        "weight": 10
                    },
                    "segments": [
                        {
                            "departure_airport": "LPA",
                            "arrival_airport": "AMS",
                            "departure_datetime": "2018-05-27T00:00:00",
                            "arrival_datetime": "2018-05-27T00:00:00",
                            "flight_class": {
                                "code": "E",
                                "name": "Economy"
                            },
                            "carrier": "HV",
                            "flight_number": "HV1235"
                        }
                    ]
                }
            },
            "baggage": [
                {
                    "person": "11111111-2222-3333-4444-555555555555",
                    "price": 1500,
                    "weight": 12,
                    "booked": false,
                    "price_absorption": 200
                },
                {
                    "person": "66666666-7777-7777-8888-999999999999",
                    "flight": "99999999-8888-7777-7777-666666666666",
                    "price": 2988,
                    "weight": 20,
                    "booked": true,
                    "price_rounding": 12
                }
            ],
            "payment": {
                "travel_fare": 12040,
                "undiscounted_price": 12240,
                "calamityfund": 250,
                "voucher": "ABCD1234",
                "price_absorption": -100,
                "price_rounding": -40
            },
            "description": "Original product description as sold to the customer"
        }
    ],
    "travelparty": [
        {
            "id": "11111111-2222-3333-4444-555555555555",
            "firstname": "Dirk",
            "infix": "de",
            "surname": "Test",
            "gender": "M",
            "date_of_birth": "1984-12-09",
            "nationality": "NL"
        },
        {
            "id": "66666666-7777-7777-8888-999999999999",
            "firstname": "Albert",
            "infix": "van der",
            "surname": "Test",
            "gender": "M",
            "date_of_birth": "1968-08-01",
            "nationality": "NL"
        }
    ],
    "customer": {
        "firstname": "Albert",
        "infix": "van der",
        "surname": "Test",
        "gender": "M",
        "date_of_birth": "1968-08-01",
        "address": {
            "street": "Teststraat",
            "house_number": "10",
            "house_number_suffix": null,
            "city": "Rotterdam",
            "postal_code": "3069BC",
            "country": "NL"
        },
        "contact": {
            "email": "test@test.nl",
            "phone": "0653493253",
            "mobile": "0104334399"
        }
    },
    "emergency_contact": {
        "name": "Familie Test",
        "email": "test@test.com",
        "phone": "0612345678"
    },
    "priceitems": [
        {
            "price": 12000,
            "description": "Luchthavenbelasting"
        },
        {
            "price": -10000,
            "description": "Vroegboekkorting",
            "quantity": 2
        }
    ],
    "insurances": [
        {
            "type": "RV-XXX",
            "people": [
                "11111111-2222-3333-4444-555555555555",
                "66666666-7777-7777-8888-999999999999"
            ],
            "price_absorption": 160,
            "price_rounding": -60
        },
        {
            "type": "AV-XXX",
            "voucher": "ABCD1234"
        }
    ],
    "rental_cars": [
        {
            "price": 8000,
            "price_absorption": -220,
            "price_rounding": 20,
            "flexservice": false,
            "driver": "11111111-2222-3333-4444-555555555555",
            "vehicle": {
                "id": 39512,
                "name": "Fiat 500",
                "service": 151,
                "accessories": [ 300 ]
            },
            "pickup": {
                "datetime": "2018-05-13T00:00:00",
                "location": 59578,
                "meeting": "airport"
            },
            "dropoff": {
                "datetime": "2018-05-27T00:00:00",
                "location": 59578,
                "meeting": "airport"
            }
        }
    ],
    "parking": [
        {
            "offer_id": "1234567890abcdef",
            "price": 10020,
            "price_absorption": 160,
            "price_rounding": 20,
            "name": "QPark Schiphol",
            "license_plate": "AA11BB",
            "card": "1234-5678-8765-4321(optional)",
            "comment": "Optional customer comment",
        }
    ],
    "surcharges": [
        {
            "type": "administrative",
            "amount": 1250
        },
        {
            "type": "sgr_contribution",
            "amount": 1500
        }
    ],
    "paid": [
        { "amount": 5000, "reference": 'ZKN86RP6GCLZNN82' }
    ],
    "messages": [
        "some message",
        { "timestamp": "2018-05-11T11:59:58", "text": "some message with timestamp" }
    ],
    "g7": [
        {
            "session": "12345",
            "xml": "<TravelMessage></TravelMessage>",
            "timestamp": "2018-05-13 02:34:00"
        },
        {
            "session": "12345",
            "xml": "<TravelMessage></TravelMessage>",
            "timestamp": "2018-05-13 02:34:01"
        }
    ],
    "vto": {
        "accommodation": {
            "brand": "OTS",
            "book_id": "123456",
            "ref": "87654",
            "price": 20000,
            "margin": 1.0,
            "status": "Booked"
        },
        "flight": {
            "brand": "KIWI",
            "book_id": "123456",
            "price": 30000,
            "margin": 1.0,
            "status": "NotBooked"
        },
        "transfer": {
            "brand": "OTS",
            "book_id": "123456",
            "ref": "87654",
            "price": 10000,
            "margin": 1.0,
            "status": "Booked"
        },
        "package": {
            "price": 60000,
            "margin": 1.213,
            "status": "Booked"
        }
    }
}

```

## Asynchronous bookflow

|  API call                          |  function                                           |      |
|:-----------------------------------|:----------------------------------------------------|:-----|
| PUT /bookings/<booking\_id>/booked | Triggers the bookflow after a booking has been made |      |

Trip-API can respond to a book call from Tools with a status of 'finalizing'. This means for Tools that Trip-API is not finished with the booking process, but will report back to Tools when it's done. Tools will not do anything other than updating the booking data when the status is 'finalizing'. The above endpoint can be called when Trip-API is finished and will run all the actions for new bookings. The expected data format for the result is the booking API json shown in the example above.

## Cancellations

Tools can cancel bookings directly at the supplier via an API connection for certain suppliers. This allows for faster cancellation procedures and website integration.

|  API call                                                                     |  function                                                   |
|:------------------------------------------------------------------------------|:------------------------------------------------------------|
| GET /bookings/<booking\_id>/cancel <br/> GET /packages/<package\_id>/cancel   | Retrieve cancellation information by booking or package ID. |
| POST /bookings/<booking\_id>/cancel <br/> POST /packages/<package\_id>/cancel | Cancel the package directly at the supplier                 |

### Response codes for cancellations

|    Code  |  Meaning                                        |
|---------:|:------------------------------------------------|
|     200  | Everything was ok                               |
|     204  | Cancellation not possible (GET)                 |
|     422  | Something went wrong during cancellation (POST) |

### Supported suppliers for cancellation

|      |
|:-----|
| VTOP |

## Insurances

### Calculating premiums

|  API call                              |  function                                                               |  examples                                                                             |
|:---------------------------------------|:------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|
| GET /bookings/<booking\_id>/insurances | Retrieve all possible insurances with premium for the specified booking | <https://api.elmar.nl/tools/bookings/2fd6c830-1398-11e5-93ff-bc305bedc3f8/insurances> |

Supported parameters:

|  Parameter         |  Values             |  Default    |  Description                                                                                                                                 |
|:-------------------|:--------------------|:------------|:---------------------------------------------------------------------------------------------------------------------------------------------|
| provider           | allianz,europeesche | allianz     | The insurance provider to use.                                                                                                               |
| people             | id1,id2,...         | all         | Comma separated list of person id's to calculate premiums for. Default when not specified is the full travelparty.                           |
| show\_ev           | true/false          | true        | Include insurance types suitable for own transport. Will only show up for bookings with transport type EV.                                   |
| show\_wintersports | true/false          | true        | Include insurance types suitable for wintersports. Will only show up for wintersports countries.                                             |
| live               | true/false          | false       | Use the Europeesche endpoint instead of an internal calculation for calculating premiums. Europeesche provider only, Allianz is always live. |

### Registering insurance selection

Registering insurances is done through the main booking api. See the above json for an example.

- Person id's can be retrieved from the premiums response
- If no people are specified for an insurance, the full travelparty is used.

### Creating policies in the insurance provider's system

This is deprecated. The call mentioned here is a dummy. Tools will automatically register policies when the booking is confirmed

|  API call                               |  function                                                                                                      |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------------------|
| POST /bookings/<booking\_id>/insurances | Create insurance policies inside the insurance provider's system, as previously specified in the booking json. |

## Rental Cars

Rental cars can be specified in the json and will be booked by the car rental API. See the [Car Rental API (Sunny Cars / Rentalcars)](Car%20Rental%20API%20(Sunny%20Cars%20_%20Rentalcars).md) for how to search for the correct information (vehicle ID, service ID, etc) and make the booking.  
See the json for an example. All information in the example is required except for the fields 'flexservice' and 'accessories', which will be treated as 'false' and 'none' when left out.

## Parking

### Searching for offers

|  API call                  |  function                                      |
|:---------------------------|:-----------------------------------------------|
| GET /parking/<booking\_id> | Show offers that are relevant for this booking |

### Service information flags

|  Flag                     |  Meaning                                                                                                                                                             |
|:--------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| valet                     | True if this a valet parking service, false otherwise                                                                                                                |
| overnight\_stay           | True if an overnight hotel stay is included with this offer                                                                                                          |
| taxi                      | True if this is a taxi service (you will be picked up at home instead of driving to the airport by car)                                                              |
| shuttle                   | True if there is a shuttle service driving you to the airport                                                                                                        |
| shuttle\_people\_included | Number of people that are included in this shuttle service. 0 = always paid, 99 = unlimited, or any value for a hard limit. More people than this limit have to pay. |
| public\_transport         | The trip between the parking lot and the airport is by public transport                                                                                              |
| walking\_distance         | The parking is in walking distance of the airport                                                                                                                    |
| app\_required             | A smartphone with Mobian app is required for this service                                                                                                            |
| enclosed                  | The parking venue is a private closed off area, using e.g. walls, fences or gates                                                                                    |
| guarded                   | Guards are present 24/7                                                                                                                                              |
| Indoor                    | True if indoor, false if outdoor, null if unknown                                                                                                                    |
| keep\_key                 | True if the key stays with the vehicle's owner, false if the key has to be handed in to the parking provider, null if unknown                                        |
| open247                   | 24/7 opened                                                                                                                                                          |
| security\_cameras         | The parking lot is protected by camera surveillance                                                                                                                  |
| wheelchair\_friendly      | The transfer possibilities have support for people in wheelchairs                                                                                                    |

## Payments

The booking API can be used to handle payments through Ogone or Adyen. Redirect the user to the a link generated by the endpoint specified below and Tools will handle registering the payment and redirecting back to the website (specified by the parameters below). It is possible to specify the desired payment method as a last parameter. This is optional for Adyen, use 'all' when no payment method restriction is needed.

|  API call                                                                      |  example                                                                                        |
|:-------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| GET /bookings/<booking\_id>/ogone\_links/<amount\_in\_cents>                   | <https://api.elmar.nl/tools/bookings/2fd6c830-1398-11e5-93ff-bc305bedc3f8/ogone_links/50000>    |
| GET /bookings/<booking\_id>/adyen\_links/<amount\_in\_cents>                   |                                                                                                 |
| GET /bookings/<booking\_id>/adyen\_links/<amount\_in\_cents>/<payment\_method> | <https://api.elmar.nl/tools/bookings/2fd6c830-1398-11e5-93ff-bc305bedc3f8/adyen_links/5000/all> |

The following parameters are supported. If these are not present, the Tools internal page will be used (similar to links sent by email).

|  parameter    |  function                                                                                                                                                                                             |
|:--------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| successurl    | Url to redirect after successful payment.                                                                                                                                                             |
| errorurl      | Url to redirect after unsuccessful payment. A parameter 'error' will be added with the error code (see below). If successurl is present and errorurl is not, successurl will also be used for errors. |

|    Ogone error code  |  description                                               |
|---------------------:|:-----------------------------------------------------------|
|                   0  | Unknown ogone error                                        |
|                   1  | Ogone code: cancelled                                      |
|                   2  | Ogone code: card refused                                   |
|                   7  | Ogone code: removed (cancelled?)                           |
|                  92  | Ogone code: unknown error                                  |
|                 101  | The order ID provided from Ogone to Tools was not expected |

## Confirmation emails

### Sending

To send the customer a confirmation email, call the following endpoint.

|                                                 |
|:------------------------------------------------|
| POST /bookings/<booking\_id>/send\_confirmation |

The following parameters are supported:

|  parameter    |  function                                   |
|:--------------|:--------------------------------------------|
| invoice       | attach an optional invoice pdf to the email |

### Rendering

To render a confirmation email without sending it, the following endpoint can be used:

|                                          |
|:-----------------------------------------|
| GET /bookings/<booking\_id>/confirmation |
