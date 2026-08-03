# Processor agreements — what each one must cover

> **DRAFT checklist for the client and their adviser. Not legal advice, and not
> a DPA.** A DPA is the provider's paper; this is what to check it against, so
> the review is a comparison rather than a reading.
>
> Prepared 2026-08-03. Fictional data only — no processor currently handles real
> worker data through this system.

`Jober_Messaging_Specs` §2 already requires that "the DPA/privacy review must
cover the provider, message content, identifiers, retention, deletion, and
incident handling". That sentence is the seed; this document turns it into a
list, and names the actual processors.

## Who the processors are

Verified against the codebase and deployment plan on 2026-08-03. "In use" means
the system talks to it today with fictional data.

| Processor | Role | Personal data it would see | Status |
|---|---|---|---|
| **FORPSI** (VPS, syncmetric-prime) | Hosting — the application and its PostgreSQL database | **Everything.** Person records, certificates and uploaded scans, pay data, audit log, message bodies | In use (staging). **The most important agreement, and the one most easily overlooked** because it is infrastructure rather than a feature |
| **Twilio** | SMS delivery | Worker phone number, full message body | In use for Jober; live credentials on staging |
| **FORPSI** (SMTP, `noreply@corvinum.eu`) | Email delivery — CorvinumEU payslips | Worker email address, subject, body, encrypted PDF attachment | In use for CorvinumEU. Note: same vendor as hosting, but a distinct service — confirm the paper covers both |
| **Mail provider for Jober** | Email delivery — job offers | Worker email address, subject, full offer body | **Not selected.** Blocked on Jober supplying a `noreply@` address |
| **Doppler** | Secrets management | Credentials only — **no worker personal data** | In use. Probably not a processor of personal data; confirm rather than assume |
| **Off-site backup target** | Backup storage | Everything, as hosting | **Not selected.** Backups are deferred; scripts exist, the host does not. A backup destination is a processor and needs its own agreement |

**No CDN, analytics, error-tracking or font service.** Checked: no external
script or style hosts in the base template, no Sentry, no analytics. Uploaded
files are on local disk (`MEDIA_ROOT`), not object storage. So the sub-processor
surface is genuinely small — worth stating positively, because it is unusual and
it simplifies the review.

## What each agreement must contain

Art. 28(3) sets the mandatory content. This list restates it in the terms of
this system so a reviewer can tick items off.

**The mandatory Art. 28(3) terms**

1. **Subject-matter, duration, nature and purpose** of the processing, and the
   **types of personal data and categories of data subject**. Say plainly:
   workers and job candidates; identity and contact data; for hosting also
   health-adjacent (disability flag), occupational certificate scans, and pay
   data.
2. **Processes only on documented instructions** from the controller, including
   for transfers to a third country.
3. **Confidentiality commitments** from everyone the processor authorises.
4. **Art. 32 security measures** — see the specifics below.
5. **Sub-processors**: no new ones without authorisation, and the same
   obligations flowed down. *Ask for the current list by name.*
6. **Assistance with data-subject rights** — access, erasure, objection. Relevant
   here because there is currently no erasure path in the application either
   (see the retention proposal).
7. **Assistance with Art. 32–36 duties** — security, breach notification, DPIA.
8. **Deletion or return at the end of the contract**, and deletion of copies —
   *including backups*, which is where this is usually vague.
9. **Information and audit rights**, including inspections.

**Specifics worth naming for this system**

- **Breach-notification window** — a defined period ("without undue delay" alone
  is not workable). Ask for hours.
- **Location of processing and storage**, and the transfer mechanism if any data
  leaves the EEA. Twilio in particular routes internationally.
- **Message content and retention at the provider.** Twilio and most mail
  providers retain message bodies and delivery logs on their own schedule,
  independently of anything this application deletes. **Purging
  `OutboundMessage` locally does not purge Twilio.** Get the provider's own
  retention period and the means to shorten or disable body logging.
- **Backup retention and deletion latency** for the hosting provider — how long a
  deleted record survives in their backups.
- **Support access** — whether provider staff can read the database or mailbox
  contents, and under what controls.

## Points specific to each processor

**FORPSI (hosting)** — sees everything, including certificate scans and pay
data. This is the agreement that matters most and the one least likely to be
thought of as a "processor" question. Confirm: physical/EEA location, who at
FORPSI can access the VPS, backup retention and deletion, and sub-processors.

**Twilio** — the sharpest question is **how long Twilio itself keeps message
bodies**, since a local retention period is meaningless if the provider holds a
copy. Also confirm the separate test and production identities the messaging
spec already mandates, and the international routing position.

**FORPSI (SMTP)** — same vendor, different service. Confirm the paper covers
mail as well as hosting rather than assuming one agreement reaches both. Note
payslip attachments are AES-256 encrypted and the password is never emailed, so
the provider sees an encrypted PDF and a covering message — worth stating in the
agreement's data description because it materially limits exposure.

**Jober's mail provider** — undecided. When it is chosen, the same checks apply,
and this is a chance to ask about body retention *before* signing rather than
after.

**Off-site backup** — not selected. Whichever it is, it holds a complete copy of
everything and needs an agreement before the first real backup, not after.

## Status

| Agreement | Received? |
|---|---|
| FORPSI hosting | **Not received** |
| Twilio | **Not received** |
| FORPSI SMTP (CorvinumEU) | **Not received** |
| Jober mail provider | Provider not selected |
| Off-site backup | Destination not selected |

`docs/product/jober-requirements-supplement.md` already records the processor
agreement and the processors/retention list as *Not received*. Nothing has
changed since.

**No real worker data may pass through any of these until the corresponding
agreement is in place.** That is a condition of the real-data gate in
`AGENTS.md`, not an additional rule invented here.

## Sign-off

| | Name | Date |
|---|---|---|
| Prepared (engineering draft) | | 2026-08-03 |
| Reviewed | Data-protection adviser / DPO | |
| Confirmed complete | Client business owner | |

Related: `jober-data-retention-proposal.md`, `jober-offer-email-lia.md`,
`jober-blacklist-lia.md`, `docs/product/jober-client-ask-list.md`.
