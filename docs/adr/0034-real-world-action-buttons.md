# ADR 0034: Buttons that reach outside the application look different

Status: **Accepted — 2026-08-05.**
Date drafted: 2026-08-05

## Context

Most controls in this product move numbers between screens. A handful do not.
*Mark cycle settled* asserts that payroll paid people. *Send encrypted PDF* puts
a document in a real inbox. *Issue equipment* is boots leaving a warehouse.
*Schedule trial* is a person getting on a bus.

Until now they all looked the same: a row of quiet grey `button-secondary`, with
the label text as the only thing separating "recalculate a total" from "money
changed hands". Tooltips and confirmation dialogs already carried good
explanations, but both require the user to already be hesitating. The signal
arrived after the decision to click.

The owner asked for these to be visibly, deliberately different — a unique
button, a unique tooltip, and very visible text — so that an office user can see
before clicking that they are committing to something the application cannot
take back.

## Decision

### 1 · A marker of three parts, always together

- **`.button-physical`** — warning-toned, with a **striped left edge drawn in
  CSS**.
- **`data-tooltip-heading="Real-world action"`** — the same phrase on every one
  of them, with the specific consequence in `data-tooltip`.
- **`.action-consequence`** — a visible caption beside the control, stating the
  physical fact in a handful of words: *Money is actually paid out. A real phone
  buzzes. Gear physically changes hands.*

One part alone degrades quietly. A class with no words is decoration; words next
to a button that looks like every other button are not read; a tooltip is only
seen by someone already unsure. `tests/test_physical_actions.py` holds the three
together and names the specific buttons, because the realistic failure is a
later edit demoting one of them back to grey.

### 2 · The stripe is a shape, not only a colour

Colour alone fails greyscale printing and colour-vision deficiency. This
stylesheet already reasons that way about its chart tokens, where `--success`
and `--danger` are noted as failing CVD checks and the dataviz palette is chosen
separately. A warning hue that reads as "just another button" to the people most
likely to miss a warning is not a warning. The repeating gradient survives both.

For the same reason it is drawn in CSS rather than set as an icon: the
CorvinumEU Material Symbols font is a fixed subset, so a new glyph would mean
re-subsetting the font, and a missing ligature renders as the literal word.

### 3 · Four families qualify

Confirmed with the owner on 2026-08-05:

- **Money and sending** — mark cycle settled, send/resend a payslip, send SMS,
  send an offer email, flag equipment unreturned, approve a deduction charge.
- **Physical handover** — issue equipment, record a return, assign or release a
  room, exit and reconcile.
- **A person has to be somewhere** — schedule a trial, skip the trial and start
  readiness.
- **Paper in hand** — record a medical date, save a certificate. This is the
  "the certificate was received, or is required" case: what is recorded here is
  a claim about a document someone physically holds.

The confirmation dialog gains a matching line whenever the pending action is one
of these, read by `app.js` from the submitter's class.

### 4 · The generic ledger *Record* button is deliberately not marked

It records something that already happened rather than causing it, and the same
button also records fuel additions and equipment charges. Marking it would put
the loudest styling in the product on its most routine control, which is how a
warning becomes wallpaper. Reversible if the office disagrees in use.

Blacklist decisions are also unmarked: serious, but not physical, and execution
is still gated on the LIA.

## Consequences

**The class name is an interface, not a style.** `app.js` reads
`.button-physical` to decide whether to show the dialog band. Renaming it
silently breaks the strongest sentence on the screen; a test asserts the pairing.

**Both clients get it from `core`.** The tokens used (`--warning`,
`--warning-soft`) exist in the shared stylesheet and in the CorvinumEU theme, in
light and dark. No client branching.

**Nothing about behaviour changed.** No service, no permission, no migration —
the same actions do the same things. What changed is how loudly the product
admits what they are.

**The set will grow.** Anything added later that pays, sends, hands over or
moves a person belongs here; the ADR is the list to check against.
