# Jober Telegram channel broadcast

Status: **Product-owner direction approved 2026-07-31; client access, privacy
review, and the open confirmations below still block implementation and real
use**

Owner: **Jober**. CorvinumEU keeps automated worker messaging disabled.

## Decision

Jober may publish Ukrainian-language, low-sensitivity operational announcements
to its existing Ukrainian-worker Telegram channel through a client-owned bot.
This is a **one-to-channel broadcast adapter** inside the existing
`features/messaging` feature. It is not a separate Telegram module, a worker
portal, a per-worker Telegram channel, or a substitute for recipient-addressed
SMS.

The first version has one configured private channel and outbound text posts
only. Manager/Admin previews and confirms a post. The application records the
actor, exact body, configured channel, provider result, and audit event. It does
not accept Telegram updates or expose a Telegram webhook.

## SMS and Telegram are different products

| Property | Twilio SMS | Telegram channel |
|---|---|---|
| Addressing | One known phone/person | One configured channel |
| Current role scope | Recruiter/Coordinator/Manager, with person/project rules | Manager/Admin only |
| Outcome claim | Per-message provider result | Channel post result only |
| Person delivery claim | May be associated with one person | Never |
| Audience segmentation | Individual selection | None in v1 |
| Content | Approved person-addressed operational text | General, low-sensitivity Ukrainian announcements |

Without a separate, deliberately approved membership-linking system, Jober
cannot map Telegram subscribers or views to `Person` records. The UI and audit
must say “posted to the Ukrainian-worker channel,” never “delivered to these
workers.” A channel post is not evidence that a particular worker received or
read a notice.

## Permissions

Add a distinct `telegram.broadcast` action granted only to Manager/Admin in the
Jober policy. Observer, Recruiter, and Coordinator cannot post.

This is intentionally narrower than `sms.send`. A shared channel may contain
workers from multiple projects or offices, so a project-scoped Coordinator
could otherwise reach people outside their authorization boundary. Coordinator
posting may be reconsidered only if Jober later creates separately administered
channels with an approved, server-enforced office/project mapping.

## Content boundary

The channel should be private and membership administered by Jober. Telegram
channels are cloud communications, not end-to-end-encrypted Secret Chats, so a
private channel does not make sensitive HR content appropriate.

Allowed in v1:

- general Ukrainian-language operational announcements;
- office-wide closures, holidays, or meeting information;
- non-personal schedule or transport changes;
- general reminders that identify no worker;
- links to authenticated Jober pages without secrets in the URL.

Prohibited:

- worker names, identifiers, phone numbers, or person-specific links;
- wages, payslips, advances, debts, deductions, or bank information;
- health, medical, certificate, blacklist, complaint, or disciplinary details;
- personal assignments, accommodation details, or individual schedules;
- uploaded documents, photos, or other attachments;
- access tokens, one-time codes, or sensitive query-string values.

Telegram must not become a route around the platform document-storage boundary.
Legally important or person-specific notices continue through an approved
recipient-addressed process; a channel broadcast alone is not proof of notice.

## Authoring workflow

1. Manager/Admin opens the Telegram broadcast page.
2. They choose a human-approved Ukrainian template or enter Ukrainian text.
3. The server validates the text-only content and displays the exact channel,
   language, and rendered message in a preview.
4. The user explicitly confirms. A unique operation key prevents a repeated
   form submission from creating a second send attempt.
5. The server creates the audit/broadcast record, calls Telegram once, and
   stores the provider result.
6. The result page links the internal audit record; it does not expose the bot
   token or claim person-level delivery.

There is no automatic translation. Templates and manually entered text need a
human who can approve the Ukrainian wording. Automatic expiry, medical,
certificate, finance, or person-specific events do not trigger Telegram posts.

## Delivery states and retry safety

The broadcast record uses these states:

- `draft` — not submitted to Telegram;
- `posted` — Telegram returned success and a message ID;
- `failed` — the request is known not to have produced a post;
- `unknown` — the connection failed after sending may have occurred.

Telegram `sendMessage` has no application idempotency key. If the app times out
after Telegram accepted the request, an automatic retry could publish a
duplicate. Therefore:

- a confirmed operation is submitted at most once automatically;
- `posted` is never retried;
- `unknown` is never retried automatically;
- a Manager must inspect the actual channel and resolve an `unknown` result
  with a reason before creating any replacement broadcast;
- resolution and replacement are audited.

## Data model and audit sketch

Use a separate `TelegramBroadcast` model rather than pretending the existing
person-addressed `OutboundMessage.to_number` row represents a channel post.
Minimum fields:

