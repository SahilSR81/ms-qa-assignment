# QA Strategy — Online Event Registration Platform

## 1. Types of Testing

| Type | Why It Matters |
|------|----------------|
| **Functional** | The core flow (register → login → browse → register for event → pay → confirm → view history) has to work end to end. One broken step and users are stuck. |
| **Integration** | Payment, registration, and email all talk to each other. The payment-to-registration handoff is the riskiest part — a successful charge with no registration record is a support nightmare. |
| **API** | All 6 REST endpoints power the frontend. Testing contracts (status codes, payload shapes, auth) at the API layer catches bugs faster than UI tests. |
| **Regression** | Small suite for first release, but every bug fix needs to be checked against the happy path to avoid whack-a-mole regressions. |
| **Security (lite)** | Auth token handling, session expiry during checkout, payment input sanitization. Full pen testing is out of scope for a solo QA, but OWASP top-10 spot checks on auth and injection are non-negotiable. |
| **Performance (lite)** | Event browse pages with big lists and concurrent registration spikes can expose slow queries or race conditions. I'd run basic load profiling on the events list and registration endpoint. |
| **Cross-browser** | Registration and payment forms need to work on Chrome, Firefox, and Safari. Autofill behavior on payment forms varies across browsers. |

## 2. Feature Priorities

Ordered by how critical they are to the user journey and revenue:

1. **User Registration & Login** — Gate to everything. No accounts = no users.
2. **Event Browsing** — Users need to find events. Wrong dates or capacities lose trust fast.
3. **Event Registration** — The main conversion action. Must handle capacity limits and prevent duplicates without messing up legit registrations.
4. **Payment** — Where the money comes from. Even though it's simulated, the flow needs to be solid: correct amount, no double charges, clear error messages.
5. **Confirmation Email** — Post-payment trust signal. Missing or duplicate emails = support tickets.
6. **Registration History** — Lower urgency but important. Wrong history (missing registrations, incorrect payment status) hurts confidence.

## 3. Highest-Risk Areas

- **Payment → Registration consistency**: If payment succeeds but the registration write fails (or the other way around), the user is either charged with no access or registered without payment. Either is bad.
- **Concurrent registration for limited-capacity events**: Two people registering for the last seat at the same time could oversell. Needs atomic capacity checks.
- **Email delivery reliability**: Third-party email services fail sometimes. Retry logic, dead-letter handling, and duplicate prevention all need testing.
- **Session handling during checkout**: If a user's session expires between picking an event and paying, the registration and payment state can get orphaned.
- **Idempotency of payment submission**: Double-clicks, page refreshes, or network retries on the payment endpoint could charge the user twice if the backend isn't idempotent.

## 4. Release Criteria

| Criterion | Measure |
|-----------|---------|
| Zero P1 bugs open | No blocking defects in registration, login, payment, or confirmation |
| Critical path automated and passing | End-to-end happy-path test green in CI |
| Zero flakiness in CI | Test suite passes 100% in headless CI — no `time.sleep()` hacks |
| API contract tests passing | All 21 Newman assertions green against the live API |
| Cross-browser smoke pass | Manual smoke of registration + payment on Chrome, Firefox |
| Rollback plan documented | Procedure to revert deployment within 15 min if a P1 is found post-launch |
| Email delivery verified | At least one real confirmation email received in staging |

## 5. Assumptions

- Payment is **simulated** — no real money movement. Testing is about flow correctness, not PCI compliance.
- Single deployment environment (staging → production). No blue-green or canary.
- No existing load testing infrastructure or performance baselines.
- Email service is a third-party integration. I can test send calls but not inbox delivery at scale.
- Web-only for launch — no native mobile apps.
- I'm the sole QA engineer. Scope is limited by what one person can do.

## 6. What I Would NOT Test Before a Tight Launch

| Skipped | Reasoning |
|---------|-----------|
| **Full accessibility audit (WCAG AA)** | Important, but a full audit needs specialized tooling and takes days. I'd schedule it for sprint 2 and just check keyboard navigability of checkout for launch. |
| **Full performance/load testing** | No baselines or infrastructure to compare against. I'd run a quick smoke test with 50 concurrent users on registration to catch obvious issues, but defer proper load testing. |
| **Internationalization / localization** | If the app launches in one locale, i18n testing can wait. I'd spot-check currency formatting in payment. |
| **Legacy browser support (IE, old Edge)** | Too small a market share to block launch. Tested on current Chrome, Firefox, Safari only. |
| **Admin/back-office workflows** | User-facing flows are the revenue path. Admin bugs are annoying but not launch-blocking. |

This is a conscious tradeoff, not a shortcut. Each skipped area is tracked as a known risk with a follow-up date.
