# Contextual tooltips

Jober and CorvinumEU share a dependency-free tooltip controller for navigation,
icon-only controls, clickable operational cards, and actions whose consequences
benefit from explanation. Ordinary visibly labelled controls such as Save,
Back, and Submit do not repeat their label in a tooltip.

Templates opt in with a localized `data-tooltip="…"` attribute. Submit buttons
carrying `data-confirm`, or belonging to a form that carries it, automatically
reuse that existing localized explanation. The controller uses delegated events,
so content swapped by htmx behaves the same as the initial document.

Dashboard links may also provide `data-tooltip-heading="…"`. The controller
renders that heading separately from the descriptive `data-tooltip` text using
text-only DOM assignments. Report cards use short action headings and explain
the destination or filter instead of repeating the generic word “Details”.
Feature-provided linked report tiles must supply both `tooltip_heading` and
`tooltip_body`; non-clickable metrics do not receive tooltips.

Mouse users see a tooltip after a short delay. Keyboard focus shows it
immediately and temporarily associates it through `aria-describedby`; Escape
dismisses it. The tooltip remains available while hovered and is clamped to the
viewport. Touch input is never delayed or converted into a two-tap interaction.

Colors are semantic client tokens and follow Light, Dark, or System mode.
Tooltip content must never introduce hidden worker PII, audit metadata,
permission details, or other information not already authorized on the page.

Dashboard drill-downs must match their wording. Active-project links filter the
project list to active records, lifecycle links filter People by status, and
inactive-reason links include the selected reason (including the “No reason”
bucket). Invalid filter values are ignored safely.
