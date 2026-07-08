# Test Cases — Online Event Registration Platform

## How I Designed These

For User Registration and Login I used UI-based test cases since the wireframes were clear and auth is the main entry point. For post-login flows (Event Registration, Payment, Confirmation Email), I used API-based tests since there weren't clear UI wireframes for those features. This way I get coverage at both layers.

---

### Module: User Registration

**TC-UR-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-UR-01 |
| **Test Scenario** | Successful registration with valid name, email, and password |
| **Preconditions** | User is on registration page; email `newuser@example.com` is not registered yet |
| **Test Steps** | 1. Go to registration page. 2. Enter "Alice Johnson" in Name. 3. Enter "newuser@example.com" in Email. 4. Enter "SecurePass123!" in Password. 5. Click "Register". |
| **Expected Result** | Account created. Returns 201 with a `userId`. User is redirected to login or sees a success message. |
| **Priority** | P1 |

**TC-UR-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-UR-02 |
| **Test Scenario** | Registration rejected when email is already taken |
| **Preconditions** | User with email `existing@example.com` already exists |
| **Test Steps** | 1. Go to registration page. 2. Enter "Bob Smith" in Name. 3. Enter "existing@example.com" in Email. 4. Enter "AnotherPass456!" in Password. 5. Click "Register". |
| **Expected Result** | Returns 409 Conflict. Error says email is already registered. No duplicate account. |
| **Priority** | P2 |

**TC-UR-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-UR-03 |
| **Test Scenario** | Registration with whitespace-only password (edge case: passes "non-empty" check but is useless) |
| **Preconditions** | User is on registration page |
| **Test Steps** | 1. Go to registration page. 2. Enter "Eve Blank" in Name. 3. Enter "eve@example.com" in Email. 4. Enter "     " (five spaces) in Password. 5. Click "Register". |
| **Expected Result** | Returns 400 Bad Request. Error says invalid password. Whitespace-only password is rejected. |
| **Priority** | P2 |

---

### Module: Login

**TC-LG-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-LG-01 |
| **Test Scenario** | Successful login returns a JWT token |
| **Preconditions** | Account with `user@example.com` / `password123` exists |
| **Test Steps** | 1. Go to login page. 2. Enter "user@example.com" in Email. 3. Enter "password123" in Password. 4. Click "Login". |
| **Expected Result** | Returns 200 OK with a valid JWT `token`. User is redirected to events page. Session created. |
| **Priority** | P1 |

**TC-LG-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-LG-02 |
| **Test Scenario** | Login fails with wrong password, no token leaked |
| **Preconditions** | Account with email `user@example.com` exists |
| **Test Steps** | 1. Go to login page. 2. Enter "user@example.com" in Email. 3. Enter "wrong_password" in Password. 4. Click "Login". |
| **Expected Result** | Returns 401 Unauthorized with "Invalid credentials". No `token` field in response. No session created. |
| **Priority** | P1 |

**TC-LG-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-LG-03 |
| **Test Scenario** | Session token expires during checkout (edge case: user mid-payment when token dies) |
| **Preconditions** | User logged in, on payment page. JWT near expiry (or TTL shortened for test). |
| **Test Steps** | 1. Log in and register for an event. 2. Go to payment page. 3. Wait for token to expire. 4. Submit payment. |
| **Expected Result** | Payment returns 401. User is redirected to login with "Session expired" message. Registration is preserved so user doesn't have to re-register. |
| **Priority** | P2 |

---

### Module: Event Registration

**TC-ER-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-ER-01 |
| **Test Scenario** | Authenticated user registers for an available event |
| **Preconditions** | User logged in with valid token. Event "event_999" has free spots. |
| **Test Steps** | 1. Call `GET /api/events`. 2. Pick first event. 3. Call `POST /api/events/register` with `{"eventId": "event_999"}` and Bearer token. |
| **Expected Result** | Returns 200 OK with a `registrationId` and success message. Event's `registered` count goes up by 1. |
| **Priority** | P1 |

