# Root Cause Analysis — Online Event Registration Platform

*See the [Sample Bug Report (Jira-style)](sample-bug-report.md) for Scenario 1.*

## Scenario 1: "My payment was successful, but my event registration was never created."

### How I Would Investigate

Start by reproducing the user's exact state: locate their `transactionId` from the payment record and check whether a corresponding `registrationId` exists. If the payment record exists but the registration does not, we have a confirmed data inconsistency between the payment and registration services. The investigation focuses on what broke in the handoff between payment confirmation and registration creation.

### What Information I Would Collect

- The user's `userId`, `email`, and the timestamp of the payment attempt.
- The `transactionId` returned to the user (from their confirmation screen or email, if received).
- The `eventId` the user was attempting to register for.
- The `registrationId` that should have been created (if a pre-registration record exists in a "pending" state).
- HTTP response status and body the user's client received from `/api/payment`.
- Any client-side error logs (browser console, network tab).

### Which Logs, APIs, and Systems I Would Inspect

- **Payment service logs**: Confirm the payment was processed and committed (not just acknowledged). Look for the specific `transactionId` and verify it reached a `completed` state.
- **Registration service logs**: Search for any write attempt for this user + event combination around the payment timestamp. Look for errors, timeouts, or constraint violations.
- **Message queue / event bus** (if the architecture uses async communication between payment and registration): Check for unprocessed or dead-lettered messages containing this `registrationId`.
- **Database**: Query the `payments` table for the transaction and the `registrations` table for any record matching the user + event. Check for orphaned records.
- **API gateway / load balancer logs**: Look for 5xx responses or timeouts on the registration write that occurred after the payment succeeded.

### Possible Root Causes

1. **Non-atomic payment-registration operation**: The payment endpoint charges the user and then calls the registration service as a separate step. If the registration write fails (DB timeout, constraint violation, service crash), the payment has already been committed with no compensating rollback — leaving the user charged but unregistered.
2. **Async message dropped**: If registration creation is triggered by a message/event from the payment service, a transient message broker failure (or a consumer crash before acknowledgment) could lose the registration event. The payment committed, the message fired, but the consumer never processed it.
3. **Race condition on capacity check**: The event was at capacity when the registration write was attempted (after payment). The registration service rejected the write with a 422, but the payment service had already committed. The error was swallowed or the frontend only displayed the payment success without checking the registration response.

### How I Would Verify Before Reporting

- Cross-reference the `transactionId` in the payment DB with the `registrations` table. If the transaction exists but no registration does, the inconsistency is confirmed.
- Check registration service error logs for the exact timestamp range. If a 500 or timeout appears, it confirms hypothesis #1.
- Check the message queue dead-letter queue for unprocessed events matching this registration. If found, it confirms hypothesis #2.
- Check if the event was at capacity at the time of the payment. If `registered == capacity` at that timestamp, it confirms hypothesis #3.
- File the bug with: the specific transactionId, the missing registrationId, the log evidence showing where the handoff failed, and a recommendation (e.g., wrap payment + registration in a saga/transaction, or implement a compensation job that auto-refunds orphaned payments).

---

## Scenario 2: Some users occasionally receive duplicate confirmation emails after registering; not consistently reproducible.

### How I Would Investigate

Intermittent duplicates without a clear reproduction pattern suggest either a retry mechanism that fires when it shouldn't, or a race condition in the email-sending pipeline. I'd start by correlating the duplicated emails — are they byte-identical? Do they have different `Message-ID` headers? Are they sent seconds apart or minutes apart? The time delta between duplicates is a critical clue.

### What Information I Would Collect

- A list of affected `registrationId` values and their associated `userId`/email.
- For each duplicate pair: exact send timestamps (from the email service's send log, not the user's inbox), `Message-ID` headers, and whether the email bodies are identical.
- The time gap between duplicate sends (seconds → likely retry; minutes/hours → likely re-triggered).
- Whether affected users share any pattern: specific event, specific time window, specific browser, specific network conditions.
- The email service's delivery status logs (accepted, delivered, bounced, retried).

### Which Logs, APIs, and Systems I Would Inspect

