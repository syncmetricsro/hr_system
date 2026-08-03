# Secure Document Vault — proposal

For the client. Plain language; the engineering design is
[`secure-document-vault-design.md`](secure-document-vault-design.md).

Prepared 2026-08-03.

## In one paragraph

Your HR system deliberately does not store identity cards, passports, birth
certificates or medical papers. That is a design decision made to protect you,
not a missing feature. If you have a genuine legal need to keep those documents,
we can build a **Secure Document Vault** as a separate module, priced separately,
because it carries obligations and running costs the main system does not.

## What the system does today

It stores **the fact that a document was checked**, not the document:

- what was verified, by whom, and when;
- validity and expiry dates, so the system can warn you before a licence lapses;
- current status — verified, missing, expiring, expired.

Files are accepted for **three occupational licences only**: forklift, crane and
welding. That limit is enforced in the software, not merely written in a policy —
there is no setting or workaround that adds a fourth type.

Everything else is either metadata-only or refused outright: identity cards and
passports, birth and residence certificates, medical reports and examination
results, bank and tax documents, and general "other attachments".

## Why refusing them is a benefit

Three practical reasons, in order of how much they are likely to matter to you:

**If there is a breach, the damage is bounded.** Nobody can steal identity
documents from a system that never held any. This is the single largest
reduction in risk available, and it is already in place.

**Less to justify.** Every document class you keep needs its own lawful basis,
its own retention period, its own access rules, and a defensible answer to "why
do you have this?". Three occupational licences is a short list to defend. A
folder of passport scans is not.

**Lower cost.** Documents that do not exist need no encryption keys, no vault
hosting, no access reviews and no separate audits.

The trade is real: you cannot pull up a copy of someone's ID from the system.
Where the law genuinely requires you to hold one, that is what this proposal is
for.

## What the vault adds

Three things the main system does not do. These are specific, verified gaps —
not a general promise of "more security".

**1 · A record of who looked.** Today the system correctly *refuses* access to
people who should not see a file, but when an authorised person opens one,
nothing is written down. The vault records every view and download: who, what,
when. For identity documents this is usually the first thing an auditor or a
regulator asks for.

**2 · Files unreadable without a key the application does not hold.** Today
files sit on the server's disk, protected by the application. Anyone with
administrator access to that server can read them directly. We say so plainly in
our own documentation rather than describing it as encrypted. In the vault each
document is encrypted with its own key held by a separate key service, so
server access alone is not document access.

**3 · Proving it is you, again.** Today a logged-in session can open anything
that user is allowed to see. The vault asks the person to re-authenticate before
viewing or exporting a sensitive document — the control that limits the damage
from an unlocked laptop or a borrowed session.

It also brings automatic deletion: each document class gets a retention rule, and
documents are deleted, anonymised or sent for review when it expires — instead of
accumulating until someone remembers to look.

## What it does not do

Stated plainly so there is no misunderstanding later:

- **It does not read your documents.** No text extraction, no language
  detection, no automatic checking that a scan really is what it claims to be. A
  human classifies each one, exactly as today.
- **It does not make sharing lawful.** If a document should not go to your
  accountant, storing it in a vault does not change that. The separate rules on
  what payroll may receive still apply.
- **It does not remove your obligations.** You remain the data controller.

## What you would need to supply

The build cannot start without these, and they are genuinely yours to decide:

1. **Which documents, and why.** A written necessity assessment per class. The
   honest answer is often fewer than the initial list, which saves you money.
2. **A data protection impact assessment.** Required for this kind of material.
3. **Signed agreements with the providers involved** — see our checklist of what
   each must cover.
4. **Retention periods per document class**, which for payroll-related documents
   are set by law and your accountant will know.
5. **Budget for running it**, not only building it — key management, storage,
   scanning for malware, backups with tested restores, and periodic access
   reviews.

## Why it is priced separately

It carries its own threat model, its own encryption and key management, its own
impact assessment, its own hosting, and its own audit and review obligations.
None of that exists in the main system, because the main system deliberately
avoids the data that requires it. Clients who do not need the vault should not
pay for its running costs, and clients who do should see what they are paying
for.

We would quote it in stages rather than as a single figure. The first stage is
assessment and design — and it is worth doing on its own, because the outcome
may be that you need less than you expected, or nothing at all.

## Next step

This is already logged as an open question — **C-Q18** — asking you to confirm
the current boundary. Two possible answers:

- **Confirm the boundary as it stands.** Nothing changes; the system keeps
  metadata and the three licence types, and your exposure stays low.
- **Commission the assessment stage.** We establish which documents you are
  genuinely required to keep, and what a vault for those would involve.

Nothing needs deciding today, and no real worker documents can be stored in any
case until the outstanding data-protection items are closed.
