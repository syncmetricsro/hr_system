# Help visual aids

`screens/` holds screenshots captured from the seeded demo stacks by
`scripts/capture_help_screens.sh`. They are committed deliberately: a
screenshot that lies is worse than none, so regeneration is one command rather
than a manual ritual, and the command should be re-run whenever the shell or a
captured page changes.

`illustrations/` holds generated diagrams for concepts with no screen to
photograph. **Every illustration must be textless** — labels are HTML with
`{% trans %}` overlaid on the asset, because a label baked into a raster can
never be translated and this Help area ships in EN/SK/HU/UK.

Screenshots carry the app's own chrome in one language; capture is in Slovak,
the default and the language most users see, and the numbered callouts carry
the explanation in the reader's language.

Fictional seed data only — never a real-data environment.