- **Email service logs (SendGrid/SES dashboard)**: Filter by recipient email for the affected users. Check if two distinct API calls were made (two different request IDs) or if the service itself retried delivery.
- **Application logs for the email-sending module**: Search for the `registrationId` and count how many times the "send confirmation email" function was invoked. If it was called twice, the bug is in the application. If it was called once, the bug is in the email service's retry behavior.
- **Message queue consumer logs**: If email sending is async (triggered by a queue message), check if the message was delivered twice (e.g., consumer didn't ACK before timeout, so the broker redelivered).
- **Payment webhook logs**: If the email is triggered by a payment webhook callback, check if the payment provider sent duplicate webhook events (common with Stripe/PayPal under network instability).

### Possible Root Causes

1. **Message broker redelivery**: The email consumer processes the message and sends the email, but crashes or times out before acknowledging the message. The broker redelivers it, and the consumer sends a second email. This explains intermittency — it only happens when the consumer is slow or under load.
2. **Duplicate payment webhook callbacks**: The payment provider retries the webhook due to a slow or failed HTTP response from the application's webhook handler. Each webhook invocation triggers a new confirmation email. The application lacks idempotency checks on the webhook payload.
3. **Frontend double-submit**: The user double-clicks the payment button, creating two payment requests that both succeed (no idempotency key). Each successful payment triggers its own confirmation email. This would correlate with users on slower connections or without JavaScript-based button disabling.

### How I Would Verify Before Reporting

- Pull the email service send log for 5-10 affected users. If two distinct API calls exist per registration (different request IDs, seconds apart), the bug is in the application, not the email provider.
- Check the message queue's delivery count for the affected messages. A delivery count > 1 confirms hypothesis #1.
- Check the payment provider's webhook delivery log. If duplicated webhooks appear with the same event ID but different delivery attempt IDs, it confirms hypothesis #2.
- Check application server access logs for duplicate `POST /api/payment` requests from the same user within a short window (< 5 seconds). If found, it confirms hypothesis #3.
- Regardless of root cause, the fix recommendation is an **idempotency guard**: before sending a confirmation email, check a `confirmation_sent` flag on the registration record. Only send if the flag is false, then set it to true atomically.

---

## Scenario 3: App becomes noticeably slower after browsing events for several minutes.

### How I Would Investigate

Progressive slowdown during a single session points to a resource leak or accumulation problem. The key question is: **where is the resource accumulating?** I'd investigate five distinct angles in parallel.

---

#### Frontend

**What to inspect:**
- Browser DevTools Performance tab: record a 2-minute session of browsing events. Look for increasing JS heap size, growing DOM node count, or lengthening task durations.
- DevTools Memory tab: take heap snapshots at 1 minute, 3 minutes, and 5 minutes. Compare retained object counts. Look for detached DOM nodes or growing arrays.
- React/framework DevTools (if applicable): check for components that mount on each event page visit but never unmount (e.g., event detail modals that accumulate in the background).

**Possible root causes:**
- **Memory leak from event listeners**: Each time the user navigates to an event detail page and back, new event listeners (scroll, resize, WebSocket) are attached but never removed. After dozens of navigations, hundreds of orphaned listeners accumulate, slowing garbage collection and increasing memory pressure.
- **Unbounded DOM growth**: A single-page app that appends event cards to the DOM on each "load more" or page transition without virtualizing the list. After several minutes, the DOM has thousands of nodes, and layout/paint operations become expensive.

---

#### Backend

**What to inspect:**
- Application server metrics (CPU, memory, thread pool utilization) over the session duration. Is the server slowing down for all users or just this user's session?
- Response times for `GET /api/events` over the session. If response times increase for this specific user's token but not others, the issue is session-scoped.
- Application logs for increasing query complexity or N+1 query patterns triggered by accumulated session state.

**Possible root causes:**
- **Server-side session state accumulation**: The server stores per-user browsing history or recently viewed events in memory (session store). As the user browses more events, the session object grows, and serialization/deserialization of the session on every request becomes slower.
- **Unoptimized event filtering**: If the frontend sends increasingly complex filter queries (e.g., "exclude previously viewed events"), each subsequent request involves a larger exclusion list, slowing query construction and execution.

---

#### Database

**What to inspect:**
- Slow query logs during the affected time window. Are specific queries taking longer as the session progresses?
- Database connection pool metrics: is the pool being exhausted? Are connections being held open and not returned?
- Query execution plans for the events listing query. Is a full table scan occurring?

**Possible root causes:**
- **Connection pool exhaustion**: If database connections are leaking (opened but not properly closed/returned after each API call), the pool gradually fills up. Subsequent requests wait for a free connection, adding latency proportional to the number of leaked connections.
- **Lock contention**: Concurrent reads on the events table competing with write operations (e.g., `registered` count updates from other users registering) could cause increasing wait times as write frequency rises.

---

#### Browser

**What to inspect:**
- Browser task manager (Chrome's `Shift+Esc`): monitor the tab's memory and CPU usage over time. A steadily climbing memory footprint confirms a client-side leak.
- Service Worker / Cache Storage: check if the browser is caching every events API response without eviction, filling up Cache Storage.
- IndexedDB / localStorage: check if the app writes browsing state to client-side storage on every navigation, growing the storage size and slowing read/write operations.

**Possible root causes:**
- **Service Worker cache bloat**: A service worker with a cache-first strategy caches every unique event detail request. After browsing 50+ events, the cache contains hundreds of entries, and cache-matching operations slow down as the cache grows linearly.
- **Browser extension interference**: A browser extension (ad blocker, analytics tracker) intercepts every network request. Processing overhead grows proportionally with the number of requests made during the session.

---

#### Network

**What to inspect:**
- Browser DevTools Network tab: check if the number of concurrent pending requests increases over time (e.g., long-polling connections that are opened but never closed).
- Check for WebSocket connections that are opened for real-time event updates but never properly closed when navigating away.
- DNS resolution times and TCP connection reuse patterns.

**Possible root causes:**
- **WebSocket connection leak**: Each event detail page opens a WebSocket for live attendance updates. Navigating away doesn't close the socket. After several minutes, dozens of open WebSocket connections consume file descriptors and bandwidth, causing the browser to throttle new connections.
- **Excessive polling**: An `setInterval`-based polling mechanism fetches updated event data every few seconds. If the interval is never cleared on component unmount, multiple overlapping intervals accumulate, each firing network requests. After 5 minutes of browsing, dozens of intervals are firing simultaneously.

### How I Would Verify Before Reporting

- **Frontend leak**: Take heap snapshots at T=0, T=3min, T=6min. If retained memory grows linearly with no plateau, it's a frontend memory leak. Identify the retaining object via the snapshot comparison.
- **Backend**: Compare `GET /api/events` response times at T=0 vs T=5min for the same user and for a fresh user. If the fresh user's response is fast, the issue is session-scoped, not server-wide.
- **Database**: Run the slow query log analysis. If no slow queries appear, rule out DB as the bottleneck.
- **Browser**: Test in an incognito window with all extensions disabled. If the slowdown disappears, it's extension-related. If it persists, compare memory usage in Chrome vs Firefox to isolate browser-specific behavior.
- **Network**: In DevTools Network tab, sort by "Connection ID" and count unique connections. If the count grows over time without connections closing, it's a connection leak.

