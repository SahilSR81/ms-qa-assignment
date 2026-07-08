# API Testing Approach — Online Event Registration Platform

## Tool Choice: Postman + Newman

I used **Postman** to design the API tests and **Newman** (Postman's CLI runner) for CI. The full collection is at [`api-testing/postman/collection.json`](postman/collection.json) with 21 requests and `pm.test()` assertions.

**Why Postman + Newman instead of REST Assured or pytest-requests:**

- I could visually design requests, inspect responses, and write assertions in Postman — helpful since most endpoints were undocumented and I was figuring out the contract from behavior.
- Newman runs the same collection from the command line with no code changes. Pass/fail exit codes plug straight into GitHub Actions.
- A reviewer can clone the repo and run the full suite with just `npm install -g newman` — no Postman account needed.
- Token chaining is built into the collection: Login captures JWT → Events captures eventId → Registration captures registrationId → Payment uses it. Tests data flow across endpoints.

The CI workflow (`.github/workflows/api-tests.yml`) starts a mock server, runs Newman, and uploads the HTML report.

---

## Endpoint Coverage

### 1. POST /api/register

**How I'd test it:** Check that valid data creates a user, missing/invalid data gets rejected, and duplicate emails are caught. Input validation matters here — a weak or empty password is a security problem.

**Positive cases:**
- Register with valid `name`, `email`, `password` → 201 with `userId` and success `message`
- Register with minimum valid lengths (1-char name, valid email, 8-char password)

**Negative cases:**
- Missing `password` → 400 with `error`
- Missing `email` → 400
- Empty body `{}` → 400
- Same email twice → 409 with error containing "already"

**Edge cases:**
- Whitespace-only password ("     ") → should get 400
- Email longer than 254 chars → should get 400
- Malformed JSON body → should get 400, not 500

**Expected status codes:** `201`, `400`, `409`

**Response checks:**
- 201: `userId` (non-empty string), `message` (contains "registered")
- 400/409: `error` (non-empty string)
- No sensitive fields leaked (password, internal DB IDs)
- `Content-Type: application/json`
- Response under 2000ms

---

### 2. POST /api/login

**How I'd test it:** Valid credentials should return a JWT. Invalid credentials must not leak tokens. Failure messages should be generic to prevent user enumeration.

**Positive cases:**
- Valid email + password → 200 with `token` (non-empty string)
- Captured token works in subsequent authenticated requests

**Negative cases:**
- Correct email, wrong password → 401 with "Invalid credentials"
- Non-existent email → 401 (same error, no user enumeration)
- Missing `email` → 400
- Missing `password` → 400
- Empty body → 400

**Edge cases:**
- SQL injection in email (`' OR 1=1 --`) → must return 401, not 200 or 500
- Expired or revoked account → 401 or 403
- Rapid login attempts → should be rate-limited (429) after N attempts

**Expected status codes:** `200`, `400`, `401`, `429` (if rate limiting exists)

**Response checks:**
- 200: `token` (non-empty string). No `password` field.
- 401: `error` (string). No `token` field (validated explicitly to catch token leakage).
- Error messages are generic ("Invalid credentials"), not "wrong password" or "user not found"
- Response under 2000ms

---

### 3. GET /api/events

**How I'd test it:** Auth'd users get the events list with correct data. Unauthenticated requests are rejected. Events data is the main browsing interface — bad data (wrong dates, missing capacity) misleads users.

**Positive cases:**
- Valid Bearer token → 200 with `events` array
- Each event has: `id`, `title`, `description`, `date`, `location`, `capacity`, `registered`
- `capacity` and `registered` are numbers, `date` is ISO8601

**Negative cases:**
- No Authorization header → 401 with `error`
- Malformed JWT (`Bearer invalid.token.here`) → 401
- Expired token → 401

**Edge cases:**
- Zero events exist → 200 with `events: []` (empty array, not null or missing)
- Event with `registered == capacity` still shows in list (visible but can't register)
- 100+ events → response under 2000ms

**Expected status codes:** `200`, `401`

**Response checks:**
- `events` is an array (not object or null)
- Each `id` and `title` is non-empty string
- `capacity` is non-negative integer
- `registered` ≤ `capacity`
- Unauthorized response has no `events` field (no data leakage)
- Under 2000ms

---

### 4. POST /api/events/register

**How I'd test it:** Auth'd user with valid eventId gets a registrationId. Then test the guardrails: missing auth, missing eventId, duplicates, full events.

**Positive cases:**
- Valid token + eventId → 200 with `registrationId` and success `message`
- `registrationId` is a non-empty string usable in payment requests

**Negative cases:**
- Missing eventId (empty body `{}`) → 400 with `error`
- No Authorization header → 401
- Malformed token → 401
- Same event twice → 409 with error containing "already"

**Edge cases:**
- Event at full capacity → 422 with error saying "full"
- Non-existent eventId → 404 or 400 (not 500)
- Two concurrent requests for last seat → only one succeeds, other gets 422

**Expected status codes:** `200`, `400`, `401`, `409`, `422`

**Response checks:**
- 200: `registrationId` (string), `message` (contains "registered")
- 409: `error` contains "already"
- 400: clearly indicates which field is missing
- No response leaks other users' registration data
- Under 2000ms

---

### 5. POST /api/payment

**How I'd test it:** Valid payment with all required fields returns a transactionId. Then test rejection of incomplete/invalid payloads, auth enforcement, and boundary amounts. Even though payment is simulated, the validation needs to be solid — this is the template for real payment integration.

**Positive cases:**
- Valid `registrationId`, positive `amount`, valid `currency`, valid `paymentMethod` → 200 with `transactionId` and success `message`
- `transactionId` is non-empty string

**Negative cases:**
- Missing `amount`, `currency`, `paymentMethod` (only registrationId) → 400
- No auth header → 401
- Malformed token → 401
- Negative amount (`-10`) → 422 with error referencing "amount"
- Zero amount (`0`) → 422

**Edge cases:**
- Extremely large amount (`999999999.99`) → should succeed or give validation error, not 500
- Non-existent `registrationId` → 404 or 400, not 200
- Non-numeric amount (`"abc"`) → 400, not a crash
- Same payment twice (idempotency) → should return same transactionId or reject duplicate

**Expected status codes:** `200`, `400`, `401`, `422`

**Response checks:**
- 200: `transactionId` (non-empty string), `message` (contains "successful")
- 422: `error` references "amount" for amount validation failures
- 400: lists missing fields
- Never includes raw payment details (card number, CVV)
- Under 2000ms

---

### 6. GET /api/registrations

**How I'd test it:** Auth'd user can see their registration history. Only their own registrations, never another user's data.

**Positive cases:**
- Valid Bearer token → 200 with `registrations` array
- Each registration has: `registrationId`, `eventId`, `eventTitle`, `registeredAt`, `paymentStatus`
- After registration + payment flow, new registration appears with `paymentStatus: "paid"`

**Negative cases:**
- No Authorization header → 401 with `error`
- Malformed token → 401
- Unauthorized response has no `registrations` data

**Edge cases:**
- New user with zero registrations → 200 with `registrations: []` (not 404)
- 50+ registrations → paginated or still under 2000ms
- `paymentStatus` reflects actual state: "pending" before payment, "paid" after

**Expected status codes:** `200`, `401`

**Response checks:**
- `registrations` is an array
- Each `registeredAt` is valid ISO8601
- `paymentStatus` is one of: "pending", "paid", "failed"
- `eventTitle` is non-empty string
- Unauthorized responses have no `registrations` field
- Under 2000ms
