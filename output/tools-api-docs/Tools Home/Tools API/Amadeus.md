
[Tools API](../Tools%20API.md)

# Amadeus

# Introduction

The Tools Amadeus API is used to interact with Amadeus for booking management. It is currently a proof of concept and not actually used in Tools itself. The current output reflects this state, and will change in the future when we implement real functionality. The result of any call is a json with the following fields:

|  **Field**       |  **Function**                                      |
|:-----------------|:---------------------------------------------------|
| result           | The output of the Amadeus API call.                |
| request.endpoint | The endpoint Tools called to retrieve this result. |
| request.method   | The HTTP method used to call the endpoint.         |
| request.body     | The body used in the request.                      |
| response.status  | The HTTP status code of the Amadeus response.      |
| response.body    | The body returned by the Amadeus API.              |
| ama\_client\_ref | The ama\_client\_ref used in the request.          |

Tools does not store any of this, it is up to the client to do this if desired.

# Endpoint overview

All endpoints are relative to the [Tools API](../Tools%20API.md).

|  **Endpoint**            |  **Parameters**                             |  **Function**                                     |
|:-------------------------|:--------------------------------------------|:--------------------------------------------------|
| GET /amadeus/<id>        | id: Amadeus ID                              | Retrieve booking data for the specified ID.       |
| GET /amadeus/pnr/<pnr>   | pnr: PNR                                    | Retrieve booking data for the specified PNR.      |
| PUT/PATCH /amadeus/<id>  | id: Amadeus ID <br/> body: JSON (see below) | Update the specified booking before it is issued. |
| POST /amadeus/<id>/issue | id: Amadeus ID                              | Issue an unissued booking.                        |
| DELETE /amadeus/<id>     | id: Amadeus ID                              | Cancel the specified booking.                     |
| GET /amadeus/queue/<id>  | id: Amadeus queue ID                        | Retrieve the contents of a queue.                 |

## Booking update options

|  **Field**    |  **Function**                                                           |
|:--------------|:------------------------------------------------------------------------|
| comments      | Add comments (a.k.a. “remarks”) to a booking. Can be a string or array. |
