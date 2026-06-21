"""
Render static figures (PNG) for the pitch deck & README from the pipeline
artifacts. Pure matplotlib (no network), so they're reproducible and embeddable.
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import colormaps
import h3

import config as C

warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.facecolor": "#0c1118", "axes.facecolor": "#0c1118",
                     "savefig.facecolor": "#0c1118", "text.color": "#e8eef5",
                     "axes.labelcolor": "#9fb3c8", "xtick.color": "#5f7385",
                     "ytick.color": "#5f7385", "axes.edgecolor": "#1d3343"})


def _polys(cells):
    out = []
    for c in cells:
        b = h3.cell_to_boundary(c)            # list[(lat,lng)]
        out.append([(lng, lat) for lat, lng in b])
    return out


def cis_heatmap():
    hx = pd.read_parquet(C.HEX_PARQUET)
    fig, ax = plt.subplots(figsize=(9, 9))
    vals = np.log1p(hx["cis_sum"].values)
    norm = (vals - vals.min()) / (vals.max() - vals.min())
    colors = colormaps["inferno"](norm)
    pc = PolyCollection(_polys(hx["h3_9"]), facecolors=colors, edgecolors="none", alpha=0.92)
    ax.add_collection(pc)
    ax.autoscale_view()
    ax.set_aspect(1.0)
    ax.set_title("GridLock IQ — Congestion-Impact Score across Bengaluru\n"
                 f"{len(hx):,} hex cells · total CIS {hx['cis_sum'].sum()/1e6:.2f}M lane-capacity units",
                 fontsize=13, color="#e8eef5", pad=14)
    sm = plt.cm.ScalarMappable(cmap="inferno"); sm.set_array(hx["cis_sum"])
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02); cb.set_label("CIS per cell (log color)")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    fig.tight_layout(); fig.savefig(C.ASSETS / "fig_cis_heatmap.png", dpi=140); plt.close(fig)
    print("[fig] fig_cis_heatmap.png")


def hotspot_map():
    hx = pd.read_parquet(C.HOTSPOTS_PARQUET)
    palette = {"hot 99%": "#e6192a", "hot 95%": "#f5772a", "not significant": "#33414f",
               "cold 95%": "#2e7be6", "cold 99%": "#1545d6"}
    fig, ax = plt.subplots(figsize=(9, 9))
    cols = hx["hotspot_class"].map(palette).fillna("#33414f")
    pc = PolyCollection(_polys(hx["h3_9"]), facecolors=cols.values, edgecolors="none", alpha=0.9)
    ax.add_collection(pc); ax.autoscale_view(); ax.set_aspect(1.0)
    hot = hx[hx["hotspot_class"].str.startswith("hot")]
    ax.set_title(f"Statistically-significant hotspots (Getis-Ord Gi*)\n"
                 f"{len(hot)} hot cells hold "
                 f"{hot['cis_sum'].sum()/hx['cis_sum'].sum()*100:.1f}% of all congestion impact",
                 fontsize=13, color="#e8eef5", pad=14)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=v, label=k) for k, v in palette.items()],
              loc="upper right", facecolor="#10202e", edgecolor="#1d3343", labelcolor="#e8eef5")
    ax.set_xlabel("longitude"); ax.set_ylabel("latitude")
    fig.tight_layout(); fig.savefig(C.ASSETS / "fig_hotspots.png", dpi=140); plt.close(fig)
    print("[fig] fig_hotspots.png")


def patrol_curve():
    cv = pd.read_parquet(C.PROC / "patrol_curve.parquet")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.fill_between(cv["n_marshals"], cv["pct_cis_captured"], color="#16e0a3", alpha=0.18)
    ax.plot(cv["n_marshals"], cv["pct_cis_captured"], color="#16e0a3", lw=2.4)
    for m in (12,):
        y = cv[cv["n_marshals"] <= m]["pct_cis_captured"].max()
        ax.axvline(m, color="#9fb3c8", ls="--", lw=1)
        ax.annotate(f"{m} units → {y:.0f}%", (m, y), color="#16e0a3",
                    xytext=(m + 1, y - 8), fontsize=11)
    ax.set_title("Patrol optimizer — % of city congestion impact captured per shift",
                 fontsize=13, color="#e8eef5")
    ax.set_xlabel("patrol units deployed"); ax.set_ylabel("% impact captured")
    ax.grid(alpha=0.12)
    fig.tight_layout(); fig.savefig(C.ASSETS / "fig_patrol_curve.png", dpi=140); plt.close(fig)
    print("[fig] fig_patrol_curve.png")


def mix_figure():
    sc = pd.read_parquet(C.SCORED_PARQUET)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    vt = sc.groupby("vehicle_type")["cis"].sum().sort_values(ascending=False).head(8)[::-1]
    axes[0].barh(vt.index, vt.values, color="#16e0a3")
    axes[0].set_title("Congestion impact by vehicle type", color="#e8eef5")
    pv = sc.groupby("primary_violation")["cis"].sum().sort_values(ascending=False).head(8)[::-1]
    axes[1].barh(pv.index, pv.values, color="#f5772a")
    axes[1].set_title("Congestion impact by violation type", color="#e8eef5")
    for a in axes:
        a.grid(alpha=0.12, axis="x"); a.set_xlabel("total CIS")
    fig.tight_layout(); fig.savefig(C.ASSETS / "fig_impact_mix.png", dpi=140); plt.close(fig)
    print("[fig] fig_impact_mix.png")


def run():
    cis_heatmap(); hotspot_map(); patrol_curve(); mix_figure()
    print("[fig] all figures in", C.ASSETS)


if __name__ == "__main__":
    run()
