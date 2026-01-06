
[Tools API](../Tools%20API.md)

# Car Rental API (Sunny Cars / Rentalcars)

- [Car Rental API](#car-rental-api)
  - [Introduction](#introduction)
  - [Providers](#providers)
  - [Creating reservations](#creating-reservations)
    - [Prerequisites](#prerequisites)
      - [Pickup and dropoff location](#pickup-and-dropoff-location)
        - [Searching by airport code](#searching-by-airport-code)
        - [Searching by country](#searching-by-country)
        - [Searching by name](#searching-by-name)
      - [Vehicle and service type](#vehicle-and-service-type)
      - [Vehicle location](#vehicle-location)
      - [Other information (Sunny Cars only)](#other-information-sunny-cars-only)
    - [Accessories](#accessories)
    - [Creating a reservation](#creating-a-reservation)
      - [Booking API](#booking-api)
      - [Direct reservations](#direct-reservations)
  - [Other functions](#other-functions)
    - [Simplified search](#simplified-search)
    - [Cancellation](#cancellation)
    - [Reservation information](#reservation-information)
    - [Listing reservations](#listing-reservations)
    - [Update/Recap](#update-recap)
    - [Localisation](#localisation)
    - [Performance](#performance)

# Car Rental API

## Introduction

The Car Rental API is a json API service for managing rental cars. All calls are done using HTTP GET, except the ones that modify database information at either Elmar or the rental company.  
All mentioned api calls below are relative to the base url.

- Production: <https://api.elmar.nl/tools/carrental>
- Acceptance: <https://api.acc.elmar.nl/tools/carrental> or <https://api.acc2.elmar.nl/tools/carrental>
- Development: <http://localhost:4000/carrental>

## Providers

Currently the only provider with full support is Sunny Cars, but Rentalcars is also supported for searching only. Provider can be selected with the 'provider' query parameter (e.g. url?provider=sunny\_cars), and is also chosen automatically based on the booking type in e.g. the search by booking endpoint. If no provider can be determined from the parameters or the booking, Sunny Cars will be used as default.

| Provider    | Default                                                                                                  | Full search                                                                                              | Simple search                                                                                            | Booking                                                                                                  |
|:------------|:---------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|
| sunny\_cars | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/check.png) | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/check.png) | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/check.png) | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/check.png) |
| rentalcars  | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/error.png) | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/check.png) | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/check.png) | ![](/wiki/s/1501342516/6452/a5e9a05c49c0d433ce7adb3838f56979136cdc1c/_/images/icons/emoticons/error.png) |

## Creating reservations

### Prerequisites

#### Pickup and dropoff location

Searching can be done by either region or location. A region is an area with one or more locations. A location is a specific rental car office. Searching by region is preferred, since the Sunny Cars API returns the best priced result for a specific vehicle from all locations in a region. Searching by location is not guaranteed to return vehicles at all, since there might be nothing available.

While making reservations, a location needs to be specified, not a region. After searching for vehicles within a region, the location can be obtained for that vehicle.

Searching a region can be done by airport code, country or name:

##### Searching by airport code

|  API call                      |  function                                                      |
|:-------------------------------|:---------------------------------------------------------------|
| /airports                      | Returns a list of available airports                           |
| /airports/<iatacode>           | Returns a single airport by code.                              |
| /airports/<iatacode>/regions   | Returns all regions on this airport. This is usually only one. |
| /airports/<iatacode>/locations | Returns all locations on this airport.                         |

Supported parameters on the /airports call:

- country: filter by country, e.g. /airports?country=NL

##### Searching by country

|  API call                   |  function                              |
|:----------------------------|:---------------------------------------|
| /countries                  | Returns a list of available countries  |
| /countries/<code>           | Returns a single country               |
| /countries/<code>/airports  | Returns all airports in this country.  |
| /countries/<code>/regions   | Returns all regions in this country.   |
| /countries/<code>/locations | Returns all locations in this country. |

##### Searching by name

|  API call                           |  function                                                                                             |
|:------------------------------------|:------------------------------------------------------------------------------------------------------|
| /regions?name=<city>                | Find regions by name. Searching by city name gives best results                                       |
| /regions?name=<city>&country=<code> | FInd regions by name. Same as above, but restricts results to places in the country with code <code>. |

#### Vehicle and service type

A vehicle ID and service type need to be obtained from the search. These are required to make a reservation. Service type can not be automatically determined by the API as there may be multiple possible servicetypes for a vehicle.

Vehicles can be located in the following ways:

|  API call                          |  function                                                        |
|:-----------------------------------|:-----------------------------------------------------------------|
| /airports/<iatacode>/vehicles      | Returns all vehicles on all regions and locations this airport.  |
| /locations/<location\_id>/vehicles | Returns all vehicles on the specified location                   |
| /regions/<region\_id>/vehicles     | Returns all vehicles on all locations in the specified region    |
| /vehicles                          | Alternate way to search, takes parameters. See below for details |

Supported parameters for the /vehicles call (these are equivalent to the calls above):

- airport: airport to search in, e.g. /vehicles?airport=AMS
- location: location id to search in, e.g. /vehicles?location=1234
- region: region id to search in, e.g. /vehicles?region=1234

Searching with different pickup and return locations can be done using the above parameters suffixed with '\_pickup' and/or '\_dropoff'. When these are present they take priority over the non-suffixed parameter. For example: /vehicles?airport\_pickup=AMS&airport\_dropoff=RTM

Supported global parameters:

|  Parameter    |  Required?    |  Format                 |  Description                                                                    |
|:--------------|:--------------|:------------------------|:--------------------------------------------------------------------------------|
| meeting       | no            | airport/address/counter | Filter for the location type where the vehicle should be picked up and dropped. |
| departuredate | yes           | yyyy-mm-dd              | Pickup date of the vehicle.                                                     |
| departuretime | no            | HH:MM                   | Pickup time of the vehicle. Defaults to 12:00 if not specified.                 |
| returndate    | yes           | yyyy-mm-dd              | Return date of the vehicle.                                                     |
| returntime    | no            | HH:MM                   | Return time of the vehicle. Defaults to 12:00 if not specified.                 |
| airco         | no            | true                    | Only return vehicles with airconditioning.                                      |
| automatic     | no            | true                    | Only return vehicles with automatic transmission.                               |
| type          | no            | numerical ID            | Filter by vehicle type. See below under "Other information".                    |

#### Vehicle location

When searching vehicles by location, the location ID is already known. When searching by region, the location ID has to be obtained from the API. This can be done in the following ways, depending on the information that is known:

|  API call                                                                      |  function                                                                          |
|:-------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|
| /airports/<iatacode>/vehicles/<vehicle\_id>/locations/<servicetype>            | Find the location of the specified vehicle by airport code.                        |
| /regions/<region\_id>/vehicles/<vehicle\_id>/locations/<servicetype>           | Find the location of the specified vehicle by region id.                           |
| /locations?region=<region\_id>&vehicle=<vehicle\_id>&servicetype=<servicetype> | Find the location by specifying region, vehicle and servicetype in a query string  |
| /locations?airport=<iatacode>&vehicle=<vehicle\_id>&servicetype=<servicetype>  | Find the location by specifying airport, vehicle and servicetype in a query string |

Servicetype can be found in the vehicle json.

#### Other information (Sunny Cars only)

For display purposes it can be useful or required to get more information about vehicles. Below are some calls you can make to gather information.

|  API call                   |  function                                                                                      |
|:----------------------------|:-----------------------------------------------------------------------------------------------|
| /vehicles/builds            | Get a list of vehicle builds, e.g. 'standard', 'SUV', etc                                      |
| /vehicles/features          | Get a list of possible vehicle features, such as 4WD or GPS                                    |
| /vehicles/services          | Get a list of possible services such as fuel policies, insurance clauses, included extras, etc |
| /vehicles/servicetypes      | Get a list of servicetypes and what's included                                                 |
| /vehicles/servicetypes/<id> | Get a single servicetype                                                                       |
| /vehicles/types             | Get a list of vehicle types, e.g. 'small car', 'minivan', etc                                  |

### Accessories

Accessories are not car-specific but location specific. After acquiring the location ID, use the following call to find the available accessories at this location:

|                                                                                                       |
|:------------------------------------------------------------------------------------------------------|
| <br/>```<br/>/locations/<location_id>/accessories?departuredate=<date>&returndate=<date><br/>```<br/> |

### Creating a reservation

There are 2 ways to create a reservation: immediately, or through the booking API.

#### Booking API

This method is best suited when the reservation needs to be registered before it is booked later (e.g. on the website, where the customer has to pay first). The desired car can be specified in the booking json and will be visible in Booking Admin but not registered with Sunny Cars yet. Refer to the   
[Booking API](Booking%20API.md) for more information on how to register the car.

To make the reservation with Sunny Cars, use the following call:

|                                       |
|:--------------------------------------|
| POST /reservations/book/<booking\_id> |

This will return a json with the latest status of all cars that were reserved during this call.

#### Direct reservations

Creating the reservation can be done by sending a POST request to /reservations. On success, the reservation will be added to the database by the API.  
Below is a list of parameters:

|  Parameter    |  Required?    |  Format                 |  Description                                                                                                                                                                                  |
|:--------------|:--------------|:------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| booking       | yes           | UUID                    | The ID of the booking to make the reservation for.                                                                                                                                            |
| location      | yes           | numerical ID            | The Sunny Cars ID of the location to pickup and drop the vehicle.                                                                                                                             |
| meeting       | yes           | airport/address/counter | The location type where the vehicle should be picked up and returned.                                                                                                                         |
| meetinginfo   | no            | string                  | The location where to pickup and return the vehicle. Will be filled automatically unless specified. Address format requested by Sunny Cars: "Acco name, Acco address, Phone number"           |
| servicetype   | yes           | numerical ID            | The servicetype ID of the requested vehicle offer.                                                                                                                                            |
| departuredate | no            | yyyy-mm-dd              | Pickup date of the vehicle. The departure date of the booking will be used if not specified.                                                                                                  |
| departuretime | no            | HH:MM                   | Pickup time of the vehicle. Defaults to 12:00 if not specified.                                                                                                                               |
| returndate    | no            | yyyy-mm-dd              | Return date of the vehicle. The return date of the booking will be used if not specified.                                                                                                     |
| returntime    | no            | HH:MM                   | Return time of the vehicle. Defaults to 12:00 if not specified.                                                                                                                               |
| driver        | no            | UUID                    | The ID of the person who is considered the main driver. Defaults to the main booker if not speficied.                                                                                         |
| user          | no            | elmar uid               | The user id (e.g. ferlan) of the user making the reservation. Defaults to 'tools' if not set. A different string like 'website' can also be specified to indicate a source other than people. |
| flexservice   | no            | boolean                 | Add Sunny Cars flexservice (free cancellation up to 4 hours in advance). The fee is specified in the vehicles search output under service.options.insurance.                                  |
| accessories   | no            | 100,200                 | List of accessory ID's to book, separated by commas. Specify an ID multiple times to book more than one of a type. See above under 'accessories' on how to get the ID's.                      |
| check         | no            | boolean                 | Don't make a real booking, do a check if the booking would be succesful instead.                                                                                                              |

Parameters 'location', 'meeting' and 'meetinginfo' can be supplied with a suffix of '\_pickup' or '\_dropoff' if the information is different for pickup and return, e.g.: meeting\_pickup=airport&meeting\_dropoff=address

## Other functions

### Simplified search

Because searching is quite a complex process, even with many details already abstracted away, there is an endpoint for simplified searches that take no parameters other than a booking ID. This can be used for e.g. marketing, where the requirement is simply to show some carrental offers.

| API call                              | function                                                                                                                                                                                     | example                                                                                    |
|:--------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|
| /search/<booking\_id>                 | Return carrental offers for the specified booking                                                                                                                                            | <https://api.elmar.nl/tools/carrental/search/015d54d2-ed6d-4798-925c-0edbd84d8aac>         |
| /search/<system>/<booking\_id>        | Return carrental offers for a booking from an external system. Currently supported: 'zeus', 'mobis', 'flygstolen'/'fs'/'tm'.                                                                 | <https://api.elmar.nl/tools/carrental/search/mobis/VTN-1424782>                            |
| /search/<booking\_id>/<type>          | Only return offers for the specified meeting type (airport, counter or address). This is only for speeding up searches and offers no additional functionality compared to the full endpoint. | <https://api.elmar.nl/tools/carrental/search/015d54d2-ed6d-4798-925c-0edbd84d8aac/airport> |
| /search/<system>/<booking\_id>/<type> | Same as above, but for external bookings.                                                                                                                                                    | <https://api.elmar.nl/tools/carrental/search/mobis/VTN-1424782/airport>                    |

### Cancellation

Send a POST request to /reservations/<reservation\_id>/cancel. No parameters are required or supported. The database will be updated to reflect the new status.

### Reservation information

To get information on 1 reservation, make a GET request to /reservations/<reservation\_id>.

### Listing reservations

Sending GET instead of POST to /reservations will return a list of current reservations. The following optional parameters are supported for filtering:

|  Parameter          |  Format                       |  Description                                                                                                                                                                  |
|:--------------------|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| status              | confirmed/requested/cancelled | Filter by status                                                                                                                                                              |
| name                | string                        | Search by driver surname                                                                                                                                                      |
| reservation\_number | numerical ID                  | Only retrieve the specified reservation by ID. This is different from the above single reservation call in that this call does not return an error when the ID was not found. |
| after\_date         | yyyy-mm-dd                    | Only retrieve reservations with a pickup date higher than the specified date.                                                                                                 |
| before\_date        | yyyy-mm-dd                    | Only retrieve reservations with a dropoff date lower than the specified date.                                                                                                 |

### Update/Recap

Our database can be updated with the latest information from the rental company by making a POST request to /reservations/<reservation\_id>/update. No parameters are required or supported.

### Localisation

This service supports localisation. The default language is Dutch (nl). To use the service in another language, either send http header HTTP\_ACCEPT\_LANGUAGE with the desired language code, or append the query parameter 'locale=<code>' to your calls.  
Currently the following languages are supported: nl (Dutch), de (German) en (English).

### Performance

- Requested information other than vehicle offer listings and reservation information is cached for 1 day.
- The Sunny Cars API authentication works with a ticket system giving out tickets with a validity of 3 minutes. If the Car Rental API is not under frequent use, the first call will take more time because a new ticket has to be requested.