- exact rendered body and language;
- non-secret channel ID/reference and display label;
- status and sanitized error category;
- Telegram message ID when returned;
- unique operation key;
- created/confirmed/resolved timestamps and actors;
- optional resolution reason for `unknown`.

The bot token is never stored in the database or audit. The audit records
create/confirm/result/manual-resolution events and old/new status values. It
must not record the full Telegram API URL because that URL contains the bot
token.

Retention for broadcast bodies and provider/audit records remains a client and
privacy decision. Deleting a Telegram post outside Jober does not silently
rewrite the application audit, and deleting an application record must not be
treated as deleting the Telegram copy.

## Provider integration and secrets

Call Telegram's HTTPS Bot API directly through Python's standard library,
following the existing Twilio dependency discipline. Do not add a Telegram SDK
or a new HTTP dependency.

Runtime configuration, supplied through Doppler or the approved production
secret manager:

- `TELEGRAM_BOT_TOKEN` — secret, never printed or committed;
- `TELEGRAM_CHANNEL_ID` — the single approved production channel;
- `TELEGRAM_CHANNEL_LABEL` — safe display name for preview/audit;
- `TELEGRAM_ALLOWED_CHANNEL_IDS` — non-production allowlist that fails closed.

Use separate client-owned test and production bots and channels. The production
bot receives only the minimum channel permission needed to post. Jober must
document the owning organizational account, at least two accountable
administrators/recovery contacts, token rotation, and emergency removal of the
bot from the channel.

Errors shown to users and written to logs must be sanitized so the token-bearing
request URL and provider response internals cannot leak. Timeouts are bounded.
No build step receives the token.

## No inbound Telegram surface in v1

The first version does not configure `setWebhook`, poll `getUpdates`, accept bot
commands, read replies/comments, collect feedback, or start private chats. It
therefore needs no public Telegram callback route or webhook secret.

Any later inbound feature is a new security and product decision. It must define
the actual workflow, verify Telegram's webhook secret token, restrict accepted
update types, rate-limit public traffic, and add retention/abuse controls. It
must not be slipped into the outbound adapter as incidental plumbing.

## Verification

Required automated coverage:

- Jober Manager/Admin allowed; every other role denied server-side;
- feature absent for CorvinumEU;
- exact configured channel and text sent through a mocked HTTPS call;
- missing token/channel and a non-production channel mismatch fail closed;
- token never appears in audit, error text, or captured logs;
- double submit produces one provider attempt;
- success, known failure, and uncertain timeout produce the correct states;
- `unknown` cannot auto-retry and manual resolution requires a reason;
- no Telegram webhook route exists;
- Playwright preview/confirm/result flow with no real provider call.

Provider-backed testing uses only the dedicated test bot/channel and runs
through Doppler. It verifies one harmless fictional post, records no token or
private channel identifier in the repository, and is never part of the ordinary
secret-free suite.

## Client confirmations and gates

Implementation remains blocked until Jober confirms or supplies:

1. the existing channel is private and intended for this operational use;
2. one common Ukrainian-worker channel is sufficient for v1;
3. Manager/Admin-only posting is accepted;
4. allowed content and retention are accepted through the privacy/DPA review;
5. who writes or approves Ukrainian templates and manual messages;
6. client-owned test and production bot/channel access;
7. organizational bot ownership, recovery administrators, and token-rotation
   procedure;
8. whether channel comments/discussion are disabled or explicitly outside the
   Jober support workflow.

Real-worker messaging remains behind the repository real-data gate. Until that
gate and the items above pass, development and demonstrations use fictional
content in the dedicated test channel only.

## Deliberate non-goals

- per-worker Telegram chat IDs, consent rows, or SMS fallback selection;
- subscriber import or matching against `Person`;
- per-person read/delivery receipts;
- Coordinator/project/office targeting;
- inbound commands, feedback, support chat, or a worker portal;
- attachments, media, documents, or automatic event-triggered broadcasts;
- a Telegram SDK, queue service, Redis, or background worker for v1.

Official technical references:

- [Telegram Bot API: `sendMessage`](https://core.telegram.org/bots/api#sendmessage)
- [Telegram Bot API: administrator rights](https://core.telegram.org/bots/api#chatadministratorrights)
- [Telegram bot tokens and ownership](https://core.telegram.org/bots#how-do-i-create-a-bot)
- [Telegram Cloud Chats and Secret Chats](https://www.telegram.org/faq#q-how-secure-is-telegram)
- [Telegram Bot API: `setWebhook`](https://core.telegram.org/bots/api#setwebhook)
