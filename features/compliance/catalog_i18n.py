"""Translatable msgids for canonical occupational-certificate names.

The database stores canonical English while badge tooltips translate at
render time. Operator-entered names are not listed here and therefore pass
through Django's gettext lookup unchanged.
"""

from django.utils.translation import gettext_noop as _

CANONICAL_CERTIFICATE_NAMES = [
    _("Forklift licence"),
    _("Crane licence"),
    _("Welding licence"),
]
