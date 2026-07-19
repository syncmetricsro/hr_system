# No Django-admin registration on purpose: wage records and recovery
# assignments are create-only money data whose every mutation must flow
# through the audited service layer. An admin ModelAdmin would be an
# unaudited edit/delete side door.
