# Tools API Testing Summary

**Date:** 2026-01-07
**Environment:** ACC (`api.acc.elmar.nl`)
**Goal:** Query 10 regions with Dutch names and URL-friendly names

## Test Results

| Auth Method | Status Code | Result |
|-------------|-------------|--------|
| `X-Api-Key` header | **403** | Authenticated, but no endpoint permission |
| `Authorization: Bearer` | 401 | Not authenticated |
| Basic Auth (`-u key:`) | 401 | Not authenticated |
| No auth | 401 | Not authenticated |

## Key Findings

### 1. Correct Authentication Method
The Tools API uses **`X-Api-Key`** header (not Bearer token):
```bash
curl -H "X-Api-Key: <your-api-key>" \
     "https://api.acc.elmar.nl/tools/content/regions"
```

This was discovered by checking how n8n integrates with the Tools API.

### 2. API Key is Valid
The fact that `X-Api-Key` returns **403 Forbidden** while all other methods return **401 Unauthorized** proves:
- The key is valid and recognized by the server
- Authentication succeeds
- The key simply lacks permission for the Content API endpoint group

### 3. Network/VPN is Working
We confirmed network connectivity is fine because:
- TLS handshake completes successfully
- Server responds within ~14ms (`x-runtime: 0.011454`)
- We receive proper HTTP headers including `x-request-id`
- If it were a network issue, we'd see connection timeouts or no response at all

## What We Tested

### Initial Attempt (Python skill)
```bash
python content_api.py --env acc --locale nl regions
```
Failed with 401 because the skill was using `Authorization: Bearer` header.

### Terminal Testing
```bash
# Step 1: Set API key
export ELMAR_TOOLS_API_KEY=<key-from-.env>

# Step 2: Test with Bearer (incorrect) - got 401
curl -v -H "Authorization: Bearer $ELMAR_TOOLS_API_KEY" \
     "https://api.acc.elmar.nl/tools/content/regions"

# Step 3: Test with X-Api-Key (correct) - got 403
curl -v -H "X-Api-Key: $ELMAR_TOOLS_API_KEY" \
     "https://api.acc.elmar.nl/tools/content/regions"
```

### Comparison Test
Ran all auth methods to confirm which one is correct:
```bash
# X-Api-Key: 403 (authenticated, no permission)
curl -s -w "\nStatus: %{http_code}\n" \
     -H "X-Api-Key: $ELMAR_TOOLS_API_KEY" \
     "https://api.acc.elmar.nl/tools/content/regions" | tail -1

# Basic Auth: 401 (not authenticated)
curl -s -w "\nStatus: %{http_code}\n" \
     -u "$ELMAR_TOOLS_API_KEY:" \
     "https://api.acc.elmar.nl/tools/content/regions" | tail -1

# Bearer: 401 (not authenticated)
curl -s -w "\nStatus: %{http_code}\n" \
     -H "Authorization: Bearer $ELMAR_TOOLS_API_KEY" \
     "https://api.acc.elmar.nl/tools/content/regions" | tail -1

# No auth: 401 (not authenticated)
curl -s -w "\nStatus: %{http_code}\n" \
     "https://api.acc.elmar.nl/tools/content/regions" | tail -1
```

## Next Steps

Contact the Tools team to request **Content API** endpoint group access for your API key.

Example message:
```
Hey,

Mijn API key werkt nu (X-Api-Key header), maar ik krijg 403 Forbidden op de Content API:

curl -H "X-Api-Key: <mijn-key>" \
     "https://api.acc.elmar.nl/tools/content/regions"

HTTP/2 403 Forbidden

Kunnen jullie de Content API endpoint group enablen voor mijn key?

Thanks!
```

## Documentation Reference

From the Tools API docs:
> "Tools is protected by an API key system. Keys are generally supplied per team or application. If you don't have one, ask your team leader or the Tools team. An API key has limited access to the endpoints listed below. Only specifically enabled endpoint groups are allowed. If you're getting a 403 error (and it's not due to an IP whitelist), you may need to contact the Tools team to allow access to the endpoint for your key."

## Skills Update Needed

The `tools-api-readonly` skill scripts need to be updated to use `X-Api-Key` header instead of `Authorization: Bearer`. Current implementation in `content_api.py`:
```python
# Current (incorrect)
headers = {"Authorization": f"Bearer {api_key}"}

# Should be
headers = {"X-Api-Key": api_key}
```