**TC-ER-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-ER-02 |
| **Test Scenario** | User tries to register for the same event twice |
| **Preconditions** | User logged in. Already registered for "event_999". |
| **Test Steps** | 1. Call `POST /api/events/register` with `{"eventId": "event_999"}` (same event). |
| **Expected Result** | Returns 409 Conflict with error containing "already". No duplicate registration. Count doesn't change. |
| **Priority** | P2 |

**TC-ER-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-ER-03 |
| **Test Scenario** | Registration attempt when event is completely full (capacity == registered) |
| **Preconditions** | User logged in. Event "event_full" has capacity 50 and 50 registered. |
| **Test Steps** | 1. Call `POST /api/events/register` with `{"eventId": "event_full"}`. |
| **Expected Result** | Returns 422 Unprocessable Entity with error saying event is full. No registration. No charge. |
| **Priority** | P1 |

---

### Module: Payment

**TC-PM-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-01 |
| **Test Scenario** | Successful payment for a valid registration |
| **Preconditions** | User logged in. Has a valid `registrationId`. |
| **Test Steps** | 1. Call `POST /api/payment` with `{"registrationId": "reg_xyz789", "amount": 49.99, "currency": "USD", "paymentMethod": "credit_card"}` and Bearer token. |
| **Expected Result** | Returns 200 OK with a `transactionId` and success message. Registration status updates to "paid". |
| **Priority** | P1 |

**TC-PM-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-02 |
| **Test Scenario** | Payment with negative amount is rejected |
| **Preconditions** | User logged in with a valid registration. |
| **Test Steps** | 1. Call `POST /api/payment` with `{"registrationId": "reg_xyz789", "amount": -10, "currency": "USD", "paymentMethod": "credit_card"}`. |
| **Expected Result** | Returns 422 with error about "amount". No transaction created. |
| **Priority** | P2 |

**TC-PM-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-03 |
| **Test Scenario** | Payment times out after submission but before confirmation (edge case: network interruption) |
| **Preconditions** | User logged in with valid registrationId. Network conditions cause timeout after request sent but before response received. |
| **Test Steps** | 1. Call `POST /api/payment` with valid data. 2. Simulate timeout (e.g., proxy throttling). 3. Check registration status via `GET /api/registrations`. |
| **Expected Result** | If payment processed server-side: registration shows "paid", retry returns idempotent success (no double charge). If not processed: shows "pending", user can retry safely. Must never leave user in "charged but unpaid" limbo. |
| **Priority** | P1 |

**TC-PM-04**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-04 |
| **Test Scenario** | Same payment submitted twice for the same registration (idempotency check) |
| **Preconditions** | User logged in with a valid registrationId. First payment already succeeded. |
| **Test Steps** | 1. Call `POST /api/payment` with same `registrationId`, `amount`, `currency`, `paymentMethod` as the first successful payment. |
| **Expected Result** | Returns 200 OK with the same `transactionId` as the first payment (not a new one). Registration status stays "paid". User is not charged twice. |
| **Priority** | P1 |

**TC-PM-05**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-05 |
| **Test Scenario** | Payment attempted with a registrationId that doesn't exist |
| **Preconditions** | User logged in. No registration exists for the given ID. |
| **Test Steps** | 1. Call `POST /api/payment` with `{"registrationId": "reg_nonexistent", "amount": 49.99, "currency": "USD", "paymentMethod": "credit_card"}`. |
| **Expected Result** | Returns 404 Not Found with error saying registration doesn't exist. No transaction created. System handles it gracefully (no stack trace or 500). |
| **Priority** | P1 |

---

### Module: Confirmation Email

**TC-CE-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-CE-01 |
| **Test Scenario** | Confirmation email received after successful payment |
| **Preconditions** | User registered, logged in, completed registration + payment. |
| **Test Steps** | 1. Complete full flow. 2. Check email inbox within 5 minutes. |
| **Expected Result** | Exactly one email received. Contains: event title, date/time, registration ID, transaction ID, amount paid. From address and subject are correctly branded. |
| **Priority** | P1 |

