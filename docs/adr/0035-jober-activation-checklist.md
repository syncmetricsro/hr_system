# ADR 0035: Jober gets the activation checklist

Status: **Accepted — 2026-08-05.**
Date drafted: 2026-08-05

## Context

The activation checklist was built for CorvinumEU in Stage C, and ADR 0022's
feature table lists it under that client. Jober has had the flag off ever since,
with the comment *"not in the Jober product"*.

That comment was wrong. `docs/product/jober-requirements-supplement.md` §11
lists **"Trial day, checklist, and activation gate"** under *Confirmed Jober
requirements retained*. Jober asked for a checklist; it was built for the client
who asked second, and Jober was never switched on.

Everything needed was already in place and unused: `features.checklists` is in
the base `INSTALLED_APPS` for every client, `clients/jober/policies.py` already
grants `CHECKLIST_TICK` to coordinators and managers, and `config/urls.py`
mounts the toggle route behind the flag. This is the Stage B/C extraction
working in the direction it was designed for — a feature built for one client
turned on for another without a fork.

## Decision

### 1 · The flag goes on, with the same nine items

Jober seeds its own copy of the nine: personal data, identity document,
work/residence permit, medical certificate, safety training, contract, duplicate
check, blacklist check, welcome call. Eight are critical; the welcome call is
not.

**Its own copy, not a shared list.** Neither office's wording should be hostage
to the other's — a checklist item means whatever that office says it means
(C-Q22 asks CorvinumEU to confirm theirs).

### 2 · The strings are byte-identical to CorvinumEU's, on purpose

`db_trans` is a verbatim `gettext` lookup, so identical English text shares one
catalog entry and one translation per language. Keeping the wording identical
today meant this slice needed **no new translation work at all** — eighteen
strings across three languages already existed.

The consequence is written into `clients/jober/catalog_i18n.py` and guarded by a
test: **the moment either list changes by one character, those strings become
new msgids and need sk, hu and uk before they ship.** The test that compares the
two lists is a tripwire, not a rule — divergence is allowed and expected, it
just has a translation bill attached.

### 3 · Critical items block activation — a third gate

Jober already gates activation twice: four-pillar readiness, then a manager
decision (ADR 0018, ADR 0031). The checklist is a third, and it blocks, exactly
as it does on CorvinumEU.

A checklist that cannot stop anything is a to-do list. The requirement names
"checklist and activation gate" in one breath, and the pillars answer a
different question — readiness is about logistics (medical, gear, a bed, a
ride), the checklist is about paperwork and identity having been verified by a
person who says so with their name against it.

### 4 · The demo seed does the office's work before it activates

`seed_people` calls `activate_on_project` for every seeded working person, and
that runs every registered activation check. Once a template with critical items
exists, **the seed would refuse its own activation** — a failure with no partial
form: seeding stops and the demo database is empty.

CorvinumEU never met this because its seed activates nobody.

So the seed ticks each critical item, through `set_item_state` with the seed
coordinator as actor, before activating. Not a workaround: it is what the office
would have done, and it makes the demo read correctly — working people with a
completed checklist carrying a name and a time, trial-day candidates with theirs
open so the block can be shown deliberately.

The template is created by `ensure_checklist_template()` in
`clients/jober/demo/checklist.py`, called from both `seed_people` and
`seed_demo_scenario`, because the two run in that order and whichever is first
must be the one that creates it.

## Consequences

**ADR 0022's table entry for checklists is superseded** — the feature is
CorvinumEU-*originated*, not CorvinumEU-only.

**Jober activation can now be blocked by a third thing**, and demo scripts that
assumed two gates need to know it. The runbook says so.

**Existing Jober databases get the checklist on next seed.** Nothing
retroactively blocks an already-working person: the gate runs at activation, not
continuously.

**No new dependency, no migration, no core change.** One flag, one seed list,
one registry file.

## Open

- Jober has not been asked to confirm its nine items the way CorvinumEU has
  (C-Q22). Same question, different client; ask at the next demo.
