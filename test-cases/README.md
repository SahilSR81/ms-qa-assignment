# Test Cases — Online Event Registration Platform

## Test Cases

## Test Design Strategy

UI flows were used for Registration and Login because authentication is a foundational user entry point where UI wireframes and requirements were clear. However, for post-login flows like Event Registration, Payment, and Confirmation Emails, automated API-based tests were selected due to the lack of UI wireframes for these specific features. This hybrid approach ensures maximum coverage across layers.

---

### Module: User Registration

**TC-UR-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-UR-01 |
| **Test Scenario** | Successful user registration with valid name, email, and password |
| **Preconditions** | User is on the registration page; email `newuser@example.com` is not already registered |
| **Test Steps** | 1. Navigate to the registration page. 2. Enter "Alice Johnson" in the Name field. 3. Enter "newuser@example.com" in the Email field. 4. Enter "SecurePass123!" in the Password field. 5. Click the "Register" button. |
| **Expected Result** | User account is created. System returns 201 with a `userId`. User is redirected to the login page or shown a success message indicating they can now log in. |
| **Priority** | P1 |

**TC-UR-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-UR-02 |
| **Test Scenario** | Registration rejected when using an email address that is already registered |
| **Preconditions** | A user with email `existing@example.com` already exists in the system |
| **Test Steps** | 1. Navigate to the registration page. 2. Enter "Bob Smith" in Name. 3. Enter "existing@example.com" in Email. 4. Enter "AnotherPass456!" in Password. 5. Click "Register". |
| **Expected Result** | Registration is rejected with a 409 Conflict status. Error message indicates the email is already registered. No duplicate account is created. |
| **Priority** | P2 |

**TC-UR-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-UR-03 |
| **Test Scenario** | Registration with a password that is only whitespace characters (edge case: input that passes "non-empty" checks but is semantically empty) |
| **Preconditions** | User is on the registration page |
| **Test Steps** | 1. Navigate to the registration page. 2. Enter "Eve Blank" in Name. 3. Enter "eve@example.com" in Email. 4. Enter "     " (five spaces) in the Password field. 5. Click "Register". |
| **Expected Result** | Registration is rejected with a 400 Bad Request. Error message indicates invalid password. A whitespace-only password must not be accepted as valid credentials. |
| **Priority** | P2 |

---

### Module: Login

**TC-LG-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-LG-01 |
| **Test Scenario** | Successful login with valid credentials returns a JWT token |
| **Preconditions** | User account with email `user@example.com` and password `password123` exists |
| **Test Steps** | 1. Navigate to the login page. 2. Enter "user@example.com" in Email. 3. Enter "password123" in Password. 4. Click "Login". |
| **Expected Result** | System returns 200 OK with a valid JWT `token` string. User is redirected to the events browsing page. Session is established. |
| **Priority** | P1 |

**TC-LG-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-LG-02 |
| **Test Scenario** | Login fails with incorrect password and does not leak authentication tokens |
| **Preconditions** | User account with email `user@example.com` exists |
| **Test Steps** | 1. Navigate to the login page. 2. Enter "user@example.com" in Email. 3. Enter "wrong_password" in Password. 4. Click "Login". |
| **Expected Result** | System returns 401 Unauthorized with a generic "Invalid credentials" error. Response body does not contain a `token` field. No session is established. |
| **Priority** | P1 |

**TC-LG-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-LG-03 |
| **Test Scenario** | Session token expires during an active checkout flow (edge case: user is mid-payment when token TTL elapses) |
| **Preconditions** | User is logged in and has navigated to the payment page for an event registration. JWT token is near expiration (or TTL is artificially shortened for test). |
| **Test Steps** | 1. Log in and register for an event. 2. Navigate to the payment page. 3. Wait for the JWT token to expire (or use a token with a very short TTL). 4. Submit the payment form. |
| **Expected Result** | Payment endpoint returns 401 Unauthorized. User is redirected to the login page with a clear message (e.g., "Session expired, please log in again"). The event registration is preserved so the user does not have to re-register after logging back in. |
| **Priority** | P2 |

---

### Module: Event Registration

