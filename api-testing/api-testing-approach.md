# API Testing Approach — Online Event Registration Platform

## Tool Choice: Postman + Newman

This project uses **Postman** for API test design and **Newman** (Postman's open-source CLI runner) for CI execution. This is a deliberate, already-implemented choice — the full collection is at [`api-testing/postman/collection.json`](postman/collection.json) with 21 requests and automated `pm.test()` assertions.

**Why Postman + Newman over alternatives (e.g., REST Assured, pytest-requests):**

- **Postman** provides a visual interface for designing requests, inspecting responses, and writing assertions — ideal for iterating on undocumented endpoints where the contract is being inferred from behavior.
- **Newman** runs the exact same collection JSON from the command line with zero code changes, producing pass/fail exit codes that integrate directly with GitHub Actions. No separate test code to maintain.
- **Zero external account requirement**: Unlike the Postman CLI (`postman login`), Newman requires only `npm install -g newman`. A reviewer cloning this repo can run the full suite in one command without creating a Postman account or configuring API keys.
- **Token chaining** is built into the collection: Login captures the JWT → Events captures the eventId → Event Registration captures the registrationId → Payment uses it. This mirrors the real user flow and tests data flow integrity across endpoints.

The CI pipeline (`.github/workflows/api-tests.yml`) starts a lightweight mock server, runs Newman against it, and uploads the HTML report as a build artifact.

---

## Endpoint Coverage

### 1. POST /api/register

**How I would test it:**
Test the user creation flow by verifying successful registration with valid inputs, proper rejection of incomplete or duplicate requests, and correct response shapes. Since registration is the entry point to the platform, input validation is critical — a user who registers with a weak or empty password is a security liability.

**Positive test cases:**
- Register a new user with valid `name`, `email`, and `password` → 201 Created, response contains `userId` and success `message`
- Register with minimum valid field lengths (1-char name, valid email, 8-char password)

**Negative test cases:**
- Omit the `password` field entirely → 400 Bad Request with an `error` string
- Omit the `email` field → 400 Bad Request
- Submit an empty JSON body `{}` → 400 Bad Request
- Register with the same email twice → 409 Conflict with an error containing "already"

**Edge cases:**
- Register with a whitespace-only password ("     ") → should be rejected (400)
- Register with an extremely long email (> 254 characters) → should be rejected (400)
- Register with a valid email but malformed JSON body → should return 400, not 500

**Expected HTTP status codes:** `201`, `400`, `409`

**Payload validations:**
- 201 response must contain `userId` (string, non-empty) and `message` (string, contains "registered")
- 400/409 responses must contain `error` (string, non-empty)
- Response must not leak sensitive fields like `password` or internal database IDs
- `Content-Type` header must be `application/json`
- Response time should be below 2000ms

---

### 2. POST /api/login

**How I would test it:**
Validate authentication by testing valid credentials (which should return a JWT token for downstream use), invalid credentials (which must not leak tokens), and missing fields. The login endpoint is security-critical — the response on failure must be indistinguishable between "wrong password" and "user doesn't exist" to prevent user enumeration.

**Positive test cases:**
- Login with valid email and password → 200 OK, response contains `token` (non-empty string)
- Token captured from successful login can be used in subsequent authenticated requests

**Negative test cases:**
- Login with correct email but wrong password → 401 Unauthorized with `error: "Invalid credentials"`
- Login with a non-existent email → 401 (same generic error, no user enumeration)
- Omit `email` field → 400 Bad Request
- Omit `password` field → 400 Bad Request
- Send empty body → 400 Bad Request

**Edge cases:**
- Login with SQL injection payload in the email field (`' OR 1=1 --`) → must return 401, not 200 or 500
- Login with an expired or revoked account → should return 401 or 403 with a descriptive error
- Rapid-fire login attempts (brute force) → should be rate-limited (429) after N attempts

**Expected HTTP status codes:** `200`, `400`, `401`, `429` (if rate limiting exists)

**Payload validations:**
- 200 response must contain `token` (string, length > 0). Must not contain `password`.
- 401 response must contain `error` (string). Must not contain `token` — this is explicitly validated in the Postman collection to catch token leakage.
- Error messages must be generic ("Invalid credentials") — not "wrong password" or "user not found"
- Response time should be below 2000ms

---

### 3. GET /api/events

**How I would test it:**
Verify that authenticated users can retrieve the events list with correct data shapes, and that unauthenticated or malformed-token requests are properly rejected. The events list is the primary browsing interface — incorrect data (wrong dates, missing capacity) directly misleads users.

**Positive test cases:**
- Request with valid Bearer token → 200 OK, response contains `events` array
- Each event object has all required fields: `id`, `title`, `description`, `date`, `location`, `capacity`, `registered`
- `capacity` and `registered` are numbers, `date` is a valid ISO8601 string

**Negative test cases:**
- Request with no Authorization header → 401 Unauthorized with `error` field
- Request with a malformed JWT (`Bearer invalid.malformed.token`) → 401 Unauthorized
- Request with an expired token → 401 Unauthorized

**Edge cases:**
- Response when zero events exist → 200 OK with `events: []` (empty array, not null or missing key)
- Event with `registered == capacity` should still appear in the list (visible but not registerable)
- Very large event list (100+ events) → response should still complete within 2000ms

**Expected HTTP status codes:** `200`, `401`

**Payload validations:**
- `events` must be an array (not an object or null)
- Each event's `id` and `title` must be non-empty strings
- `capacity` must be a non-negative integer
- `registered` must be ≤ `capacity`
- Unauthorized responses must not contain the `events` field — validated in the collection to ensure no data leakage
- Response time below 2000ms

---

### 4. POST /api/events/register

**How I would test it:**
Test event registration by verifying the complete flow: authenticated user with a valid eventId gets a registrationId back. Then test the guardrails: missing auth, missing eventId, duplicate registration, and full-capacity events. This is the core conversion endpoint — correctness here directly affects revenue.

**Positive test cases:**
- Register for an available event with valid token and eventId → 200 OK with `registrationId` and success `message`
- The returned `registrationId` is a non-empty string that can be used in subsequent payment requests

**Negative test cases:**
- Omit eventId (send empty body `{}`) → 400 Bad Request with `error`
- No Authorization header → 401 Unauthorized with `error`
- Malformed token → 401 Unauthorized
- Register for the same event twice → 409 Conflict with error containing "already"

**Edge cases:**
- Register for an event that is at full capacity → 422 Unprocessable Entity with error indicating "full"
- Register with a non-existent eventId → should return 404 or 400 (not 500)
- Two concurrent registration requests for the last available seat → only one should succeed; the other should get 422

**Expected HTTP status codes:** `200`, `400`, `401`, `409`, `422`

**Payload validations:**
- 200 response must contain `registrationId` (string) and `message` (string, contains "registered")
- 409 response `error` must contain "already" to distinguish from other conflicts
- 400 response must clearly indicate which field is missing
- No response should leak other users' registration data
- Response time below 2000ms

---

### 5. POST /api/payment

**How I would test it:**
Validate the payment processing endpoint across the full spectrum: successful payment with all required fields, rejection of incomplete or invalid payloads, auth enforcement, and boundary amount values. Even though payment is simulated, the validation logic must be airtight — it's the template for the real payment integration.

**Positive test cases:**
- Pay with valid `registrationId`, positive `amount`, valid `currency`, and valid `paymentMethod` → 200 OK with `transactionId` and success `message`
- `transactionId` is a non-empty string

**Negative test cases:**
- Omit `amount`, `currency`, and `paymentMethod` (send only registrationId) → 400 Bad Request
- No Authorization header → 401 Unauthorized
- Malformed token → 401 Unauthorized
- Negative amount (`-10`) → 422 Unprocessable Entity with error referencing "amount"
- Zero amount (`0`) → 422 Unprocessable Entity

**Edge cases:**
- Payment with an extremely large amount (e.g., `999999999.99`) → should either succeed or return a specific validation error, not a 500
- Payment with a `registrationId` that doesn't exist → should return 404 or 400, not 200
- Payment with non-numeric amount (e.g., `"abc"`) → should return 400, not crash
- Submitting the same payment twice for the same registrationId (idempotency check) → should either return the same transactionId or reject the duplicate

**Expected HTTP status codes:** `200`, `400`, `401`, `422`

**Payload validations:**
- 200 response must contain `transactionId` (string, non-empty) and `message` (string, contains "successful")
- 422 response `error` must reference "amount" for amount validation failures
- 400 response must list missing fields or indicate which fields are required
- Response must never include raw payment method details (card number, CVV) in any response
- Response time below 2000ms

---

### 6. GET /api/registrations

**How I would test it:**
Verify that the authenticated user can retrieve their registration history with correct data shapes, and that unauthenticated requests are blocked. This endpoint should only return registrations belonging to the authenticated user — never another user's data.

**Positive test cases:**
- Request with valid Bearer token → 200 OK, response contains `registrations` array
- Each registration has `registrationId`, `eventId`, `eventTitle`, `registeredAt`, and `paymentStatus`
- After completing a registration + payment flow, the new registration appears in the list with `paymentStatus: "paid"`

**Negative test cases:**
- Request with no Authorization header → 401 Unauthorized with `error` field
- Request with malformed token → 401 Unauthorized
- Unauthorized response must not contain `registrations` data

**Edge cases:**
- New user with zero registrations → 200 OK with `registrations: []` (empty array, not 404)
- User with many registrations (50+) → response should paginate or still return within 2000ms
- `paymentStatus` should reflect the actual state: "pending" before payment, "paid" after successful payment

**Expected HTTP status codes:** `200`, `401`

**Payload validations:**
- `registrations` must be an array
- Each registration's `registeredAt` must be a valid ISO8601 timestamp
- `paymentStatus` must be one of a defined set of values (e.g., "pending", "paid", "failed")
- `eventTitle` must be a non-empty string
- Unauthorized responses must not contain `registrations` — validated explicitly in the collection
- Response time below 2000ms