**TC-CE-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-CE-02 |
| **Test Scenario** | No duplicate confirmation emails for a single payment |
| **Preconditions** | User completed one registration + one payment. Email service is working. |
| **Test Steps** | 1. Complete registration + payment. 2. Monitor inbox for 10 minutes. 3. Count emails for this registrationId. |
| **Expected Result** | Exactly one email. Email service logs show a single send attempt for this registrationId. |
| **Priority** | P2 |

**TC-CE-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-CE-03 |
| **Test Scenario** | Confirmation email when email service has a brief outage (edge case: transient failure) |
| **Preconditions** | User completed registration + payment. Email service returns 503 on first attempt (simulated). |
| **Test Steps** | 1. Complete flow while email service is down. 2. Restore service after 30 seconds. 3. Monitor inbox for 5 minutes. |
| **Expected Result** | System retries and email is delivered once service recovers. No silent failures — either delivered on retry or user is notified of delay. No duplicate emails from retry cycle. |
| **Priority** | P2 |

---

## Summary

**Total: 17 test cases** (TC-UR-01 through TC-CE-03)

- User Registration: 3
- Login: 3
- Event Registration: 3
- Payment: 5 (highest risk area per QA strategy)
- Confirmation Email: 3

---

## Prioritization: If Launch Is Tomorrow and I Can Only Run 5 Tests

| Rank | Test ID | Why This One |
|:----:|---------|--------------|
| 1 | **TC-LG-01** | Login is the gate to everything. If login breaks, nobody can do anything. Single point of failure. |
| 2 | **TC-ER-01** | Event registration is why users come here. If this breaks, there's no revenue. |
| 3 | **TC-PM-01** | Payment is where the money comes from. Broken payment after registration = zero revenue from converted users. |
| 4 | **TC-PM-03** | Payment timeout is the riskiest edge case. Double-charge or "paid but no registration" = immediate support escalation and potential chargebacks. Worse than a clean failure because the user is stuck guessing. |
| 5 | **TC-CE-01** | Confirmation email is the user's receipt. Without it, support gets flooded with "did my registration work?" questions — even when everything worked fine. Cheapest way to cut Day 1 support load. |

**Why these 5:** They cover the full happy-path revenue journey (login → register → pay → confirm) plus the most dangerous failure mode (payment timeout). Negative tests and duplicate prevention (TC-UR-02, TC-ER-02, TC-PM-02) are important but not launch-blocking — a duplicate registration is a data quality problem, not a "platform is down" problem. The capacity edge case (TC-ER-03) matters but is unlikely on Day 1 when registration counts are low.

---

## Test Coverage Traceability

| Test ID | Module | Scenario | Method |
|---------|--------|----------|--------|
| TC-UR-01 | User Registration | Successful registration | UI |
| TC-UR-02 | User Registration | Duplicate email rejection | UI |
| TC-UR-03 | User Registration | Whitespace password rejection | UI |
| TC-LG-01 | Login | Successful login (returns JWT) | UI |
| TC-LG-02 | Login | Incorrect password rejection | UI |
| TC-LG-03 | Login | Session expiry during checkout | API |
| TC-ER-01 | Event Registration | Successful registration | API |
| TC-ER-02 | Event Registration | Duplicate registration rejection | API |
| TC-ER-03 | Event Registration | Registration at zero capacity | API |
| TC-PM-01 | Payment | Successful payment | API |
| TC-PM-02 | Payment | Negative amount rejection | API |
| TC-PM-03 | Payment | Payment network timeout | Manual |
| TC-PM-04 | Payment | Payment idempotency (duplicate submission) | API |
| TC-PM-05 | Payment | Non-existent registrationId | API |
| TC-CE-01 | Confirmation Email | Successful email delivery | API |
| TC-CE-02 | Confirmation Email | No duplicate emails | API |
| TC-CE-03 | Confirmation Email | Email service outage retry | API |
