# Branches waiting on a decision

Since 2026-08-04 this project does not use pull requests (see `CLAUDE.md`
"Workflow"), so nothing deletes a branch automatically and nothing surfaces one
that was left behind. This file is that surface. Keep it short: a branch either
lands or it goes.

## Needs a decision

### `agent/corvinum-wage-ledger` — **5 commits not in `main`**

- Last activity **2026-07-20**, so it has been sitting for two weeks.
- Head commit: *"Allow agent-advised, human-executed OS/editor package installs"*
  — which sounds like it touches `AGENTS.md` supply-chain policy rather than the
  wage ledger the branch is named after, so read the diff before assuming either.
- `features/wage_ledger` **is** in `main` and working, so the branch is not
  blocking the feature; what is unclear is whether these five commits were
  superseded or simply never finished.

```bash
git log --oneline origin/main..origin/agent/corvinum-wage-ledger
git diff origin/main...origin/agent/corvinum-wage-ledger --stat
```

Outcome to record here once decided: merged, or deleted.

## Safe to delete whenever

Fully merged into `main` — `git rev-list --count origin/main..origin/<branch>`
returns **0** for each, so deleting removes only the branch pointer:

- `agent/fix-goods-receipt-period-tests` (2026-08-01)
- `agent/occupational-certificates-and-hr-design` (2026-07-31)
- `docs/deployment-1458ff7` (2026-08-01)
- `docs/deployment-631dd1c` (2026-07-29)

Three others from the pull-request era were deleted on 2026-08-04 after the same
check: `feat/activation-without-trial`, `feat/profitability-workbook`,
`fix/i18n-extraction-safety`.

## The rule that keeps this file short

Slice branches now stay **local** and are deleted by `git branch -d` right after
`git merge --no-ff`. A branch should only reach the remote if it is being handed
to someone else — and then it belongs in the list above until it is resolved.
