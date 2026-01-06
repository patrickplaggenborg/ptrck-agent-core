


# Tools API

- [Tools API](#tools-api)
  - [Introduction](#introduction)
    - [Multiple language support](#multiple-language-support)
    - [Access control](#access-control)
  - [Content](#content)
  - [Booking / insurances](#booking-insurances)
  - [Customers](#customers)
  - [Car Rental](#car-rental)
  - [Parking](#parking)
    - [parameters for search](#parameters-for-search)
    - [parameters for creating reservations](#parameters-for-creating-reservations)
  - [Transfer](#transfer)
    - [parameters for transfers (both endpoints)](#parameters-for-transfers-both-endpoints)
  - [Baggage](#baggage)
  - [Hotels](#hotels)
  - [Other](#other)
    - [Image Sync options](#image-sync-options)
    - [Newsletter subscribe options](#newsletter-subscribe-options)
    - [Automated export](#automated-export)

# Tools API

### Introduction

This is an overview of all public API functions that are available on the Elmar Tools API environment.  
The code can be found in the project codenamed Samaritan here: <https://git.elmar.nl/elmardev/samaritan>

All mentioned api calls below are GET requests (unless specified otherwise) and are relative to the base url.

Production: <https://api.elmar.nl/tools/>  
Acceptance: <https://api.acc.elmar.nl/tools/>  
Development: <http://localhost:4000/>

#### Multiple language support

Many endpoints in Tools are localised. Language can be selected by using the standard ACCEPT\_LANGUAGE http header, or the query parameter 'locale' in request urls. When nothing specified, the default is 'nl'.

#### Access control

Tools is protected by an API key system. Keys are generally supplied per team or application. If you don’t have one, ask your team leader or the Tools team. An API key has limited access to the endpoints listed below. Only specifically enabled endpoint groups are allowed. If you’re getting a 403 error (and it’s not due to an IP whitelist), you may need to contact the Tools team to allow access to the endpoint for your key.

### Content

[Content API](Tools%20API/Content%20API.md)

### Booking / insurances

[Booking API](Tools%20API/Booking%20API.md)

### Customers

[Customer API](Tools%20API/Customer%20API.md)

### Car Rental

[Car Rental API (Sunny Cars / Rentalcars)](Tools%20API/Car%20Rental%20API%20(Sunny%20Cars%20_%20Rentalcars).md)

### Parking

|  API call                         |  function                                                 |  example                                                                         |
|:----------------------------------|:----------------------------------------------------------|:---------------------------------------------------------------------------------|
| GET /parking/<booking\_id>/search | Get a list of available services and prices for a booking | <https://api.elmar.nl/tools/parking/3cc41650-ddcf-11e4-9ae3-bc305bedc3f8/search> |
| POST /parking/<booking\_id>       | Create a parking reservation for a booking                |                                                                                  |
| DELETE /parking/<booking\_id>     | Cancel a parking reservation for a booking                |                                                                                  |

##### parameters for search

|  option    |  values    |  mandatory    |  function                    |
|:-----------|:-----------|:--------------|:-----------------------------|
| campaign   | string     | no            | override default campaign ID |

##### parameters for creating reservations

|  option        |  values    |  mandatory    |  function                                                          |
|:---------------|:-----------|:--------------|:-------------------------------------------------------------------|
| provider       | integer    | yes           | specifies the provider to book, as specified in the search results |
| license\_plate | AA-11-BB   | yes           | the license plate of the vehicle                                   |
| comment        | string     | no            | optional comment to send to the provider                           |
| card           | string     | no            | credit card number, can be used as ID with some providers          |

### Transfer

|  API call                       |  function                                                                                                                                                                                                                                                                                                      |  example                                                                     |
|:--------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------|
| /transfer/<brand>/<product\_id> | Check if a product has a transfer included                                                                                                                                                                                                                                                                     | <https://api.elmar.nl/tools/transfer/AL/VLVARVAR105>                         |
| /transfer?products=PROD1,PROD2  | Check multiple products for transfer inclusion. Omit the products parameter to check everything. Also available as POST. <br/> Note: product codes are not unique between brands (e.g. AL/A1, NE/XN/XV, etc). Suffix the product code with a dot and the brand code for better accuracy, e.g. 80194\_NE\_WI.XN | <https://api.elmar.nl/tools/transfer?products=VLVARVAR105.AL,VLVARVAR106.A1> |

##### parameters for transfers (both endpoints)

|  option         |  values    |  mandatory    |  function                                                                                                                                                     |
|:----------------|:-----------|:--------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| departure\_date | date       | no            | Some TO's have temporary changes in transfers. Supplying the departure date will enable these extra conditions. Without, only the general rules will be used. |

### Baggage

|  API call         |  function                                                                                                                                                                                                                    |  example                                                                                                                                                                                                                                                                                                                                                     |
|:------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GET /baggage      | Retrieve included checked (hold) baggage based on criteria. Parameters are supplied as a query string. All parameters in the example are required. Times can be in any date or time format that ruby can parse.              | <https://api.acc.elmar.nl/tools/baggage?brand=TC&arrival=2018-01-02&carrier=KL&departure=2018-01-01T02:00:00&destination=JFK&origin=AMS>                                                                                                                                                                                                                     |
| POST /baggage     | Retrieve included checked (hold) baggage based on criteria. Parameters are supplied in JSON format. All parameters in the example are required. Times can be in any date or time format that ruby can parse.                 | <https://api.acc.elmar.nl/tools/baggage> <br/> ```java<br/>{<br/>  "arrival": "<date or datetime of arrival>",<br/>  "brand": "<touroperator brand code>",<br/>  "carrier": "<carrier iata/icao code>",<br/>  "departure": "<date or datetime of departure>",<br/>  "destination": "<airport ata code>",<br/>  "origin": "<airport iata code>"<br/>}<br/>``` |
| GET /handbaggage  | Retrieve cabin (hand) baggage for an airline. Parameters are supplied as a query string. Carrier is required, brand is optional. An empty JSON and 404 code are returned for carriers with unknown hand baggage information. | <https://api.acc.elmar.nl/tools/handbaggage?carrier=HV>                                                                                                                                                                                                                                                                                                      |
| POST /handbaggage | Retrieve cabin (hand) baggage for an airline. Parameters are supplied in JSON format. Carrier is required, brand is optional. An empty JSON and 404 code are returned for carriers with unknown hand baggage information.    | <https://api.acc.elmar.nl/tools/handbaggage> <br/> ```java<br/>{<br/>  "carrier": "HV",<br/>  "brand": "AR"<br/>}<br/>```                                                                                                                                                                                                                                    |

### Hotels

The hotels api can be used to retrieve hotel offers for a booking. Currently supports booking.com as provider.

|  API call                                |  function                                  |  example                                                                                                                        |
|:-----------------------------------------|:-------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------|
| GET /hotels/(<system\_id>/)<booking\_id> | Retrieve hotels for the specified booking. | <https://api.elmar.nl/tools/hotels/f0902d81-a42a-4f14-9828-48a61fe2b56f> <br/> <https://api.elmar.nl/tools/hotels/zeus/4729252> |

### Other

|  API call                           |  function                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |  example                                                                                                          |
|:------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------|
| /images/compare/<accommodation\_id> | Run the image comparer for an accommodation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | <https://api.elmar.nl/tools/images/compare/143d2940-8f5c-11df-a2df-001c42000009>                                  |
| /images/compare?limit=<limit>       | Run the image comparer for <limit> accommodations that need updating (default 1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | <https://api.elmar.nl/tools/images/compare?limit=10>                                                              |
| /images/sync                        | Synchronize images between database and filesystem. See below for options. This needs to be run on all tools servers as the processing is only local.                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                   |
| /products(.format)                  | Retrieve all products in a csv (default) or json format (deprecated, use /content/products)                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                                                                                                                   |
| POST /newsletters/subscribe         | Subscribe a customer to the VD newsletter. See below for options.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | <https://api.elmar.nl/tools/newsletters/subscribe?email=fake@elmar.nl&firstname=Fake&surname=Customer&country=NL> |
| /recommend/<booking\_id>            | Get recommendations for a booking                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | <https://api.elmar.nl/tools/recommend/3cc41650-ddcf-11e4-9ae3-bc305bedc3f8>                                       |
| /touroperators                      | Touroperator configuration (names, blacklist, ..)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | <https://api.elmar.nl/tools/touroperators>                                                                        |
| /refunds/<id>                       | Get refund details for refund <id>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | <https://api.acc.elmar.nl/tools/refunds/1961>                                                                     |
| /refunds/user\_service\_id/<uuid>   | Get all refunds for user service ID <uuid>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | <https://api.acc.elmar.nl/tools/refunds/user_service_id/698cbcc9-dcdf-4b41-8673-9a25eee61045>                     |
| /vouchers/<code>                    | Get voucher details for voucher code <code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | <https://api.acc.elmar.nl/tools/vouchers/714277B2>                                                                |
| /vouchers/user\_service\_id/<uuid>  | Get all vouchers for user service ID <uuid>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | <https://api.acc.elmar.nl/tools/vouchers/user_service_id/698cbcc9-dcdf-4b41-8673-9a25eee61045>                    |
| POST /vouchers/<code>/refund        | Convert a voucher to a refund. <br/> Optional parameters: "iban": specify a (different) bank account to be used. Either an IBAN or a preexisting non-iDEAL Ogone/Adyen payment is required. This will be determined automatically. If neither can be found, a 409 error is returned and the request can be retried with a specified IBAN. "bank\_name": specify the name on the bank account when supplying an IBAN. Has no effect for API-based refunds (ogone/adyen). Will be determined automatically if not specified (from payment information or mainbooker name). |                                                                                                                   |

##### Image Sync options

|  option       |  values                |  function                                                                                                                                                |
|:--------------|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| accommodation | uuid                   | Run the image sync only for a specific accommodation, specified by ID. Use this in combination with force=true to fix accommodations with broken images. |
| async         | true                   | Don't block until the operation is finished, immediately return. Ignored for 'clean' and 'size' parameters.                                              |
| clean         | true                   | Clean up old images in the filesystem that are no longer in the database                                                                                 |
| elmarphotos   | true/false             | When true, only process elmar photos. When false, ignore elmar photos.                                                                                   |
| force         | true                   | Redownload already downloaded images. Still skips images that are smaller after download.                                                                |
| geonames      | true                   | Only process geonames images                                                                                                                             |
| recheck       | hours                  | Images are rechecked if they are changed within this time period, even when they are already downloaded. Default 12 hours.                               |
| size          | valid size, e.g. 520   | Reprocess all images for the given size                                                                                                                  |
| touroperators | TO brand code, e.g. HI | Only process specific touroperator brands, seperated by comma.                                                                                           |
| url           | url                    | Download 1 single image to the filesystem.                                                                                                               |

##### Newsletter subscribe options

|  option    |  description                                   |
|:-----------|:-----------------------------------------------|
| email      | The customer's email address (mandatory)       |
| firstname  | Customer's first name (optional)               |
| surname    | Customer's surname (optional)                  |
| country    | Customer's countrycode of residence (optional) |

##### Automated export

[Tools automated export](Tools%20API/Tools%20automated%20export.md)