**TC-ER-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-ER-01 |
| **Test Scenario** | Authenticated user successfully registers for an available event |
| **Preconditions** | User is logged in with a valid token. Event "event_999" exists with available capacity (registered < capacity). |
| **Test Steps** | 1. Call `GET /api/events` to retrieve available events. 2. Select the first event (event_999). 3. Call `POST /api/events/register` with `{ "eventId": "event_999" }` and valid Bearer token. |
| **Expected Result** | System returns 200 OK with a `registrationId` and a success message containing "registered". The event's `registered` count increments by 1. |
| **Priority** | P1 |

**TC-ER-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-ER-02 |
| **Test Scenario** | User attempts to register for the same event twice with the same account |
| **Preconditions** | User is logged in. User has already registered for event "event_999". |
| **Test Steps** | 1. Call `POST /api/events/register` with `{ "eventId": "event_999" }` (same event as previous registration). |
| **Expected Result** | System returns 409 Conflict with an error message containing "already". No duplicate registration record is created. The event's registered count does not increment. |
| **Priority** | P2 |

**TC-ER-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-ER-03 |
| **Test Scenario** | Registration attempt for an event at exactly zero remaining capacity (edge case: capacity == registered) |
| **Preconditions** | User is logged in. Event "event_full" has `capacity: 50` and `registered: 50` (zero seats remaining). |
| **Test Steps** | 1. Call `POST /api/events/register` with `{ "eventId": "event_full" }`. |
| **Expected Result** | System returns 422 Unprocessable Entity with an error message indicating the event is full. No registration is created. The user is not charged. |
| **Priority** | P1 |

---

### Module: Payment

**TC-PM-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-01 |
| **Test Scenario** | Successful payment for a valid event registration |
| **Preconditions** | User is logged in. User has a valid `registrationId` from a successful event registration. |
| **Test Steps** | 1. Call `POST /api/payment` with `{ "registrationId": "reg_xyz789", "amount": 49.99, "currency": "USD", "paymentMethod": "credit_card" }` and valid Bearer token. |
| **Expected Result** | System returns 200 OK with a `transactionId` string and a success message containing "successful". Registration status in `/api/registrations` updates to "paid". |
| **Priority** | P1 |

**TC-PM-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-02 |
| **Test Scenario** | Payment submission with a negative amount is rejected |
| **Preconditions** | User is logged in with a valid registration. |
| **Test Steps** | 1. Call `POST /api/payment` with `{ "registrationId": "reg_xyz789", "amount": -10, "currency": "USD", "paymentMethod": "credit_card" }`. |
| **Expected Result** | System returns 422 Unprocessable Entity with an error message referencing "amount". No transaction is created. |
| **Priority** | P2 |

**TC-PM-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-PM-03 |
| **Test Scenario** | Payment endpoint times out after card details are submitted but before confirmation is returned (edge case: network interruption during payment processing) |
| **Preconditions** | User is logged in. User has a valid registrationId. Network conditions are simulated to cause a timeout after the request is sent but before the response is received. |
| **Test Steps** | 1. Call `POST /api/payment` with valid payload. 2. Simulate a network timeout (e.g., via proxy throttling) after the request reaches the server but before the response returns. 3. Check the registration status via `GET /api/registrations`. |
| **Expected Result** | If the payment was processed server-side, the registration shows "paid" and retrying the payment should return an idempotent success (not a double charge). If the payment was not processed, the registration shows "pending" and the user can retry safely. The system must not leave the user in an ambiguous state where they are charged but see "unpaid". |
| **Priority** | P1 |

---

### Module: Confirmation Email

**TC-CE-01**

| Field | Value |
|-------|-------|
| **Test ID** | TC-CE-01 |
| **Test Scenario** | Confirmation email is received after successful payment for an event registration |
| **Preconditions** | User is registered and logged in with a valid email address. User has registered for an event and completed payment successfully. |
| **Test Steps** | 1. Complete the full registration + payment flow. 2. Check the email inbox associated with the registered account within 5 minutes. |
| **Expected Result** | Exactly one confirmation email is received. Email contains: event title, event date/time, registration ID, payment transaction ID, and the amount paid. The "From" address and subject line are correctly branded. |
| **Priority** | P1 |

**TC-CE-02**

