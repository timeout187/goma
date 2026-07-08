# Goma web GUI (preview console)

Two companion front ends for Goma, both driven by the same illustrative
free-surface film-flow model:

- **`index.html`** — a single self-contained page (no build step, no
  dependencies): slider controls plus a hand-built, orbitable 3D SVG of a
  free-surface film flow — the kind of moving-boundary problem Goma is built
  to solve.
- **`app.py`** — the same idea as a Streamlit app, using an interactive
  Plotly 3D surface with its own Play/Pause/scrub controls.

## `index.html` — zero install

Open it directly in a browser:

```bash
open web-gui/index.html      # macOS
xdg-open web-gui/index.html  # Linux
```

No server, no `pnpm`/`npm`, no compilation.

## `app.py` — Streamlit version

```bash
pip install -r web-gui/requirements.txt
streamlit run web-gui/app.py
```

To host it live on Streamlit Community Cloud: sign in at
[share.streamlit.io](https://share.streamlit.io), "New app", point it at
this repo/branch with main file path `web-gui/app.py`. (This is a one-time
manual step tied to a Streamlit account — not something that can be done
from the repo itself.)

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
