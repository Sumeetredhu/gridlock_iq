"""
Step 06 - Patrol optimizer (greedy weighted maximum-coverage).

Given the FORECASTED next-shift congestion impact and a fixed number of patrol
units, decide WHERE to send them to relieve the most congestion per shift.

A patrol stationed in a hex covers its immediate H3 neighbourhood. We greedily
pick the stop that adds the most still-uncovered predicted CIS (classic
submodular max-coverage; greedy is within 63% of optimal and fully explainable),
then cluster the chosen stops into per-marshal routes. Also emits the
"marshals vs % impact captured" curve that powers the dashboard slider.
"""
import warnings
import numpy as np
import pandas as pd
import h3
from sklearn.cluster import KMeans

import config as C

warnings.filterwarnings("ignore")

COVER_K = 1          # a stop covers its hex + 1 ring of neighbours (~0.5 km across)
STOPS_PER_MARSHAL = 6
DEFAULT_MARSHALS = 12


def _coverage(cell):
    return set(h3.grid_disk(cell, COVER_K))


def greedy_cover(weights: dict, budget: int):
    """weights: hex->predicted CIS. Returns ordered list of chosen stops + curve."""
    covered = set()
    chosen = []
    curve = []
    total = sum(weights.values())
    candidates = list(weights.keys())
    cover_cache = {c: _coverage(c) for c in candidates}
    captured = 0.0
    for _ in range(budget):
        best, best_gain = None, -1
        for c in candidates:
            gain = sum(weights.get(h, 0.0) for h in cover_cache[c] - covered)
            if gain > best_gain:
                best, best_gain = c, gain
        if best is None or best_gain <= 0:
            break
        chosen.append((best, best_gain))
        covered |= cover_cache[best]
        candidates.remove(best)
        captured += best_gain
        curve.append(captured / total if total else 0)
    return chosen, curve, total


def run():
    if C.FORECAST_PARQUET.exists():
        fc = pd.read_parquet(C.FORECAST_PARQUET).rename(columns={"pred_cis": "w"})
        wcol = "w"
        print("[patrol] optimizing against FORECASTED next-shift CIS")
    else:
        fc = pd.read_parquet(C.HEX_PARQUET).rename(columns={"cis_sum": "w"})
        print("[patrol] optimizing against historical CIS (no forecast found)")
    fc = fc[["h3_9", "lat", "lon", "w"]].dropna()
    weights = dict(zip(fc["h3_9"], fc["w"]))

    budget = DEFAULT_MARSHALS * STOPS_PER_MARSHAL
    chosen, curve, total = greedy_cover(weights, budget)
    print(f"[patrol] {len(chosen)} stops capture {curve[-1]*100:.1f}% of forecast CIS")

    # full coverage curve + ordered stop sequence up to 30 marshals (for the slider)
    big_budget = 30 * STOPS_PER_MARSHAL
    full_chosen, full_curve, _ = greedy_cover(weights, big_budget)
    curve_df = pd.DataFrame({
        "n_stops": np.arange(1, len(full_curve) + 1),
        "pct_cis_captured": np.array(full_curve) * 100,
    })
    curve_df["n_marshals"] = np.ceil(curve_df["n_stops"] / STOPS_PER_MARSHAL).astype(int)
    curve_df.to_parquet(C.PROC / "patrol_curve.parquet", index=False)

    # ordered greedy sequence so the dashboard can slice the first N*6 stops instantly
    seq = pd.DataFrame({
        "order": np.arange(1, len(full_chosen) + 1),
        "h3_9": [c for c, _ in full_chosen],
        "gain_cis": [g for _, g in full_chosen],
    })
    seq["lat"] = seq["h3_9"].apply(lambda c: h3.cell_to_latlng(c)[0])
    seq["lon"] = seq["h3_9"].apply(lambda c: h3.cell_to_latlng(c)[1])
    seq["cum_pct"] = np.array(full_curve) * 100
    seq.to_parquet(C.PROC / "patrol_sequence.parquet", index=False)

    # assign chosen stops to marshals via spatial clustering, then NN route order
    stops = pd.DataFrame({
        "h3_9": [c for c, _ in chosen],
        "gain_cis": [g for _, g in chosen],
    })
    stops["lat"] = stops["h3_9"].apply(lambda c: h3.cell_to_latlng(c)[0])
    stops["lon"] = stops["h3_9"].apply(lambda c: h3.cell_to_latlng(c)[1])
    km = KMeans(n_clusters=DEFAULT_MARSHALS, n_init=5, random_state=C.RANDOM_STATE)
    stops["marshal"] = km.fit_predict(stops[["lat", "lon"]])

    # order each marshal's stops by greedy nearest-neighbour from cluster centroid
    routes = []
    for m, grp in stops.groupby("marshal"):
        pts = grp.to_dict("records")
        cur = min(pts, key=lambda p: (p["lat"], p["lon"]))
        order = [cur]
        rem = [p for p in pts if p is not cur]
        while rem:
            nxt = min(rem, key=lambda p: (p["lat"] - cur["lat"]) ** 2 + (p["lon"] - cur["lon"]) ** 2)
            order.append(nxt)
            rem.remove(nxt)
            cur = nxt
        for i, p in enumerate(order):
            p["stop_order"] = i + 1
            routes.append(p)
    plan = pd.DataFrame(routes).sort_values(["marshal", "stop_order"]).reset_index(drop=True)
    plan.to_parquet(C.PATROL_PARQUET, index=False)

    print(f"[patrol] {DEFAULT_MARSHALS} marshals x {STOPS_PER_MARSHAL} stops; "
          f"plan rows={len(plan)}")
    print(f"[patrol] coverage curve: 5 marshals={curve_df.iloc[min(29,len(curve_df)-1)]['pct_cis_captured']:.0f}% "
          f"... {DEFAULT_MARSHALS} marshals={curve[-1]*100:.0f}%")
    print(f"[patrol] wrote {C.PATROL_PARQUET} + patrol_curve.parquet")
    return plan


if __name__ == "__main__":
    run()
