"""
Goma Free-Surface Film Flow -- Streamlit companion console
------------------------------------------------------------
An animated, orbitable 3D preview of the kind of free/moving-boundary
problem Goma solves, driven by the same illustrative traveling-wave
heightfield as web-gui/index.html (the hand-built SVG version). Not
connected to Goma's actual Newton/FEM solver -- see web-gui/README.md.

Run with:  streamlit run web-gui/app.py
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Goma FSF Console", layout="wide", page_icon="\U0001F30A")

st.title("Goma - Free-Surface Film Flow Console")
st.caption(
    "Companion visualization, **not** solver output. Illustrates the kind of moving-boundary "
    "free-surface problem Goma is built to solve -- see [gomafem.com](https://www.gomafem.com) "
    "for the real thing."
)

with st.sidebar:
    st.header("Process parameters")
    flow = st.slider("Flow rate Q", 0.0, 1.0, 0.5, 0.01)
    visc = st.slider("Viscosity μ", 0.02, 1.0, 0.4, 0.01)
    tens = st.slider("Surface tension σ", 0.0, 1.0, 0.5, 0.01)
    cang = st.slider("Contact angle θ", 0.0, 1.0, 0.5, 0.01)
    n_frames = st.slider("Animation frames", 10, 60, 30, 5)


def height_field(x: np.ndarray, z: np.ndarray, t: float) -> np.ndarray:
    speed = 0.25 + 0.65 * flow
    damp1 = np.exp(-visc * 2.1)
    damp2 = (1 - tens) * 0.85 + 0.05
    wave1 = 0.16 * damp1 * np.sin(2 * np.pi * (x * 1.15 - t * speed))
    wave2 = 0.07 * damp2 * np.sin(2 * np.pi * (x * 2.6 - t * speed * 1.35))
    edge = np.cosh(z * 2.4) - 1
    wet_sign = (cang - 0.5) * 2
    meniscus = -0.10 * wet_sign * (1 - tens * 0.6) * edge / 3.0
    mean = 0.10 + 0.16 * flow
    return mean + wave1 + wave2 + meniscus


x = np.linspace(-1, 1, 46)
z = np.linspace(-0.5, 0.5, 20)
X, Z = np.meshgrid(x, z)

speed = 0.25 + 0.65 * flow
period = 1.0 / max(speed, 0.05)
t_values = np.linspace(0, period, n_frames, endpoint=False)

colorscale = [
    [0.00, "rgb(43,108,176)"],
    [0.30, "rgb(56,178,172)"],
    [0.55, "rgb(236,201,75)"],
    [0.78, "rgb(226,112,58)"],
    [1.00, "rgb(192,57,43)"],
]

frames = []
for i, t in enumerate(t_values):
    Y = height_field(X, Z, t)
    frames.append(go.Frame(data=[go.Surface(z=Y, x=X, y=Z, colorscale=colorscale, cmin=0.0, cmax=0.35, showscale=False)], name=str(i)))

fig = go.Figure(
    data=[go.Surface(z=height_field(X, Z, 0.0), x=X, y=Z, colorscale=colorscale, cmin=0.0, cmax=0.35, showscale=False)],
    frames=frames,
)
fig.update_layout(
    height=620,
    margin=dict(l=0, r=0, t=10, b=0),
    scene=dict(
        xaxis_title="flow direction (x)",
        yaxis_title="width (z)",
        zaxis_title="film height",
        aspectmode="manual",
        aspectratio=dict(x=2, y=1, z=0.5),
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        y=1, x=0, xanchor="left", yanchor="top",
        buttons=[
            dict(label="Play", method="animate",
                 args=[None, dict(frame=dict(duration=60, redraw=True), fromcurrent=True, mode="immediate")]),
            dict(label="Pause", method="animate",
                 args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]),
        ],
    )],
    sliders=[dict(
        steps=[dict(method="animate", args=[[str(i)], dict(mode="immediate", frame=dict(duration=0, redraw=True))], label="")
               for i in range(len(frames))],
        x=0.08, len=0.9,
    )],
)

st.plotly_chart(fig, use_container_width=True)

speed_val = 0.25 + 0.65 * flow
ca = (visc * (0.2 + speed_val)) / max(0.02, tens)
re = (1000 * (0.2 + speed_val) * (0.10 + 0.16 * flow)) / max(0.02, visc * 8)

cols = st.columns(4)
cols[0].metric("Mean film height", f"{(0.10 + 0.16 * flow) * 10:.2f} mm")
cols[1].metric("Wave speed", f"{speed_val * 8:.2f} mm/s")
cols[2].metric("Capillary number", f"{ca:.3f} Ca")
cols[3].metric("Reynolds number", f"{re:.1f} Re")

st.markdown(
    "This page renders an illustrative traveling-wave heightfield shaped by the sliders above -- "
    "it is **not** connected to Goma's actual Newton/FEM solver or to real Exodus output. See "
    "[web-gui/README.md](https://github.com/timeout187/goma/blob/main/web-gui/README.md) for scope "
    "notes and [BUILD.md](https://github.com/timeout187/goma/blob/main/BUILD.md) for building the "
    "real solver."
)
