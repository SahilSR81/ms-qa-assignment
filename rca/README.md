# Root Cause Analysis — Online Event Registration Platform

*See [Sample Bug Report](sample-bug-report.md) for Scenario 1 written as a proper ticket.*

---

## Scenario 1: "My payment went through but my registration never showed up."

### How I'd Investigate

First, I'd find the user's `transactionId` from the payment record and check if a matching `registrationId` exists. If payment exists but registration doesn't, there's a data inconsistency between the two services. The question is what broke in the handoff.

### What I'd Collect

- User's `userId`, `email`, and payment timestamp
- The `transactionId` (from their confirmation screen or email if they got one)
- The `eventId` they were trying to register for
- Any `registrationId` that might exist in a "pending" state
- HTTP response they got from `/api/payment`
- Browser console / network tab errors

### Logs and Systems I'd Inspect

- **Payment service logs** — Was the payment actually committed (not just acknowledged)? Look for the `transactionId` in a `completed` state.
- **Registration service logs** — Any write attempt for this user + event around the payment timestamp? Errors, timeouts, constraint violations?
- **Message queue** (if payment and registration talk async) — Check for unprocessed or dead-lettered messages with this `registrationId`.
- **Database** — Query `payments` for the transaction and `registrations` for any matching record. Look for orphaned records.
- **API gateway / load balancer logs** — Any 5xx or timeouts on the registration write that happened after payment succeeded?

### Possible Root Causes

1. **Non-atomic operation**: Payment commits first, then tries to create the registration as a separate step. If the registration write fails (DB timeout, crash, constraint violation), the payment is already committed with no rollback. User is charged but has no ticket.
2. **Async message lost**: Registration creation is triggered by a message from the payment service. A transient broker failure or consumer crash before ACK could lose the message. Payment committed, message fired, consumer never processed it.
3. **Race condition on capacity**: Event hit capacity right after payment but before registration write. Registration service rejected it with 422, but payment had already committed. The error was swallowed or the frontend only showed payment success.

### How I'd Verify Before Reporting

- Cross-reference `transactionId` in payments DB with registrations table. Transaction exists but no registration? Confirmed.
- Check registration service error logs for the timestamp. 500 or timeout? Supports hypothesis #1.
- Check message queue dead-letter queue for this registration. If found, supports hypothesis #2.
- Check if event was at capacity at payment time. If `registered == capacity`, supports hypothesis #3.
- File the bug with: transactionId, missing registrationId, log evidence, and a fix suggestion (e.g., wrap in a saga/transaction, or add a reconciliation job that auto-refunds orphaned payments).

---

## Scenario 2: Some users randomly get duplicate confirmation emails. Can't reproduce consistently.

### How I'd Investigate

Intermittent duplicates without a clear pattern usually mean a retry mechanism firing when it shouldn't, or a race condition in the email pipeline. First thing: check the duplicates — are they byte-identical? Different `Message-ID` headers? Seconds apart or minutes apart? The time gap is a big clue.

### What I'd Collect

- List of affected `registrationId`s and their user/email
- For each duplicate: exact send timestamps (from email service logs, not inbox), `Message-ID` headers, whether the bodies match
- Time gap between sends (seconds → retry; minutes/hours → re-triggered)
- Any common pattern: same event, same time window, same browser?
- Email service delivery status logs (accepted, delivered, bounced, retried)

### Logs and Systems I'd Inspect

