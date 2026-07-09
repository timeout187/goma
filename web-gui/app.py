"""
Goma Moving-Boundary Preview Console -- Streamlit companion
------------------------------------------------------------
An animated, orbitable 3D preview of two classic free/moving-boundary
problem classes Goma solves: thin-film coating flow and a sessile
droplet (wetting/contact-angle). Mirrors web-gui/index.html's two
problem types with the same slider semantics. Not connected to Goma's
actual Newton/FEM solver -- see web-gui/README.md.

Run with:  streamlit run web-gui/app.py
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Goma Preview Console", layout="wide", page_icon="\U0001F30A")

st.title("Goma - Moving-Boundary Preview Console")
st.caption(
    "Companion visualization, **not** solver output. Illustrates two of the classic "
    "free/moving-boundary problem classes Goma is built to solve -- see "
    "[gomafem.com](https://www.gomafem.com) for the real thing."
)

COLORSCALE = [
    [0.00, "rgb(43,108,176)"],
    [0.30, "rgb(56,178,172)"],
    [0.55, "rgb(236,201,75)"],
    [0.78, "rgb(226,112,58)"],
    [1.00, "rgb(192,57,43)"],
]

with st.sidebar:
    st.header("Problem type")
    mode_label = st.radio("Mode", ["Thin Film Flow", "Sessile Droplet"], label_visibility="collapsed")
    mode = "film" if mode_label == "Thin Film Flow" else "drop"

    st.header("Process parameters")
    if mode == "film":
        flow = st.slider("Flow rate Q", 0.0, 1.0, 0.5, 0.01)
    else:
        flow = st.slider("Droplet volume V", 0.0, 1.0, 0.5, 0.01)
    visc = st.slider("Viscosity μ", 0.02, 1.0, 0.4, 0.01)
    tens = st.slider("Surface tension σ", 0.0, 1.0, 0.5, 0.01)
    cang = st.slider("Contact angle θ", 0.0, 1.0, 0.5, 0.01)
    n_frames = st.slider("Animation frames", 10, 60, 30, 5)


def film_height(x: np.ndarray, z: np.ndarray, t: float) -> np.ndarray:
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


def drop_constants():
    footprint_r = 0.35 + 0.55 * flow
    theta_deg = 20 + cang * 120
    theta_rad = np.deg2rad(theta_deg)
    cap_height = min(footprint_r * np.tan(theta_rad / 2), footprint_r * 1.6)
    s = np.sin(theta_rad)
    sphere_r = footprint_r / s if abs(s) > 0.02 else footprint_r * 50
    osc_amp = 0.05 * (1 - min(0.95, visc * 0.8)) * (1 - tens * 0.7)
    osc_freq = 0.4 + 1.2 * tens
    return footprint_r, theta_deg, cap_height, sphere_r, osc_amp, osc_freq


def drop_height(r: np.ndarray, footprint_r, cap_height, sphere_r, osc_amp, osc_freq, t) -> np.ndarray:
    rr = r * footprint_r
    under = sphere_r * sphere_r - rr * rr
    base = np.sqrt(np.maximum(0, under)) - (sphere_r - cap_height)
    osc = 1 + osc_amp * np.sin(2 * np.pi * osc_freq * t)
    return np.maximum(0, base) * osc


if mode == "film":
    x = np.linspace(-1, 1, 46)
    z = np.linspace(-0.5, 0.5, 20)
    X, Z = np.meshgrid(x, z)
    speed = 0.25 + 0.65 * flow
    period = 1.0 / max(speed, 0.05)
    t_values = np.linspace(0, period, n_frames, endpoint=False)

    def surface_at(t):
        return X, Z, film_height(X, Z, t)

    aspect = dict(x=2, y=1, z=0.5)
    zrange = (0.0, 0.35)
else:
    footprint_r, theta_deg, cap_height, sphere_r, osc_amp, osc_freq = drop_constants()
    r = np.linspace(0, 1, 40)
    theta = np.linspace(0, 2 * np.pi, 60)
    R, TH = np.meshgrid(r, theta)
    X = R * footprint_r * np.cos(TH)
    Z = R * footprint_r * np.sin(TH)
    period = 1.0 / max(osc_freq, 0.1)
    t_values = np.linspace(0, period, n_frames, endpoint=False)

    def surface_at(t):
        return X, Z, drop_height(R, footprint_r, cap_height, sphere_r, osc_amp, osc_freq, t)

    aspect = dict(x=1, y=1, z=0.7)
    zrange = (0.0, max(0.3, cap_height * 1.15))

frames = []
for i, t in enumerate(t_values):
    _, _, Y = surface_at(t)
    frames.append(go.Frame(
        data=[go.Surface(z=Y, x=X, y=Z, colorscale=COLORSCALE, cmin=zrange[0], cmax=zrange[1], showscale=False)],
        name=str(i),
    ))

_, _, Y0 = surface_at(0.0)
fig = go.Figure(
    data=[go.Surface(z=Y0, x=X, y=Z, colorscale=COLORSCALE, cmin=zrange[0], cmax=zrange[1], showscale=False)],
    frames=frames,
)
fig.update_layout(
    height=620,
    margin=dict(l=0, r=0, t=10, b=0),
    scene=dict(
        xaxis_title="x" if mode == "drop" else "flow direction (x)",
        yaxis_title="y" if mode == "drop" else "width (z)",
        zaxis_title="height",
        aspectmode="manual",
        aspectratio=aspect,
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

cols = st.columns(4)
if mode == "film":
    speed_val = 0.25 + 0.65 * flow
    ca = (visc * (0.2 + speed_val)) / max(0.02, tens)
    re = (1000 * (0.2 + speed_val) * (0.10 + 0.16 * flow)) / max(0.02, visc * 8)
    cols[0].metric("Mean film height", f"{(0.10 + 0.16 * flow) * 10:.2f} mm")
    cols[1].metric("Wave speed", f"{speed_val * 8:.2f} mm/s")
    cols[2].metric("Capillary number", f"{ca:.3f} Ca")
    cols[3].metric("Reynolds number", f"{re:.1f} Re")
else:
    a_m = footprint_r * 0.01
    sigma_actual = 0.02 + 0.06 * tens
    bo = (1000 * 9.81 * a_m * a_m) / sigma_actual
    cols[0].metric("Footprint radius", f"{footprint_r * 10:.2f} mm")
    cols[1].metric("Cap height", f"{cap_height * 10:.2f} mm")
    cols[2].metric("Contact angle", f"{theta_deg:.0f} deg")
    cols[3].metric("Bond number", f"{bo:.3f} Bo")

st.markdown(
    "Both problem types render an illustrative surface shaped by the sliders above -- "
    "neither is connected to Goma's actual Newton/FEM solver or to real Exodus output. See "
    "[web-gui/README.md](https://github.com/timeout187/goma/blob/main/web-gui/README.md) for "
    "scope notes and [BUILD.md](https://github.com/timeout187/goma/blob/main/BUILD.md) for "
    "building the real solver."
)
