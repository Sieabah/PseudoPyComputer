## API Error Codes
- 0x0001 -> Still in queue
- 0x0002 -> Failed to inventory (retry), this error destroys your apikey
- 0x0003 -> Failed to authenticate, invalid api key
- 0x0004 -> The API key validates, but does not bind to the given serial number
- 0x0005 -> Invalid Protocol (HTTP) use HTTPS
- 0x0006 -> BadRequest, there was no metadata sent with your request
- 0x0007 -> Unsupported API Version
- 0x0008 -> Undefined api action given
- 0x0009 -> Action given in URI and JSON differ
- 0x000A -> Tried to find computer information but none could be found
- 0x000B -> The computer already exists in the inventory system, check rebind request.
- 0x000C -> There is no inventory information for the given client id (not in queue or failed).

## API Response Codes (HTTP-Based)
- 200 -> OK
- 201 -> Accepted
- 400 -> Bad Request
- 401 -> Unauthorized
- 403 -> Forbidden
- 404 -> Not Found
- 405 -> Method not allowed
- 406 -> Not Acceptable
- 500 -> Internal Server Error
- 503 -> Service Unavailable