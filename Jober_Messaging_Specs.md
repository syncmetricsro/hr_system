# Messaging Specification — Twilio SMS + Telegram

**Status:** Spec addendum to `jober_coding_agent_product_design_plan_v3_jober_only.md` (slots into the `messaging/` app; expands and supersedes open input #17 "SMS provider…").
**Scope:** Jober only. Outbound notifications to workers + limited inbound (opt-in / feedback). **Not** a worker portal or worker login.

> ⚠️ **Updated by Jober's round-4 answers — see `jober_answers_round4.md`, which is authoritative where it conflicts below.** Key changes: **no Telegram bot** — Jober already runs a manual Telegram broadcast channel, so drop the bot, per-worker opt-in, and chat-ID linking (§2 inbound and §3 Telegram adapter are superseded). **SMS is the system channel** (provider/sender chosen by SyncMetric; volume ≥ ~400/mo). **Arbitrary per-recipient selection is required** (not just all/none). **Coordinators may send to their own project.** Worker messages are **manually composed** (pay/advance reminders); the automatic expiry alerts are **internal staff notifications**, not auto-sent to workers.

---

## 1. Why two channels

- **SMS (Twilio)** stays the **primary** channel. Many workers have no email and not all have a smartphone; SMS is the lowest common denominator and the manager confirmed it as the main worker channel.
- **Telegram** is added as a **richer, cheaper secondary channel.** It has very high adoption among Ukrainian and CIS/Central-Asian populations — i.e. exactly Jober's workforce — supports longer multilingual messages, delivery feedback, and costs nothing per message. It is **opt-in** and never required.

Channel choice per worker: SMS by default; Telegram used when the worker has opted in and has a stored chat ID; otherwise fall back to SMS.

---

## 2. What it must do (MVP)

- **Outbound, one-to-many:** bulk notifications to a selected audience (all active workers, a project, an accommodation, a coordinator's workers) — pay dates, schedule/bus changes, general notices.
- **Outbound, transactional:** the entry-medical / compliance expiry reminders already in the plan, and operational alerts.
- **Multilingual templates:** every message is a template with HU/SK/UA variants; the worker's language picks the variant.
- **Audience selection + preview + confirm:** the sender sees the resolved recipient count and a rendered preview before sending; sending is an explicit confirm.
- **Delivery status:** record per-recipient queued / sent / delivered / failed (Twilio status callback; Telegram send result).
- **Full audit:** who sent what, to which audience, when, in which language, with what delivery outcome.

### Inbound (limited, on purpose)

- **Telegram opt-in / linking:** a worker starts the Jober bot (via a link or QR — can reuse the feedback QR on the payslip). The bot captures their `chat_id` and links it to the person record after a lightweight verification (e.g. a short code). Telegram does **not** let you message a user who hasn't started the bot, so this opt-in step is mandatory, not optional polish.
- **Feedback intake** (the QR feedback form already specified) may also arrive via the Telegram bot, routed to Manager-only, anonymous-or-identified — same rules as the web form.
- **No free-form worker support chat, no worker login, no self-service.** Inbound is limited to opt-in and feedback. This keeps the "no worker portal" boundary intact.

---

## 3. Architecture

A single `messaging/` app with a **channel abstraction** so the rest of the system never calls a provider directly:

- `Message` (template key, language, rendered body, audience descriptor, created_by, created_at, status).
- `MessageRecipient` (message, person, channel used, provider message id, status, error, timestamps).
- `WorkerChannel` (person, channel = sms|telegram, address = phone|chat_id, opt_in_state, consent_at, opt_out_at).
- `MessageTemplate` (key, HU/SK/UA bodies, variables, category).
- Provider **adapters** behind one interface: `SmsTwilioAdapter`, `TelegramBotAdapter`. Swapping or adding a provider touches only an adapter.
- **Sending runs as a background management command / queued job** (bulk fan-out, retries, rate-limit pacing), never inline in a request. Redis/worker is added only if volume requires it; until then a management command + DB queue is enough at this scale.

### Provider integration (supply-chain stance — see AGENTS.md §3.5)

- **Telegram:** call the Bot HTTP API directly via the project's **one pinned HTTP client** (e.g. `httpx`). The Bot API is small; a dedicated Telegram SDK is **not** justified.
- **Twilio:** default to calling the REST API via the same HTTP client. The official `twilio` PyPI SDK **may** be used if the team prefers, but only through the standard approval + hash-pin + cooldown gate (AGENTS.md §3.1) — it is not a free addition.
- Net new third-party dependency target: **one HTTP client**, hash-pinned, rather than two vendor SDKs and their trees.

---

## 4. Security, consent & privacy

- **Credentials** (Twilio Account SID/Auth Token or API key, Telegram bot token) via env / secret manager; never committed. Separate test vs production credentials.
- **Webhook verification is mandatory:** validate Twilio's `X-Twilio-Signature` on status callbacks; set and verify a Telegram secret webhook token. Reject anything unverified. Never act on an unverified callback.
- **Consent & opt-out:** store consent state per channel; honor STOP/opt-out for SMS and a /stop or block for Telegram; suppress messaging to opted-out workers. Record consent/opt-out timestamps (GDPR).
- **Retention:** message bodies and delivery logs have a retention rule (confirm with Jober); phone numbers and Telegram chat IDs are personal data under the same DPA/retention regime as the rest of the system.
- **Abuse / rate controls:** pace bulk sends to provider limits; cap who can trigger bulk (role-gated — see below); the public Telegram opt-in path needs basic abuse protection (rate limit, verification code) like the feedback form.
- **Test-recipient override:** like the spike's SMTP pattern, a configured test recipient can capture all sends in non-production so a misconfiguration can't message real workers.

---

## 5. Permissions

- **Bulk send / campaigns:** Manager (and Admin). Possibly Coordinator for their own project audience — **confirm with Jober**.
- **Transactional/system messages** (expiry reminders): system-triggered, not a user action.
- **Feedback inbound:** Manager-only visibility, as already specified.
- All sends/audience selections are audited (AGENTS.md §5).

---

## 6. Testing (folds into the plan's test plan)

- Audience resolution (project / accommodation / coordinator / all-active) yields the expected recipient set.
- Language selection picks the correct HU/SK/UA template variant.
- Channel selection prefers Telegram when opted-in, falls back to SMS otherwise.
- Webhook signature/token verification rejects forged callbacks.
- Opt-out suppresses future sends.
- Delivery-status updates map to the right `MessageRecipient`.
- Bulk send is idempotent (a retried batch does not double-send).
- Test-recipient override reroutes everything in non-production.
- Playwright: audience select → preview → confirm → mocked delivery; anonymous Telegram/web feedback reaches Manager but not Coordinator.

---

## 7. Open questions for Jober

1. **Twilio account & sender identity:** existing Twilio account? Sender = a Slovak long number, short code, or alphanumeric sender ID? (Alphanumeric senders can't receive SMS replies — affects opt-out handling.)
2. **Expected SMS volume / month** (drives cost and rate-limit pacing).
3. **Who may send bulk** — Manager only, or also Coordinators for their own project?
4. **Is Telegram actually wanted**, and will Jober run/own a bot? (Recommended for this workforce, but it's their call.)
5. **Which events auto-trigger messages** vs manual-only (e.g. expiry reminders auto; schedule changes manual).
6. **Message/log retention period** and consent-record retention.
7. **Languages per worker** — is each worker's preferred language already known, or set at intake?
8. **Inbound replies:** does Jober want to read SMS replies at all, or is SMS strictly outbound (Telegram carrying any two-way via feedback only)?