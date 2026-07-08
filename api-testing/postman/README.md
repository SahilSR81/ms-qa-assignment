# MSAI — API Test Suite (Postman + Newman)

Postman collection for testing the MSAI event management REST API. Designed to run locally or in CI with no external accounts needed.

## What's Covered

| Endpoint | Requests | What's Tested |
|----------|----------|---------------|
| `POST /api/register` | 3 | Happy path, missing field, duplicate email |
| `POST /api/login` | 3 | Happy path (token capture), invalid credentials, missing field |
| `GET /api/events` | 3 | Happy path (event ID capture), missing token, malformed token |
| `POST /api/events/register` | 4 | Happy path (registration ID capture), missing eventId, missing token, duplicate |
| `POST /api/payment` | 5 | Happy path, missing fields, missing token, negative amount, zero amount |
| `GET /api/registrations` | 3 | Happy path, missing token, malformed token |

**Total: 21 requests across 6 endpoints**, each with `pm.test()` assertions on status code, response body fields, field types, and response time.

## Assumptions (for Undocumented Endpoints)

Only `POST /api/login` had a provided contract. I inferred the rest:

### POST /api/register
- **Request:** `{ "name": string, "email": string, "password": string }`
- **201:** `{ "message": string, "userId": string }`
- **400:** `{ "error": string }` — missing/invalid fields
- **409:** `{ "error": string }` — duplicate email

### GET /api/events
- **Auth:** Bearer token in Authorization header
- **200:** `{ "events": [{ "id": string, "title": string, "description": string, "date": ISO8601, "location": string, "capacity": number, "registered": number }] }`
- **401:** `{ "error": string }`

### POST /api/events/register
- **Request:** `{ "eventId": string }` + Bearer token
- **200:** `{ "message": string, "registrationId": string }`
- **400:** `{ "error": string }` — missing eventId
- **409:** `{ "error": string }` — already registered
- **422:** `{ "error": string }` — event is full

### POST /api/payment
- **Request:** `{ "registrationId": string, "amount": number, "currency": string, "paymentMethod": string }` + Bearer token
- **200:** `{ "message": string, "transactionId": string }`
- **400:** `{ "error": string }` — missing fields
- **422:** `{ "error": string }` — invalid amount (zero or negative)

### GET /api/registrations
- **Auth:** Bearer token required
- **200:** `{ "registrations": [{ "registrationId": string, "eventId": string, "eventTitle": string, "registeredAt": ISO8601, "paymentStatus": string }] }`
- **401:** `{ "error": string }`

## Token Chaining

The collection runs in order. Data flows like this:

```
POST /api/login (happy)
  └─► saves `token` → pm.environment.set("token", ...)
       └─► used as Bearer {{token}} in all auth'd requests

GET /api/events (happy)
  └─► saves `event_id` → pm.environment.set("event_id", ...)
       └─► used in POST /api/events/register body

POST /api/events/register (happy)
  └─► saves `registration_id` → pm.environment.set("registration_id", ...)
       └─► used in POST /api/payment body
```

No tokens or IDs are hardcoded. The environment file declares all variables empty (except `base_url` and `register_email`), and test scripts fill them at runtime.

## How to Run in Postman GUI

1. Open Postman → **Import** → drag in `collection.json` and `environment.json`
2. Select the **"MSAI - API Testing"** environment from the top-right
3. Update `base_url` if your server isn't at `http://localhost:3000`
4. Click **Runner** → select collection → select environment → **Run**

## How to Run via Newman

```bash
# Install Newman (one-time)
npm install -g newman newman-reporter-htmlextra

cd api-testing/postman

# Start mock server
node mock-server.js &
sleep 2

# Run the suite
newman run collection.json -e environment.json

# With HTML report
newman run collection.json \
  -e environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export report.html

# Stop the mock server
kill %1
```

## Why Newman Instead of Postman CLI

I chose Newman over `postman login` / `postman collection run` because:

> A reviewer cloning this repo should be able to run everything with zero account setup. Newman only needs `npm install -g newman`. The Postman CLI needs a Postman account, an API key, and cloud-synced collections — unnecessary friction for a hiring reviewer.

Newman is the open-source CLI runner. It reads the same JSON files, runs the same `pm.test()` scripts, and gives the same pass/fail results — no login required.

## CI Integration

The GitHub Actions workflow (`.github/workflows/api-tests.yml`) runs on every push/PR to `main`:

1. Checkout repo
2. Install Node.js
3. Install Newman + HTML reporter
4. Run collection from `api-testing/postman/`
5. Upload `report.html` as artifact (even on failure, via `if: always()`)

Newman exits with code 1 on any failed assertion, which fails the CI build.
