"""
GridLock IQ - Parking-Induced Congestion Command Center.

Run:  streamlit run app/streamlit_app.py
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")  # avoid Windows MKL KMeans warning

import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
from matplotlib import colormaps as mpl_cmaps

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as C

st.set_page_config(page_title="GridLock IQ", layout="wide", page_icon="🚦",
                   initial_sidebar_state="expanded")

# ----------------------------------------------------------------------------
# styling
# ----------------------------------------------------------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.2rem;}
[data-testid="stMetricValue"] {font-size: 1.7rem; color:#16e0a3;}
[data-testid="stMetricLabel"] {color:#9fb3c8;}
h1,h2,h3 {color:#e8eef5;}
.stApp {background: #0c1118;}
.kpi {background:linear-gradient(135deg,#10202e,#0c1118);border:1px solid #1d3343;
      border-radius:14px;padding:14px 16px;}
.tag {display:inline-block;background:#16e0a322;color:#16e0a3;border:1px solid #16e0a3;
      border-radius:8px;padding:2px 10px;font-size:.75rem;margin-right:6px;}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# data loaders (cached)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load():
    d = {}
    d["summary"] = json.loads((C.SUMMARY_JSON).read_text()) if C.SUMMARY_JSON.exists() else {}
    d["hex"] = pd.read_parquet(C.HOTSPOTS_PARQUET) if C.HOTSPOTS_PARQUET.exists() else pd.read_parquet(C.HEX_PARQUET)
    d["forecast"] = pd.read_parquet(C.FORECAST_PARQUET)
    d["seq"] = pd.read_parquet(C.PROC / "patrol_sequence.parquet")
    d["curve"] = pd.read_parquet(C.PROC / "patrol_curve.parquet")
    d["chronic"] = pd.read_parquet(C.CHRONIC_PARQUET)
    d["rej_station"] = pd.read_parquet(C.PROC / "rejection_by_station.parquet")
    d["repeat"] = pd.read_parquet(C.PROC / "repeat_offenders.parquet")
    return d


def ramp(series, cmap="inferno", alpha=170):
    s = series.astype(float)
    n = (s - s.min()) / (s.max() - s.min() + 1e-9)
    n = np.sqrt(n)  # emphasise mid-range
    colors = (mpl_cmaps[cmap](n)[:, :3] * 255).astype(int)
    return [[int(r), int(g), int(b), alpha] for r, g, b in colors]


def hex_layer(df, value="cis_sum", cmap="inferno", elev=True):
    df = df.copy()
    df["color"] = ramp(df[value], cmap)
    df["elev"] = (df[value] / df[value].max() * 3000) if elev else 0
    return pdk.Layer(
        "H3HexagonLayer", df, get_hexagon="h3_9", pickable=True, extruded=elev,
        get_fill_color="color", get_elevation="elev", elevation_scale=1,
        opacity=0.55, coverage=0.95,
    )


def deck(layers, tooltip, pitch=45, zoom=11):
    return pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=C.BLR_CENTER[0], longitude=C.BLR_CENTER[1],
                                         zoom=zoom, pitch=pitch, bearing=0),
        map_provider="carto", map_style="dark",
        tooltip=tooltip,
    )


D = load()
S = D["summary"]

# ----------------------------------------------------------------------------
# sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🚦 GridLock IQ")
    st.caption("Parking-Induced Congestion Intelligence — Bengaluru")
    ds = S.get("dataset", {})
    st.markdown(f"**{ds.get('tickets', 0):,}** tickets · "
                f"{ds.get('date_min','')} → {ds.get('date_max','')}")
    st.markdown(f"**{ds.get('stations',0)}** police stations · "
                f"**{ds.get('junction_share_pct',0)}%** at junctions")
    st.markdown("---")
    st.markdown("<span class='tag'>OSM lane-fusion</span><span class='tag'>Getis-Ord Gi*</span>"
                "<span class='tag'>LightGBM forecast</span><span class='tag'>Greedy optimizer</span>",
                unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Flipkart GRiD · ML track")

st.title("Parking-Induced Congestion Command Center")

tabs = st.tabs(["🗺️ Command Center", "🔥 Hotspots (Gi*)", "🔮 Forecast",
                "🚓 Patrol Optimizer", "✅ Enforcement Quality",
                "♻️ Chronic & Repeat", "📷 CV Detection"])

# ----------------------------------------------------------------------------
# 1. Command Center
# ----------------------------------------------------------------------------
with tabs[0]:
    cis = S.get("cis", {})
    eq = S.get("enforcement_quality", {})
    econ = S.get("economics", {})
    c = st.columns(5)
    c[0].metric("Congestion priority index", f"{cis.get('total_cis',0)/1e6:.2f}M", "relative impact units")
    c[1].metric("Hotspot cells (FDR)", f"{cis.get('n_hot_cells',0)}", "Gi* significant")
    c[2].metric("Impact in hotspots", f"{cis.get('hot_cells_cis_share_pct',0)}%", "of city total")
    c[3].metric("Est. congestion cost", f"₹{econ.get('total_cost_cr_year','—')} cr/yr", "planning estimate")
    c[4].metric("Enforcement ROI", f"{econ.get('enforcement_roi_x','—')}×", "12 units, cost relieved")
    c2 = st.columns(5)
    c2[0].metric("OSM geometry match", f"{cis.get('osm_geometry_match_pct',0)}%", "coords snapped")
    c2[1].metric("Explicit OSM lane tags", f"{cis.get('explicit_osm_lane_tag_pct',0)}%", "rest class-inferred")
    c2[2].metric("Officer-hrs saveable/yr", f"{eq.get('est_officer_hours_saved_annual',0):,}", "false positives")
    c2[3].metric("Chronic sites", f"{S.get('chronic',{}).get('chronic_sites',0):,}", "patrol-resistant")
    c2[4].metric("Repeat offenders", f"{S.get('chronic',{}).get('repeat_offenders_10plus',0):,}", "10+ tickets")

    st.markdown("#### Congestion-Impact heatmap — every ticket weighted by lanes blocked × footprint × junction × peak")
    st.pydeck_chart(deck(
        [hex_layer(D["hex"])],
        {"html": "<b>CIS:</b> {cis_sum}<br/><b>Tickets:</b> {n}<br/>"
                 "<b>Station:</b> {top_station}<br/><b>Road:</b> {top_road}"}),
        use_container_width=True, height=560)
    st.caption("Bars = total Congestion-Impact Score per ~0.1 km² hex cell. Taller & brighter = more carriageway capacity lost.")

# ----------------------------------------------------------------------------
# 2. Hotspots (Gi*)
# ----------------------------------------------------------------------------
with tabs[1]:
    st.markdown("#### Statistically-significant hotspots (Getis-Ord Gi*, 999 perms, BH-FDR q≤0.05)")
    hx = D["hex"].copy()
    if "hotspot_class" in hx.columns:
        palette = {"hot 99%": [220, 30, 40, 200], "hot 95%": [240, 120, 40, 190],
                   "not significant": [90, 110, 130, 60],
                   "cold 95%": [40, 120, 220, 150], "cold 99%": [20, 70, 200, 170]}
        hx["color"] = hx["hotspot_class"].map(palette)
        hx["elev"] = (hx["gi_z"].clip(lower=0) * 200)
        layer = pdk.Layer("H3HexagonLayer", hx, get_hexagon="h3_9", extruded=True,
                          get_fill_color="color", get_elevation="elev", pickable=True, opacity=0.6)
        st.pydeck_chart(deck([layer], {"html": "<b>{hotspot_class}</b><br/>Gi* z={gi_z}<br/>"
                                               "CIS={cis_sum}<br/>{top_station}"}),
                        use_container_width=True, height=520)
        hot = hx[hx["hotspot_class"].str.startswith("hot")].sort_values("gi_z", ascending=False)
        rob = S.get("robustness", {})
        st.markdown(f"**{len(hot)} FDR-significant hot cells** hold "
                    f"**{S.get('cis',{}).get('hot_cells_cis_share_pct',0)}%** of all congestion impact.")
        if rob:
            st.caption(f"🧪 Robustness: under ±{rob.get('jitter_pct',25)}% random weight noise "
                       f"({rob.get('n_draws',300)} draws) the top-{rob.get('topk',20)} hotspots keep a median "
                       f"**{rob.get('top20_jaccard_median',0)*100:.0f}%** overlap (ranking Spearman "
                       f"{rob.get('ranking_spearman_median','?')}). The conclusions don't depend on the exact weights.")
        cols = [c for c in ["lat","lon","n","cis_sum","gi_z","gi_q","top_station","top_road"] if c in hot.columns]
        st.dataframe(hot[cols].head(25).round(3), use_container_width=True, height=300)
    else:
        st.info("Run hotspots.py to populate Gi* layer.")

# ----------------------------------------------------------------------------
# 3. Forecast
# ----------------------------------------------------------------------------
with tabs[2]:
    mf = S.get("forecast", {})
    c = st.columns(4)
    c[0].metric("Forecast Precision@30", f"{mf.get('precision_at_k',0):.0%}", "next-day worst cells")
    base_p = mf.get('baseline_precision_at_k')
    c[1].metric("vs naive baseline", f"{base_p:.0%}" if base_p else "—",
                f"+{(mf.get('precision_at_k',0)-base_p)*100:.0f} pts lift" if base_p else "")
    c[2].metric("Holdout MAE", f"{mf.get('mae',0):.0f}", "CIS / hex-hour")
    c[3].metric("Target shift", f"DOW {D['forecast']['target_dow'].iloc[0]}", "morning peak 9–11")
    st.markdown("#### Predicted congestion-impact for the next shift — deploy *ahead* of the problem")
    fc = D["forecast"].head(300).copy()
    fc["color"] = ramp(fc["pred_cis"], "plasma")
    fc["elev"] = fc["pred_cis"] / fc["pred_cis"].max() * 2500
    layer = pdk.Layer("H3HexagonLayer", fc, get_hexagon="h3_9", extruded=True,
                      get_fill_color="color", get_elevation="elev", pickable=True, opacity=0.6)
    st.pydeck_chart(deck([layer], {"html": "Predicted CIS: {pred_cis}<br/>rank {rank}"}),
                    use_container_width=True, height=520)
    st.caption("LightGBM on temporal + static-location features, temporally validated. "
               "Precision@30 = of the 30 cells we flag as tomorrow's worst, the share that truly are.")

# ----------------------------------------------------------------------------
# 4. Patrol Optimizer  (the interactive wow)
# ----------------------------------------------------------------------------
with tabs[3]:
    st.markdown("#### How many patrol units — and where — to relieve the most congestion this shift?")
    n_marshals = st.slider("Patrol units deployed", 1, 30, 12)
    seq = D["seq"]
    n_stops = min(n_marshals * 6, len(seq))
    chosen = seq.head(n_stops).copy()
    captured = float(chosen["cum_pct"].iloc[-1])

    from sklearn.cluster import KMeans
    k = min(n_marshals, len(chosen))
    chosen["marshal"] = KMeans(n_clusters=k, n_init=4, random_state=42).fit_predict(chosen[["lat", "lon"]])
    pal = (mpl_cmaps["tab20"](np.linspace(0, 1, k))[:, :3] * 255).astype(int)
    chosen["color"] = chosen["marshal"].apply(lambda m: [int(x) for x in pal[m % k]] + [220])

    c = st.columns(3)
    c[0].metric("% city congestion impact captured", f"{captured:.0f}%")
    c[1].metric("Patrol stops", f"{n_stops}", f"{6} per unit")
    c[2].metric("Avg impact / unit", f"{captured/n_marshals:.1f}%", "marginal value")

    paths = []
    for m, g in chosen.sort_values(["marshal"]).groupby("marshal"):
        pts = g[["lon", "lat"]].values.tolist()
        if len(pts) > 1:
            paths.append({"path": pts, "color": [int(x) for x in pal[m % k]]})
    scatter = pdk.Layer("ScatterplotLayer", chosen, get_position=["lon", "lat"],
                        get_fill_color="color", get_radius=180, pickable=True, opacity=0.9)
    path_layer = pdk.Layer("PathLayer", pd.DataFrame(paths) if paths else pd.DataFrame({"path": [], "color": []}),
                           get_path="path", get_color="color", width_min_pixels=3)
    st.pydeck_chart(deck([scatter, path_layer],
                         {"html": "Marshal {marshal}<br/>added CIS: {gain_cis}"}, pitch=30),
                    use_container_width=True, height=480)

    cv = D["curve"]
    fig = px.area(cv, x="n_marshals", y="pct_cis_captured",
                  labels={"n_marshals": "Patrol units", "pct_cis_captured": "% impact captured"},
                  template="plotly_dark")
    fig.add_vline(x=n_marshals, line_color="#16e0a3")
    fig.update_traces(line_color="#16e0a3", fillcolor="rgba(22,224,163,0.15)")
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Greedy submodular max-coverage on forecasted impact (≥63% of optimal, fully explainable). "
               "Diminishing returns curve shows the right number of units to fund.")

# ----------------------------------------------------------------------------
# 5. Enforcement Quality
# ----------------------------------------------------------------------------
with tabs[4]:
    eq = S.get("enforcement_quality", {})
    c = st.columns(4)
    c[0].metric("Ticket rejection rate", f"{eq.get('reject_rate_pct',0)}%", "human-reviewed")
    c[1].metric("Model ROC-AUC", f"{eq.get('model_roc_auc',0)}", "predicts rejection")
    c[2].metric("Est. wasted tickets", f"{eq.get('est_wasted_tickets',0):,}", f"over {eq.get('window_days','~150')} days")
    c[3].metric("Officer-hours saveable", f"{eq.get('est_officer_hours_saved_annual',0):,}/yr",
                f"{eq.get('est_officer_hours_saved_window',0):,} in window")
    st.markdown("#### Where is enforcement effort being wasted? (predicted false-positive rate by station)")
    rs = D["rej_station"].head(20)
    fig = px.bar(rs, x="mean_reject_prob", y="police_station", orientation="h",
                 color="mean_reject_prob", color_continuous_scale="reds",
                 labels={"mean_reject_prob": "predicted reject probability", "police_station": ""},
                 template="plotly_dark")
    fig.update_layout(height=560, yaxis={"categoryorder": "total ascending"},
                      margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("A pre-capture screen on the highest-risk tickets focuses officer review where it pays off.")

# ----------------------------------------------------------------------------
# 6. Chronic & Repeat
# ----------------------------------------------------------------------------
with tabs[5]:
    ch = S.get("chronic", {})
    c = st.columns(3)
    c[0].metric("Chronic micro-sites", f"{ch.get('chronic_sites',0):,}", "active ≥20 days")
    c[1].metric("Repeat offenders (10+)", f"{ch.get('repeat_offenders_10plus',0):,}")
    c[2].metric("Worst offender", f"{ch.get('worst_offender_violations',0)}", "violations")
    st.markdown("#### Patrol-resistant chronic sites → infrastructure fixes (not more tickets)")
    cc = D["chronic"][["active_days", "n", "cis_sum", "top_road", "recommendation", "sample_addr"]].head(20)
    st.dataframe(cc.round(0), use_container_width=True, height=380)
    st.markdown("#### Repeat-offender leaderboard")
    st.dataframe(D["repeat"][["vehicle_number", "violations", "cis_sum", "vehicle_type", "fav_station"]].head(15),
                 use_container_width=True, height=300)

# ----------------------------------------------------------------------------
# 7. CV Detection
# ----------------------------------------------------------------------------
with tabs[6]:
    st.markdown("#### 📷 Live detection — turn any street image or video into auto-tickets")
    st.caption("Closes the loop: today's data is captured manually by marshals. "
               "A YOLOv8 detector on junction CCTV / patrol dashcams flags illegal parking in real time "
               "— feeding the very same CIS pipeline with zero human latency. "
               "The red band is the demo 'no-parking zone'; vehicles inside it are flagged ILLEGAL.")
    try:
        from cv_detect import detect_image, detect_video, HAS_YOLO, HAS_CV2
        if not HAS_YOLO:
            st.info("Install `ultralytics` to enable live detection: `pip install ultralytics`.")
        st.success("✅ YOLOv8 model is loaded — upload below to test." if HAS_YOLO else "Model not installed.")
        up = st.file_uploader("⬆️ Upload a street **image** (jpg/png) or short **video** (mp4/mov/avi)",
                              type=["jpg", "jpeg", "png", "mp4", "mov", "avi", "mkv"])
        st.caption("No file handy? Grab any street-parking photo from the web, or take one outside. "
                   "First run downloads the ~6 MB YOLO weights, so give it a few seconds.")
        if up is not None:
            name = (up.name or "").lower()
            is_video = name.endswith((".mp4", ".mov", ".avi", ".mkv"))
            with st.spinner("Running YOLOv8 detection…"):
                if is_video:
                    if not HAS_CV2:
                        st.error("Video needs OpenCV — run `pip install opencv-python`.")
                    else:
                        frames, results = detect_video(up.read(), max_frames=8)
                        c = st.columns(3)
                        c[0].metric("Frames sampled", results["frames_sampled"])
                        c[1].metric("Vehicles detected", results["total_vehicles"])
                        c[2].metric("Illegal detections", results["total_illegal_detections"])
                        cols = st.columns(2)
                        for i, fr in enumerate(frames):
                            cols[i % 2].image(fr, caption=f"frame {results['per_frame'][i]['frame']} · "
                                              f"{results['per_frame'][i]['illegal']} illegal",
                                              use_container_width=True)
                        st.json(results)
                else:
                    img, results = detect_image(up.read())
                    st.image(img, caption=f"Detected {results['n_vehicles']} vehicles · "
                                          f"{results['n_illegal']} in the no-parking zone",
                             use_container_width=True)
                    st.json(results)
    except Exception as e:
        st.warning(f"CV module not active ({e}). It's an optional extension — core demo is unaffected.")