| Field | Value |
|-------|-------|
| **Test ID** | TC-CE-02 |
| **Test Scenario** | No duplicate confirmation emails are sent when a user completes a single payment |
| **Preconditions** | User has completed one event registration and one payment. Email service is functioning normally. |
| **Test Steps** | 1. Complete registration and payment for a single event. 2. Monitor the email inbox for 10 minutes. 3. Count the number of confirmation emails received for this specific registrationId. |
| **Expected Result** | Exactly one confirmation email is received — not zero, not two or more. The email service's send log shows a single send attempt for this registrationId. |
| **Priority** | P2 |

**TC-CE-03**

| Field | Value |
|-------|-------|
| **Test ID** | TC-CE-03 |
| **Test Scenario** | Confirmation email delivery when the email service experiences a brief outage (edge case: transient mail service failure) |
| **Preconditions** | User has completed registration and payment. The email service is temporarily unavailable (simulated via service mock returning 503 for the first attempt). |
| **Test Steps** | 1. Complete registration and payment while the email service is returning 503. 2. Restore the email service after 30 seconds. 3. Monitor the inbox for the next 5 minutes. |
| **Expected Result** | The system retries email delivery after the transient failure. The confirmation email is eventually delivered once the service recovers. The system does not silently swallow the failure — either the email is delivered on retry or the user is notified that confirmation is delayed. No duplicate emails are sent during the retry cycle. |
| **Priority** | P2 |

---

## Test Case Count

**Total: 15 test cases** (TC-UR-01 through TC-CE-03)

- User Registration: 3
- Login: 3
- Event Registration: 3
- Payment: 3
- Confirmation Email: 3

---

## Prioritization Exercise

**Scenario:** The app launches tomorrow. Only 5 test cases can be executed. Which 5?

| Priority Rank | Test ID | Reasoning |
|:---:|---------|-----------|
| 1 | **TC-LG-01** | Login is the gateway to every authenticated action. If login fails, no user can browse events, register, or pay. This is the single point of failure for the entire platform. |
| 2 | **TC-ER-01** | Event registration is the primary conversion action — it's why users come to the platform. If this fails, there is no revenue path at all. |
| 3 | **TC-PM-01** | Payment directly generates revenue. A broken payment flow after successful registration means the business earns nothing from converted users. |
| 4 | **TC-PM-03** | Payment timeout is the highest-risk edge case for user trust and financial correctness. A double-charge or a "paid but not registered" state will generate immediate support escalations and potential chargebacks. This is more dangerous than a clean failure because the user is left uncertain. |
| 5 | **TC-CE-01** | Confirmation email is the user's receipt and proof of registration. Without it, users will flood support asking "did my registration go through?" — even if everything worked correctly. It's the cheapest way to reduce Day 1 support load. |

**Why these 5 over others:** These trace the complete happy-path revenue journey (login → register → pay → confirm) plus the single most dangerous failure mode (payment timeout ambiguity). The negative and duplicate-prevention tests (TC-UR-02, TC-ER-02, TC-PM-02) are important but are not launch-blocking — a duplicate registration is a data quality issue, not a "platform is broken" issue. The capacity edge case (TC-ER-03) is critical but is a lower-probability event on Day 1 when registration counts are low.

---

## Test Coverage Traceability

| Test ID | Module | Scenario Summary | Execution Method |
|---------|--------|------------------|------------------|
| TC-UR-01 | User Registration | Successful registration | Automated UI |
| TC-UR-02 | User Registration | Duplicate email rejection | Automated UI |
| TC-UR-03 | User Registration | Whitespace password rejection | Automated UI |
| TC-LG-01 | Login | Successful login (returns JWT) | Automated UI |
| TC-LG-02 | Login | Incorrect password rejection | Automated UI |
| TC-LG-03 | Login | Session expiry during checkout | Automated API |
| TC-ER-01 | Event Registration | Successful registration | Automated API |
| TC-ER-02 | Event Registration | Duplicate registration rejection | Automated API |
| TC-ER-03 | Event Registration | Registration at zero capacity | Automated API |
| TC-PM-01 | Payment | Successful payment | Automated API |
| TC-PM-02 | Payment | Negative amount rejection | Automated API |
| TC-PM-03 | Payment | Payment network timeout | Manual / Exploratory |
| TC-CE-01 | Confirmation Email | Successful email delivery | Automated API |
| TC-CE-02 | Confirmation Email | No duplicate emails | Automated API |
| TC-CE-03 | Confirmation Email | Email service outage retry | Automated API |
