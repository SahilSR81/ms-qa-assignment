# MeetStream AI — API Test Suite (Postman + Newman)

A production-grade Postman collection for testing the MeetStream AI event management REST API, designed to run locally or in CI with zero external account dependencies.

## What's Covered

| Endpoint | Requests | Coverage |
|----------|----------|----------|
| `POST /api/register` | 3 | Happy path, missing field, duplicate email |
| `POST /api/login` | 3 | Happy path (token capture), invalid credentials, missing field |
| `GET /api/events` | 3 | Happy path (event ID capture), missing token, malformed token |
| `POST /api/events/register` | 4 | Happy path (registration ID capture), missing eventId, missing token, duplicate registration |
| `POST /api/payment` | 5 | Happy path, missing fields, missing token, negative amount, zero amount |
| `GET /api/registrations` | 3 | Happy path, missing token, malformed token |

**Total: 21 requests across 6 endpoints**, each with specific `pm.test()` assertions on status code, response body fields, field types, and response time.

## Assumptions (Undocumented Endpoints)

Only `POST /api/login` had a provided contract. The following assumptions were made for all other endpoints and are documented in the collection description:

### POST /api/register
- **Request:** `{ "name": string, "email": string, "password": string }`
- **201:** `{ "message": string, "userId": string }`
- **400:** `{ "error": string }` — missing or invalid fields
- **409:** `{ "error": string }` — duplicate email

### GET /api/events
- **Auth:** Bearer token required in Authorization header
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

## Token Chaining Approach

The collection is designed to run sequentially. The data flow is:

```
POST /api/login (happy path)
  └─► captures `token` → pm.environment.set("token", ...)
       └─► used as `Bearer {{token}}` in all authenticated requests

GET /api/events (happy path)
  └─► captures `event_id` → pm.environment.set("event_id", ...)
       └─► used in POST /api/events/register body

POST /api/events/register (happy path)
  └─► captures `registration_id` → pm.environment.set("registration_id", ...)
       └─► used in POST /api/payment body
```

No tokens or IDs are hardcoded anywhere. The environment file declares all variables with empty initial values (except `base_url` and `register_email`), and test scripts populate them at runtime.

## How to Import & Run in Postman GUI

1. Open Postman → **Import** → drag in both `collection.json` and `environment.json`
2. Select the **"MeetStream AI - API Testing"** environment from the top-right dropdown
3. Update `base_url` in the environment if your server isn't at `http://localhost:3000`
4. Click **Runner** → select the collection → ensure the environment is selected → **Run**

## How to Run Locally via Newman

```bash
# Install Newman (one-time)
npm install -g newman newman-reporter-htmlextra

# Run the suite (from repo root)
cd api-testing/postman
newman run collection.json -e environment.json

# With HTML report
newman run collection.json \
  -e environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export report.html
```

## Why Newman over Postman CLI

This is a deliberate design choice, not an oversight:

> **A reviewer cloning this repo must be able to run the full test suite with zero external account setup.** Newman requires only `npm install -g newman` and a single command. The Postman CLI (`postman login`, `postman collection run`) requires a Postman account, an API key, and cloud-synced collections — all of which create unnecessary friction for a hiring reviewer evaluating a take-home assignment.

Newman is the open-source, standalone CLI runner maintained by the Postman team. It reads the same collection/environment JSON files, executes the same `pm.test()` scripts, and produces the same pass/fail exit codes — without requiring authentication to any external service.

## CI Integration

The GitHub Actions workflow (`.github/workflows/api-tests.yml`) runs on every push and PR to `main`:

1. Checks out the repo
2. Sets up Node.js 20
3. Installs Newman + HTML reporter globally
4. Runs the collection from `api-testing/postman/`
5. Uploads `report.html` as a build artifact (even on failure, via `if: always()`)

Newman exits with code 1 on any failed `pm.test()` assertion, which naturally fails the CI build — no `--suppress-exit-code` is used.
