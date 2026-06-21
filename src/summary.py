"""
Step 09 - Headline KPI export.

Reads every pipeline artifact and writes outputs/summary.json - the single
source of truth for the dashboard hero numbers and the pitch deck.
"""
import json
import warnings
import numpy as np
import pandas as pd

import config as C

warnings.filterwarnings("ignore")

# assumptions for impact translation (clearly labelled, conservative)
MIN_PER_REVIEW = 4        # officer-minutes to review/process one ticket


def _load_json(p):
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def run():
    scored = pd.read_parquet(C.SCORED_PARQUET)
    hexa = pd.read_parquet(C.HEX_PARQUET)
    hot = pd.read_parquet(C.HOTSPOTS_PARQUET) if C.HOTSPOTS_PARQUET.exists() else hexa
    curve = pd.read_parquet(C.PROC / "patrol_curve.parquet")
    chronic = pd.read_parquet(C.CHRONIC_PARQUET)
    mr = _load_json(C.OUTPUTS / "metric_rejection.json")
    mf = _load_json(C.OUTPUTS / "metric_forecast.json")
    msens = _load_json(C.OUTPUTS / "metric_sensitivity.json")
    mecon = _load_json(C.OUTPUTS / "metric_economics.json")

    total_cis = float(scored["cis"].sum())
    hot_cells = hot[hot["hotspot_class"].astype(str).str.startswith("hot")] if "hotspot_class" in hot else hexa.head(108)
    hot_share = float(hot_cells["cis_sum"].sum() / hexa["cis_sum"].sum() * 100)
    # most-common real address per H3 cell (fixes collision from lat/lon 2-dp rounding)
    addr_by_cell = (scored.dropna(subset=["location"])
                    .groupby("h3_9")["location"]
                    .agg(lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0])
                    .to_dict())

    # how many marshals to capture 50% of impact
    c50 = curve[curve["pct_cis_captured"] >= 50]
    marshals_50 = int(c50["n_marshals"].iloc[0]) if len(c50) else None
    cap12 = curve[curve["n_marshals"] <= 12]["pct_cis_captured"].max()

    top = hexa.head(10)[["h3_9", "lat", "lon", "n", "cis_sum", "top_station", "top_road",
                         "junction_share"]].round(2)
    top_hotspots = top.to_dict("records")
    for h in top_hotspots:
        h["sample_addr"] = str(addr_by_cell.get(h["h3_9"], "NA"))[:80]
        h.pop("h3_9", None)

    est_wasted = mr.get("est_wasted_tickets", 0)
    officer_hours_window = round(est_wasted * MIN_PER_REVIEW / 60)
    # window length from the data (review must-fix #4: it's ~5 months, NOT a year)
    dmin = pd.to_datetime(scored["date"].min())
    dmax = pd.to_datetime(scored["date"].max())
    window_days = max((dmax - dmin).days, 1)
    annualize = 365.0 / window_days
    officer_hours_year = round(officer_hours_window * annualize)

    summary = {
        "dataset": {
            "tickets": int(len(scored)),
            "date_min": str(scored["date"].min()),
            "date_max": str(scored["date"].max()),
            "stations": int(scored["police_station"].nunique()),
            "junction_share_pct": round(float(scored["is_junction"].mean() * 100), 1),
            "unique_vehicles": int(scored["vehicle_number"].nunique()),
        },
        "cis": {
            "total_cis": round(total_cis),
            "mean_cis": round(float(scored["cis"].mean()), 1),
            "hex_cells": int(len(hexa)),
            "n_hot_cells": int(len(hot_cells)),
            "hot_cells_cis_share_pct": round(hot_share, 1),
            "osm_geometry_match_pct": round(float((scored["road_source"] == "osm").mean() * 100), 1),
            "explicit_osm_lane_tag_pct": round(float((scored.get("lane_source", pd.Series(["class_inferred"]*len(scored))) == "osm_lanes_tag").mean() * 100), 1),
        },
        "forecast": mf,
        "patrol": {
            "capture_12_marshals_pct": round(float(cap12), 1),
            "marshals_for_50pct": marshals_50,
            "stops_per_marshal": 6,
        },
        "enforcement_quality": {
            "reject_rate_pct": round(float((scored["validation_status"] == "rejected").mean() /
                                           max((scored["validation_status"].isin(["approved", "rejected"]).mean()), 1e-9) * 100), 1),
            "model_roc_auc": mr.get("roc_auc"),
            "est_wasted_tickets": est_wasted,
            "window_days": window_days,
            "est_officer_hours_saved_window": officer_hours_window,
            "est_officer_hours_saved_annual": officer_hours_year,
        },
        "chronic": {
            "chronic_sites": int(len(chronic)),
            "repeat_offenders_10plus": int((scored.groupby("vehicle_number").size() >= 10).sum()),
            "worst_offender_violations": int(scored.groupby("vehicle_number").size().max()),
        },
        "robustness": msens,
        "economics": mecon,
        "top_hotspots": top_hotspots,
    }
    C.SUMMARY_JSON.write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: summary[k] for k in
                      ["dataset", "cis", "forecast", "patrol", "enforcement_quality", "chronic"]},
                     indent=2))
    print(f"[summary] wrote {C.SUMMARY_JSON}")
    return summary


if __name__ == "__main__":
    run()
