# Goma web GUI (preview console)

A single self-contained page (`index.html`, no build step, no dependencies) that
gives Goma a graphical front end: slider controls plus an animated, orbitable
3D SVG of a free-surface film flow — the kind of moving-boundary problem Goma
is built to solve.

Open it directly in a browser:

```bash
open web-gui/index.html      # macOS
xdg-open web-gui/index.html  # Linux
```

No server, no `pnpm`/`npm`, no compilation.

## What it is (and isn't)

- **Is:** a real, working GUI — process-parameter sliders (flow rate,
  viscosity, surface tension, contact angle), a live 3D mesh you can drag to
  orbit and scroll to zoom, a readout strip with derived Capillary/Reynolds
  numbers, and a "Save SVG frame" button that exports the current view as a
  standalone vector file.
- **Isn't:** wired to Goma's actual Newton solver. The surface you see is an
  illustrative traveling-wave heightfield shaped by the sliders, not a real
  finite-element solve, and it doesn't read Goma's `.exoII`/ASCII output.

## Why it's built this way

Goma itself is a command-line finite-element solver with a heavy native
dependency stack (Trilinos, PETSc, SEACAS, MUMPS, ...) — see
[`../BUILD.md`](../BUILD.md). That's the right shape for a solver; it is not
a GUI, and bolting a real-time visual front end onto the solver binary itself
would be a large, separate undertaking. This page is a companion piece: it
demonstrates the "GUI + animated 3D" experience people want to see, using the
same physical vocabulary (film height, capillary number, meniscus curvature at
contact lines) that Goma's own free-surface problems use.

## Turning this into something that reads real Goma output

The natural next step, if useful, is a results viewer rather than a live
demo: parse Goma's Exodus/ASCII output for a solved problem and drive the
same mesh-rendering code in this file from real nodal displacement/height
data instead of the synthetic `heightAt()` function. The projection, camera,
depth-sorted rendering, and SVG export in `index.html` would carry over
unchanged; only the data source would need to change.
