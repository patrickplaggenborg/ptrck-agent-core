
[Tools API](../../Tools%20API.md) > [Content API](../Content%20API.md)

# Marketing Content API

- [Introduction](#introduction)
- [Accommodations](#accommodations)
  - [Parameters](#parameters)
  - [Examples](#examples)
- [Bulk accommodations](#bulk-accommodations)

### Introduction

The Marketing Content API is a part of the Elmar Tools Content API service to supply HTML content for use in marketing emails.  
All API url's are GET requests and are relative to the base url:

- Production: <https://api.elmar.nl/tools/content/marketing>
- Acceptance: [https://api.acc.elmar.nl/tools/content/marketing](https://api.acc.elmar.nl/tools/content)
- Development: <http://localhost:4000/content/marketing>

### Accommodations

Accommodation blocks can be retrieved by supplying a URL to an accommodation on the VD website.

The current price will be requested from Trip-API so the rendering speed is dependent on how fast Trip-API responds to the query.

##### Parameters

|  parameter     |  usage                                                                   |  values                                     |
|:---------------|:-------------------------------------------------------------------------|:--------------------------------------------|
| url            | The url to use to determine offer information (mandatory)                |                                             |
| type           | The type of block to generate (the template to use)                      | 'small' (default) or 'wide'                 |
| title          | Override the title with the given string (e.g. title=Frankrijk)          |                                             |
| flag           | Show a country flag next to the title                                    | 'no' (default) or 'yes'                     |
| stars / rating | Show the star rating next to the title                                   | 'no' or 'yes' (default depends on template) |
| zoover         | Disable the zoover score display (only available in 'small' template)    | 'no'                                        |
| url\_extension | Extra parameters to append to the url (also known as the 'query string') |                                             |

##### Examples

<https://api.elmar.nl/tools/content/marketing/accommodations?url=http://www.vakantiediscounter.nl/egypte/rode_zee/hurghada/hotel_jasmine_palace_resort.htm?accoid=0f7398d7-2cb6-4641-8dff-73e8f69efaf2&boardingtype=AI&category=HOT&departureairport=DUS&departuredate=2016-10-10&flexibility=0&transporttype=VL&trip_duration=7&searchResultUrl=http%3A%2F%2Fwww.vakantiediscounter.nl%2Flast-minute%3Fflexibility%3D2%26holidaytype%3Dall%26sort%3Dpopularity_desc%26transporttype%3DVL%26trip_duration_range%3D6-10>

<https://api.elmar.nl/tools/content/marketing/accommodations?type=wide&url=http://www.vakantiediscounter.nl/egypte/rode_zee/hurghada/hotel_jasmine_palace_resort.htm?accoid=0f7398d7-2cb6-4641-8dff-73e8f69efaf2&boardingtype=AI&category=HOT&departureairport=DUS&departuredate=2016-10-10&flexibility=0&transporttype=VL&trip_duration=7&searchResultUrl=http%3A%2F%2Fwww.vakantiediscounter.nl%2Flast-minute%3Fflexibility%3D2%26holidaytype%3Dall%26sort%3Dpopularity_desc%26transporttype%3DVL%26trip_duration_range%3D6-10>

### Bulk accommodations

There is also an endpoint that returns the above information for all accommodations instead of just one. Example:

<https://api.elmar.nl/tools/content/marketing/accommodations/all.json?departuredate=2019-08-01&boardingtype=AI>

Some parameters as used by the vakantiediscounter website are accepted, e.g. countrycode, boardingtype, transporttype, etc. The only compulsory parameter is departuredate.
