# No Django-admin registration on purpose: ledger entries follow no-hard-delete
# and reversal-only correction rules (C-Q5) that only the audited service layer
# enforces; an admin ModelAdmin would be an unaudited side door around both.