- **Email service dashboard (SendGrid/SES)** — Filter by recipient. Two distinct API calls (different request IDs) or did the service itself retry?
- **App logs for email module** — Search for the `registrationId` and count how many times the send function was called. If called twice, bug is in the app. If once, bug is in the email service's retry behavior.
- **Message queue consumer logs** — If email sending is async, was the message delivered twice? (Consumer didn't ACK before timeout, broker redelivered.)
- **Payment webhook logs** — If email is triggered by a webhook callback, did the payment provider send duplicate webhook events? Common with Stripe/PayPal under network issues.

### Possible Root Causes

1. **Message broker redelivery**: Consumer sends the email but crashes or times out before ACKing. Broker redelivers, consumer sends another email. Explains intermittency — only happens when consumer is slow or under load.
2. **Duplicate payment webhooks**: Payment provider retries webhook because the app's handler responded slowly or with an error. Each webhook call triggers a new confirmation email. No idempotency check on the webhook payload.
3. **Frontend double-submit**: User double-clicks the payment button, creating two payment requests that both succeed (no idempotency key). Each successful payment triggers its own email. Correlates with users on slow connections.

### How I'd Verify Before Reporting

- Pull email service send logs for 5-10 affected users. Two distinct API calls per registration (different request IDs, seconds apart) = bug is in the app, not the email provider.
- Check message queue delivery count. Count > 1 supports hypothesis #1.
- Check payment provider webhook delivery log. Duplicate webhooks with same event ID but different delivery attempt IDs supports hypothesis #2.
- Check app server access logs for duplicate `POST /api/payment` from the same user within 5 seconds. Found? Supports hypothesis #3.
- Regardless of the root cause, the fix is an **idempotency guard**: check a `confirmation_sent` flag on the registration before sending. Only send if false, then set it to true atomically.

---

## Scenario 3: App gets noticeably slower after browsing events for a few minutes.

### How I'd Investigate

Slowdown that gets worse during a single session means something is accumulating. The question is **where** — frontend, backend, database, browser, or network. I'd check all five.

---

#### Frontend

**What to check:**
- Browser DevTools Performance tab: record 2 minutes of browsing. Look at JS heap size, DOM node count, task durations.
- Memory tab: take heap snapshots at 1 min, 3 min, 5 min. Compare retained objects. Look for detached DOM nodes or growing arrays.
- React DevTools (if applicable): check if components mount on each page visit but never unmount (modals, etc. piling up).

**Possible causes:**
- **Memory leak from event listeners**: Each navigation adds new listeners (scroll, resize, WebSocket) that never get cleaned up. After many navigations, hundreds of orphaned listeners slow garbage collection.
- **Unbounded DOM growth**: SPA appends event cards on "load more" without virtualizing the list. After a few minutes the DOM has thousands of nodes, layout/paint become slow.

---

#### Backend

**What to check:**
- Server metrics (CPU, memory, thread pool) over the session. Is the server slowing for everyone or just this user?
- Response times for `GET /api/events` over time. If it increases for this user's token but not others, the issue is session-scoped.
- App logs for increasing query complexity or N+1 patterns triggered by session state.

**Possible causes:**
- **Session state bloat**: Server stores browsing history in the session. As user browses more events, the session object grows, serialization gets slower.
- **Unoptimized filters**: Frontend sends increasingly complex "exclude previously viewed" filters. Each request has a bigger exclusion list.

---

#### Database

**What to check:**
- Slow query logs during the affected window. Are specific queries taking longer?
- Connection pool metrics: pool getting exhausted? Connections not being returned?
- Execution plans for events listing query. Full table scan?

**Possible causes:**
- **Connection pool exhaustion**: Connections opened but not properly closed after each API call. Pool fills up, subsequent requests wait, latency goes up.
- **Lock contention**: Reads on events table competing with writes (registration count updates from other users) causing increasing wait times.

---

#### Browser

**What to check:**
- Chrome's Task Manager (`Shift+Esc`): monitor tab memory and CPU over time. Steady climb = client-side leak.
- Service Worker / Cache Storage: caching every API response without eviction?
- IndexedDB / localStorage: app writing state on every navigation, storage growing?

**Possible causes:**
- **Service Worker cache bloat**: Cache-first strategy caches every event detail request. After 50+ events, cache has hundreds of entries, matching gets slower.
- **Browser extension interference**: Ad blocker or analytics extension intercepts every request. Overhead grows with request count.

---

#### Network

**What to check:**
- DevTools Network tab: number of concurrent pending requests growing over time (long-polling connections never closed)?
- WebSocket connections opened for live updates but never closed on navigation away.
- DNS resolution times, TCP connection reuse.

**Possible causes:**
- **WebSocket leak**: Each event detail page opens a WebSocket for live attendance. Navigating away doesn't close it. After a few minutes, dozens of open sockets consume file descriptors.
- **Excessive polling**: `setInterval`-based polling never cleared on unmount. Multiple overlapping intervals fire network requests. After 5 minutes, dozens of intervals firing simultaneously.

### How I'd Verify Before Reporting

- **Frontend leak**: Heap snapshots at T=0, T=3min, T=6min. Memory grows linearly with no plateau = frontend leak. Identify retaining object via snapshot comparison.
- **Backend**: Compare `GET /api/events` response times at T=0 vs T=5min for same user and a fresh user. If fresh user is fast, issue is session-scoped.
- **Database**: Run slow query log analysis. No slow queries? Rule out DB.
- **Browser**: Test in incognito with all extensions disabled. If slowdown disappears, it's extension-related. If it persists, compare Chrome vs Firefox.
- **Network**: In DevTools Network tab, sort by Connection ID and count unique connections. Count growing without connections closing = connection leak.
