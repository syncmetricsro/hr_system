# Client appearance themes

Jober and CorvinumEU support **Light**, **Dark**, and **System** appearance
modes on every page, including sign-in and two-factor setup. Jober starts in
Light and CorvinumEU starts in Dark until the browser user makes a choice.

The choice is presentation-only and stored in local browser storage under a
client-specific key (`jober-theme` or `corvinum-theme`). It is shared between
tabs for that client but is not synchronized to the user's account or another
device. Clearing site storage restores the client default. System mode follows
the operating system and responds when that preference changes.

The synchronous, self-hosted `static/src/js/theme.js` runs before CSS to avoid
showing the default palette before a stored preference is applied. If browser
storage is blocked or contains an unknown value, the page remains usable and
falls back to the client default. No endpoint, cookie, dependency, or network
request is involved.

Corvinum's palettes follow its supplied PeopleOps prototype and keep the
sidebar dark in both modes. Jober uses its supplied SVG brand asset; its dark
palette is an “after-hours control room” treatment built from graphite,
aubergine, periwinkle, warm amber, and mint status colors. In Dark mode the
approved blue Jober SVG is transformed to a brighter periwinkle while its white
inset remains white; the source vector and Light-mode rendering stay unchanged. Functional QR
plates remain dark-on-white in every mode for scanning reliability.
