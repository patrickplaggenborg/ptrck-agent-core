
[Tools API](../Tools%20API.md)

# Tools automated export

The export function in Tools Portal can be automated (e.g. for scripting or daily export to an external system). In addition to access by the supplied forms, the most important endpoints support JSON output and GET requests. It is intended for advanced users only.

### Endpoints

|                                                               |                   |
|:--------------------------------------------------------------|:------------------|
| https://tools.elmar.nl/export/accommodations.json             | Accommodations    |
| https://tools.elmar.nl/export/touroperatoraccommodations.json | TO Accommodations |
| https://tools.elmar.nl/export/bookings.json                   | Bookings          |
| https://tools.elmar.nl/export/customers.json                  | Customers         |
| https://tools.elmar.nl/export/insurances.json                 | Insurances        |
| https://tools.elmar.nl/export/refunds.json                    | Refunds           |

### Parameters

All endpoints need a list of fields to export. Without this, the export will be empty. Fields can be supplied as fields[]=field1&fields[]=field2. Since the list of fields is quite long, changes often, and this function is only for advanced users, the field names need to be looked up in the Tools export utility by inspecting elements with the browser: <https://tools.elmar.nl/export>.  
The filters listed here can be used as well by supplying the name=value pairs as query parameters, e.g. filters[]=live for the accommodations endpoint.  
The names for JSON fields are the same as for the CSV version. Language can be selected with locale=<code> (e.g. locale=en).

### Request examples

|                            |                                                                                                                                                  |
|:---------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| Confirmed bookings in 2018 | https://tools.elmar.nl/export/bookings.json?fields[]=reservationnumber&filters[]=confirmed&bookingdate=2018-01-01&bookingdate\_before=2019-01-01 |
| Live accommodations        | https://tools.elmar.nl/export/accommodations.json?fields[]=name&filters[]=live                                                                   |
