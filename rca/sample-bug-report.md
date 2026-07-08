# Bug Report: Successful Payment but Missing Event Registration

**Ticket Key**: QA-104  
**Type**: Bug  
**Status**: Open  
**Priority**: Highest  
**Severity**: Critical

## Description
When a user completes a payment for an event registration, they are successfully charged, but the registration record is sometimes not created in the database. This leaves the user in an ambiguous state where they have lost money but do not hold a valid ticket for the event.

## Environment
* **Environment**: Production
* **App Version**: v1.4.2 (Backend)
* **Browser**: Reproducible across all browsers (Backend issue)
* **Date/Time Reported**: 2026-07-08T14:30:00Z

## Preconditions
1. User must be logged in.
2. User must have initiated registration for an event with available capacity.

## Steps to Reproduce
1. Log in to the application.
2. Navigate to `/events` and select an event.
3. Click "Register" and proceed to the checkout screen.
4. Enter valid credit card information.
5. Submit the payment.

*(Note: Issue is intermittent in production and appears to be caused by a race condition or non-atomic transaction during the Payment -> Registration handoff).*

## Expected Result
1. The payment is processed.
2. The `registrations` table is updated with the user and event.
3. The user is shown a success screen with their Ticket/Registration ID.
4. The user receives a confirmation email.

## Actual Result
1. The payment is processed successfully (confirmed via Stripe Dashboard / Payment DB).
2. The user sees a success screen.
3. **No registration record is created in the database.**
4. No confirmation email is sent.

## Investigation Notes & Evidence
* **Transaction ID**: `txn_9988776655`
* **User ID**: `usr_12345`
* **Event ID**: `evt_999`
* **Logs**: Payment service logs show a 200 OK for `POST /api/payment`. However, registration service logs show a `504 Gateway Timeout` or `422 Unprocessable Entity` exactly 1.2 seconds later for the same user session. 
* **Hypothesis**: The payment commit and the registration commit are not wrapped in an atomic transaction (or a distributed Saga). If the registration write fails post-payment, there is no compensating rollback or refund issued.

## Suggested Fix
1. **Short Term**: Implement an async daily reconciliation job to identify orphaned payments (payments without a matching registration ID) and automatically issue refunds.
2. **Long Term**: Refactor the checkout endpoint to use a distributed transaction pattern (e.g., Saga) or a two-phase commit so that a registration failure automatically triggers a payment void/refund before responding to the client.
