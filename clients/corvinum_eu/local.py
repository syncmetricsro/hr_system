"""Local CorvinumEU demo settings for ``http://localhost:8001``.

Keep production behavior as the base, then make the one deliberate development
exception: password-only login for fictional-data client testing. Staging and
production never import this module and continue to require TOTP for managers.
"""

from clients.corvinum_eu.production import *  # noqa: F403

TWO_FACTOR_AUTH_ENABLED = False
