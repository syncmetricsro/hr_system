# Jober messaging specification — Twilio SMS and Telegram channel broadcast

Status: **Reconciled 2026-07-31. Twilio SMS is implemented; Telegram channel
broadcast is specified but not implemented and remains blocked by client-owned
access and privacy decisions.**

Scope: Jober only. CorvinumEU keeps automated worker messaging disabled. This
is not a worker portal or worker login.

The second Jober demo interview superseded the round-4 “manual Telegram channel,
no bot” answer. It also rejected this file's earlier per-worker Telegram bot,
chat-ID linking, opt-in, SMS fallback, and feedback-bot proposal. The canonical
Telegram design is now
[`docs/product/jober-telegram-channel-design.md`](docs/product/jober-telegram-channel-design.md).

## 1. Two deliberately different channels

### Twilio SMS

SMS is recipient-addressed operational messaging. The current implementation:

- sends through Twilio's REST API using Python's standard library;
- associates an outbound row with a phone number and optionally a `Person`;
- permits Recruiter, Coordinator, and Manager through `sms.send`;
- restricts Coordinators to people on their responsible projects;
- verifies inbound Twilio signatures and fails closed;
- records the provider result and audit event;
- can restrict non-production sends to an approved test-recipient allowlist.

The current UI sends one manually composed or selected-template message from a
person card. The broader campaign/audience-preview system described in early
discovery was not implemented and is not silently promised by this document.

### Telegram

Telegram is one outbound post to Jober's configured Ukrainian-worker channel.
It is not addressed to individual workers and must not claim subscriber,
person-level delivery, read, project, or opt-in evidence.

The approved direction is:

- one client-owned private channel in v1;
- one client-owned bot with minimum posting rights;
- Manager/Admin-only text broadcasts;
- human-approved Ukrainian templates or manually written Ukrainian text;
- exact preview and explicit confirmation;
- general, low-sensitivity content only;
- no inbound webhook, commands, replies, feedback, chat-ID linking, attachments,
  or automatic event triggers;
- application audit of the post attempt and Telegram message ID, not individual
  delivery.

The full content policy, states, retry safety, secret handling, data sketch,
tests, and client gates live in the canonical Telegram design linked above.

## 2. Shared safety rules

- Provider credentials come from Doppler or the approved runtime secret manager
  and never from Git, the database, audit, logs, or a build stage.
- Separate test and production provider identities are mandatory.
- Ordinary tests are secret-free and mock provider calls. Provider-backed tests
  use `doppler run -- ...` and only approved test recipients/channels.
- Every send/post is role-gated server-side, explicitly confirmed where the UI
  offers it, and audited.
- Message bodies and provider records need an approved retention period before
  real-worker use.
- The DPA/privacy review must cover the provider, message content, identifiers,
  retention, deletion, and incident handling.
- Sensitive HR, health, certificate, blacklist, document, payslip, debt, and
  bank data never goes to the shared Telegram channel.

## 3. Implementation boundary

Keep both transports in the existing `features/messaging` feature. Provider
services may share safe infrastructure helpers, but they do not share false
domain semantics:

- `OutboundMessage` remains a person/phone-shaped SMS record;
- Telegram uses a separate channel-broadcast record;
- Jober policy enables the transports and grants their separate actions;
- CorvinumEU has neither route nor permission;
- no `features/telegram` package and no client conditional in `core/`.

Both provider integrations use the standard library unless a separately
approved dependency ADR changes that rule. Telegram's token-bearing API URL
must never appear in logs or audit.

## 4. Current open items

### SMS

- approved message/log retention;
- native review of templates and a decision on multilingual variants;
- whether a future campaign/audience workflow is needed;
- production sender/account and inbound-reply operating policy.

### Telegram

- private-channel confirmation and one-channel acceptance;
- Manager/Admin-only posting confirmation;
- client-owned test and production bot/channel access;
- bot ownership, recovery administrators, and token rotation;
- Ukrainian author/approver;
- content and retention approval through the DPA/privacy review;
- channel comments/discussion policy.

Real-worker messaging remains behind the repository real-data gate. Telegram's
target state is ON/PENDING for Jober and OFF for CorvinumEU; “pending” is not
evidence of an implemented module.
