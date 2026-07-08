# QA Strategy — Online Event Registration Platform

## 1. Types of Testing

| Type | Why It Matters for This App |
|------|-----------------------------|
| **Functional** | The core user journey (register account → log in → browse events → register for event → pay → receive confirmation → view history) must work end-to-end. A single broken step blocks revenue. |
| **Integration** | Payment processing, event registration, and confirmation email depend on multiple services communicating correctly. The payment-to-registration handoff is the highest-risk integration point — a successful charge with no registration record is a support escalation. |
| **API** | Six REST endpoints underpin the entire frontend. Validating contracts (status codes, payload shapes, auth enforcement) at the API layer catches issues faster and cheaper than UI tests. |
| **Regression** | As the first release, the regression suite is small but critical. Every bug fix before launch must be verified against the existing happy-path flows to prevent whack-a-mole regressions. |
| **Security (lite)** | Auth token handling, session expiry during checkout, and payment input sanitization are must-checks. Full penetration testing is out of scope for a solo QA engineer at launch, but OWASP top-10 spot checks on auth and injection are non-negotiable. |
| **Performance (lite)** | Event browse pages with large event lists and concurrent registration spikes (e.g., a popular event dropping) can expose slow queries or race conditions. Basic load profiling of the events list and registration endpoint under modest concurrency is warranted. |
| **Cross-browser** | Registration and payment forms must render and submit correctly on Chrome, Firefox, and Safari. Edge cases like autofill behavior on payment forms vary across browsers. |

## 2. Feature Prioritization

Ordered by **user journey position × revenue impact**:

1. **User Registration & Login** — Gate to everything. If users can't create accounts or authenticate, zero downstream usage.
2. **Event Browsing** — Users must find and view events to register. Incorrect event data (wrong dates, capacities) erodes trust immediately.
3. **Event Registration** — The primary conversion action. Must handle capacity limits correctly and prevent duplicate registrations without losing legitimate ones.
4. **Payment** — Directly tied to revenue. Simulated for now, but the flow must be airtight: correct amount, idempotent submissions, clear error states for declined/timed-out payments.
5. **Confirmation Email** — Post-payment trust signal. A missing or duplicate confirmation email generates support tickets and user anxiety.
6. **Registration History** — Lower urgency but important for user self-service. Incorrect history (missing registrations, wrong payment status) erodes confidence.

## 3. Highest-Risk Areas

- **Payment → Registration consistency**: If the payment service succeeds but the registration write fails (or vice versa), the user is either charged without access or registered without payment. This requires transactional guarantees or compensating actions.
- **Concurrent registration for limited-capacity events**: Two users registering for the last seat simultaneously could oversell. Requires atomic capacity checks.
- **Email delivery reliability**: Third-party email services have transient failures. Retry logic, dead-letter handling, and duplicate-send prevention must all be verified.
- **Session handling during checkout**: If a user's session expires between selecting an event and completing payment, the registration and payment state can become orphaned.
- **Idempotency of payment submission**: Double-clicks, browser refreshes, or network retries on the payment endpoint could create duplicate charges if the backend isn't idempotent.

## 4. Release Criteria

| Criterion | Measure |
|-----------|---------|
| Zero P1 (critical) bugs open | No blocking defects in registration, login, payment, or confirmation flows |
| Critical path automated and green | End-to-end happy-path test (register → login → browse → register for event → pay → confirm) passing in CI |
| Zero-flakiness CI automation | Test suite passes 100% of the time in headless CI environments without reliance on hardcoded `time.sleep()` |
| API contract tests passing | All 21 Postman/Newman assertions green against the live API |
| Cross-browser smoke pass | Manual smoke of registration + payment on Chrome, Firefox|
| Rollback plan documented | Documented procedure to revert deployment within 15 minutes if a P1 is discovered post-launch |
| Email delivery verified | At least one end-to-end confirmation email received in a real inbox (not just API-level) in staging |


## 5. Assumptions

- Payment is **simulated** — no real payment gateway or money movement. Testing focuses on flow correctness, not PCI compliance.
- Single deployment environment (staging → production). No blue-green or canary infrastructure.
- No existing load testing infrastructure or baseline performance metrics to compare against.
- Email service is a third-party integration (e.g., SendGrid, SES) — we can test send calls but not inbox delivery at scale.
- The platform is web-only for launch; no native mobile apps.
- I am the sole QA engineer. Testing scope is bounded by one person's throughput over the available timeline.

## 6. Risk-Based Thinking: What I Would NOT Test Before a Time-Constrained Launch

| Deliberately Skipped | Reasoning |
|----------------------|-----------|
| **Full accessibility audit (WCAG AA)** | Important for inclusivity and legal compliance, but a comprehensive audit requires specialized tooling and takes days. I would schedule this for sprint 2 and limit launch-day checks to keyboard navigability of the checkout flow. |
| **Exhaustive performance/load testing** | Without baseline metrics or load infrastructure, a full load test is not achievable before launch. I'd run a quick smoke under 50 concurrent users on the registration endpoint to catch obvious bottlenecks, but defer capacity planning to post-launch. |
| **Internationalization / localization** | If the app launches in a single locale, i18n testing is deferred entirely. Currency formatting in payment is the one exception I'd spot-check. |
| **Legacy browser support (IE, old Edge)** | Market share too small to justify blocking launch. Tested on current Chrome, Firefox, Safari only. |
| **Admin/back-office workflows** | User-facing flows are the revenue path. Admin tooling bugs are inconvenient but not launch-blocking. |

This is a tradeoff, not a shortcut — each skipped area is tracked as a known-risk item with a planned follow-up date, not silently ignored.
