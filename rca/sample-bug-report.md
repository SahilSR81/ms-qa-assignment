# Bug Report: Successful Payment but Missing Event Registration

**Ticket Key**: QA-104
**Type**: Bug
**Status**: Open
**Priority**: Highest
**Severity**: Critical

## Description

User completes payment but the registration record is not created in the database. They get charged but don't get a ticket.

## Environment

- **Environment**: Production
- **App Version**: v1.4.2 (Backend)
- **Browser**: All browsers (this is a backend issue)
- **Date/Time Reported**: 2026-07-08T14:30:00Z

## Preconditions

1. User must be logged in.
2. User must have started registration for an event with available capacity.

## Steps to Reproduce

1. Log in.
2. Go to `/events` and pick an event.
3. Click "Register" and proceed to checkout.
4. Enter valid credit card info.
5. Submit payment.

*(Note: This is intermittent. Likely caused by a race condition or non-atomic transaction in the Payment -> Registration handoff.)*

## Expected Result

1. Payment is processed.
2. `registrations` table gets updated with user + event.
3. User sees success screen with Registration ID.
4. Confirmation email is sent.

## Actual Result

1. Payment succeeds (confirmed in Payment DB / Stripe Dashboard).
2. User sees success screen.
3. **No registration record in the database.**
4. No confirmation email.

## Investigation Notes

- **Transaction ID**: `txn_9988776655`
- **User ID**: `usr_12345`
- **Event ID**: `evt_999`
- **Logs**: Payment service shows 200 OK for `POST /api/payment`. Registration service logs show a `504 Gateway Timeout` / `422 Unprocessable Entity` about 1.2 seconds later for the same session.
- **Hypothesis**: Payment commit and registration commit are not wrapped in a single atomic transaction (or Saga). If registration write fails after payment, there's no rollback or refund.

## Suggested Fix

1. **Short term**: Add a daily reconciliation job to find orphaned payments (paid but no matching registration) and auto-refund them.
2. **Long term**: Use a distributed transaction (Saga pattern) or two-phase commit so that a registration failure automatically voids/refunds the payment before responding to the client.
