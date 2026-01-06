
[Tools API](../Tools%20API.md)

# Content API

- [Introduction](#introduction)
  - [Language selection](#language-selection)
- [Accommodations](#accommodations)
  - [Images](#images)
  - [Trust You mappings](#trust-you-mappings)
- [Products](#products)
- [Geo](#geo)
- [Images](#images)
- [Landing Pages](#landing-pages)
- [Marketing content](#marketing-content)

### Introduction

The Content API is an Elmar Tools service to supply an easy way to query the information inside the Elmar Tools system.  
All API url's are GET requests unless specified otherwise, and are relative to the base url:

- Production: <https://api.elmar.nl/tools/content>
- Acceptance: <https://api.acc.elmar.nl/tools/content> or <https://api.acc2.elmar.nl/tools/content>
- Development: <http://localhost:4000/content>

#### Language selection

Some fields returned by the API are place names, which may have localised versions available. For example, a country has a 'name' field, which will be in the desired language when specified and available. Currently supported are nl, en and de. The default is 'nl'. If a language is requested that is not supported, the default will be returned.

Setting the desired language can be done using 2 ways: the 'Accept-Language' HTTP header, or the parameter 'locale' in the url query string (e.g. '<base\_url>?locale=de').

Note: some API's return a 'dutch\_name' field. Do not use this. It's deprecated and was kept for backwards compatibility, and may be removed at any moment. Use the above mentioned method instead to localise names (using 'nl' language code).

### Accommodations

|  API call                                        |  Description                                                                                                                       |  Example                                                                                                                                                                          |
|:-------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /accommodations                                  | Retrieve a simplified version of all accommodations                                                                                | <https://api.elmar.nl/tools/content/accommodations>                                                                                                                               |
| /accommodations?accommodations=id1,id2,...       | Retrieve a simplified version of the specified accommodations                                                                      | <https://api.elmar.nl/tools/content/accommodations?accommodations=143d2940-8f5c-11df-a2df-001c42000009,0de26440-71b7-11e1-a285-000c29b36cdf>                                      |
| /accommodations/<id>                             | Full information for a single accommodation                                                                                        | <https://api.elmar.nl/tools/content/accommodations/143d2940-8f5c-11df-a2df-001c42000009> <https://api.elmar.nl/tools/content/accommodations/0de26440-71b7-11e1-a285-000c29b36cdf> |
| /accommodations/<country>/<region>/<city>/<name> | Full information for a single accommodation, by urlfriendly name. Can respond with a 302 redirect if the resource has moved.       | <https://api.elmar.nl/tools/content/accommodations/turkije/antalya/alanya/eftalia_aytur_hotel>                                                                                    |
| /accommodations/<id>/media                       | Retrieve all media for the specified accommodation                                                                                 | <https://api.elmar.nl/tools/content/accommodations/13cf9a60-8f5c-11df-a2df-001c42000009/media>                                                                                    |
| /accommodations/media?accommodations=id1,id2,... | Retrieve accommodation media in bulk by acco id. Leave out accommodations parameter to retrieve all accos. Also available as POST. | <https://api.elmar.nl/tools/content/accommodations/media?accommodations=13cf9a60-8f5c-11df-a2df-001c42000009,1384d5c0-8f5c-11df-a2df-001c42000009>                                |

Supported parameters for single accommodations:

|  Parameter    |  Values    |  Default    |  Description                                                                                                           |
|:--------------|:-----------|:------------|:-----------------------------------------------------------------------------------------------------------------------|
| replace       | true/false | true        | Replace third party brand names and telephone numbers in the description text with our own brand name and phone number |

#### Images

Images are represented in the result by a filename only. This is because the exact url depends on the size and the intended integration. It follows this url structure:

```java
https://<base_domain>/images/cache/<size>/<filename>
```

base\_domain can be one of: api.elmar.nl, tools.vakantiediscounter.nl  
size can be one of: 70 114 164 170 230 370 520 670 970 1200

#### Trust You mappings

The following endpoint will return the combinations of accommodation ID, Trust You ID and GIATA ID:

`/accommodations/trust_you_mappings`

### Products

|  API call               |  Description                                                                         |  Example                                                                                                                  |
|:------------------------|:-------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------|
| /products(.format)      | Retrieve all products in a csv (default) or json format                              | <https://api.elmar.nl/tools/content/products?brand=SA>                                                                    |
| /products/list/<market> | Retrieve a simplified version for a specific market of the above list in json format | <https://api.elmar.nl/tools/content/products/list/NL>                                                                     |
| /products/<brand>/<id>  | Product details for the specified brand                                              | <https://api.elmar.nl/tools/content/products/AL/VLVARVAR806> <https://api.elmar.nl/tools/content/products/A1/VLVARVAR806> |

Supported parameters for bulk products:

|  Parameter    |  Values    |  Default    |  Description                                                                                               |
|:--------------|:-----------|:------------|:-----------------------------------------------------------------------------------------------------------|
| touroperator  | TO code    | null        | Only return the specified touroperator(s) (e.g. TUI, AL, ...) (separated by comma for multivalue)          |
| brand         | brand code | null        | Only return the specified touroperator brand(s) (e.g. HI, CH, A1, ...) (separated by comma for multivalue) |
| header        | true/false | false       | Add CSV header (only valid for CSV format)                                                                 |
| index         | true/false | false       | Add index to CSV rows (only valid for CSV format)                                                          |

Supported parameters for a single product:

|  Parameter    |  Values    |  Default    |  Description                                                                                                 |
|:--------------|:-----------|:------------|:-------------------------------------------------------------------------------------------------------------|
| live          | true/false | false       | Refresh product description from touroperator.                                                               |
| departuredate | yyyy-mm-dd | null        | Date to use for live descriptions. Required for certain touroperators (AL, SA, RI). Ignored when not needed. |

### Geo

|  API call                   |  Description                                                                                                                                                                    |  Example                                                                                                   |
|:----------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|
| /airports                   | List of airports                                                                                                                                                                | <https://api.elmar.nl/tools/content/airports>                                                              |
| /cities                     | City details for all cities.                                                                                                                                                    | <https://api.elmar.nl/tools/content/cities>                                                                |
| /cities/<id>                | City details. <id> can be a database id or url friendly name. Query with countrycode when possible (see below) when using url friendly name since they are not globally unique. | <https://api.elmar.nl/tools/content/cities/3117735>                                                        |
| /cities/<countrycode/<id>   | City details. <id> can be a database id or url friendly name.                                                                                                                   | <https://api.elmar.nl/tools/content/cities/ES/madrid>                                                      |
| /countries                  | Country details for all countries                                                                                                                                               | <https://api.elmar.nl/tools/content/countries>                                                             |
| /countries/<countrycode>    | Country details                                                                                                                                                                 | <https://api.elmar.nl/tools/content/countries/ES>                                                          |
| /regions                    | Region details for all regions and tourisic regions.                                                                                                                            | <https://api.elmar.nl/tools/content/regions>                                                               |
| /regions/<id>               | Geo region details by database id, or touristic region details by url friendly name.                                                                                            | <https://api.elmar.nl/tools/content/regions/tenerife> <https://api.elmar.nl/tools/content/regions/3336901> |
| /regions/<countrycode>/<id> | Region (geo/touristic) details. <id> can be a url friendly name, id (touristic only) or area code (geo only).                                                                   | <https://api.elmar.nl/tools/content/regions/ES/tenerife>                                                   |

List endpoints (without ID) support a full=true parameter, to retrieve all information on all entities at once. This is SLOW, because most of this extra information requires heavy queries. Because it's a resource drain, these endpoints are rate limited. Only one query can be run on each of them at a time. Trying to query multiple times at once will result in a 429 http error.

### Images

Images can be loaded directly without the need to query the geo endpoint. By using the url's as indicated below an image can be loaded dynamically (Tools API will figure out the image to show). Images are also available on the website domains for better website integration.

|  API call                                                    |  Description                                                                                                                                                                                                          |  Internal example                                                                                                                                                                                                   |  Public example                                                                                                        |
|:-------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------|
| /images/<country>(/<region>)(/<city>)/<size>.jpg             | Returns the image belonging to the specified geopage. Region and city are optional. Geo components can be specified in url name or object ID (mixable). Size must be a supported (prerendered) image size (e.g. 520). | <https://api.elmar.nl/tools/content/images/spanje/520.jpg> <br/> <https://api.elmar.nl/tools/content/images/ES/2593109/520.jpg>                                                                                     | <https://www.vakantiediscounter.nl/tools/content/images/spanje/520.jpg>                                                |
| /images/<country>/<region>/<city>/<accommodation>/<size>.jpg | Returns the profile image for the specified accommodation in the requested size.                                                                                                                                      | <https://api.elmar.nl/tools/content/images/spanje/regio_valencia/valencia/primus_valencia/520.jpg> <br/> <https://api.elmar.nl/tools/content/images/TR/antalya/324190/143d2940-8f5c-11df-a2df-001c42000009/520.jpg> | <https://www.vakantiediscounter.nl/tools/content/images/spanje/regio_valencia/valencia/primus_valencia/520.jpg>        |
| /images/accommodations/<id>/<size>/<number>.jpg              | Returns an image for an accommodation, where 0 is the profile image.                                                                                                                                                  | <https://api.elmar.nl/tools/content/images/accommodations/143d2940-8f5c-11df-a2df-001c42000009/520/0.jpg>                                                                                                           | <https://www.vakantiediscounter.nl/tools/content/images/accommodations/143d2940-8f5c-11df-a2df-001c42000009/520/0.jpg> |

### Landing Pages

|  API call             |  Description                                  |  Example                                                   |
|:----------------------|:----------------------------------------------|:-----------------------------------------------------------|
| /landing\_pages       | Retrieve all landing page configurations      | <https://api.elmar.nl/tools/content/landing_pages>         |
| /landing\_pages/<url> | Retrieve landing page configuration for a url | <https://api.elmar.nl/tools/content/landing_pages/turkije> |

### Marketing content

[Marketing Content API](Content%20API/Marketing%20Content%20API.md)
