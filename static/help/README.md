# Help screenshot assets

`screens/` contains reviewable screenshots captured from the committed seeded
demo stacks by `scripts/capture_help_screens.sh`. The capture starts with a
1440×900 desktop viewport, crops to 16:9, writes a 1280×720 article WebP and a
matching 640×360 `-thumb.webp`, and strips metadata through the already-pinned
Pillow dependency.

- Jober screenshots are captured in Slovak under `screens/jober/`.
- Corvinum screenshots are captured in Hungarian under `screens/corvinum/`.
- Numbered callouts and explanations are translated HTML overlays in the Help
  article. They are never baked into the raster.
- Only the repository's fictional demo records may appear.

Never capture TOTP enrollment, one-time payslip passwords, provider
credentials, logs, production screens, or non-fictional records. The Audit
figure deliberately removes the event table before capture, and the Payslips
figure is captured before any send action so no password message can exist.

Run the capture only through the committed isolated workflow:

```bash
scripts/capture_help_screens.sh
```

Manually review every generated image before commit. A screenshot that exposes
restricted data or describes a screen that no longer exists must be rejected,
not patched with baked-in labels.
