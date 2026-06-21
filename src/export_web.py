"""
Export the pipeline results to a compact JSON the police web dashboard consumes.
Keeps the web app a static, dependency-free single page.
"""
import json
import warnings
import numpy as np
import pandas as pd
import h3

import config as C

warnings.filterwarnings("ignore")
OUT = C.ROOT / "app_web"
OUT.mkdir(exist_ok=True)


def run():
    scored = pd.read_parquet(C.SCORED_PARQUET)
    summary = json.loads(C.SUMMARY_JSON.read_text())

    # address per H3 cell (res 9) for labelling map points
    addr9 = (scored.dropna(subset=["location"]).groupby("h3_9")["location"]
             .agg(lambda s: s.mode().iloc[0] if len(s.mode()) else s.iloc[0]).to_dict())

    def short_addr(a):
        return str(a).split(",")[0].strip() if a else "Bengaluru"

    hot = pd.read_parquet(C.HOTSPOTS_PARQUET)
    hot = hot.sort_values("cis_sum", ascending=False).head(120)
    hotspots = [{
        "lat": round(r.lat, 5), "lon": round(r.lon, 5),
        "cis": int(r.cis_sum), "n": int(r.n),
        "station": r.top_station, "road": r.top_road,
        "cls": r.hotspot_class if "hotspot_class" in hot.columns else "",
        "addr": short_addr(addr9.get(r.h3_9)),
        "jshare": round(float(r.junction_share), 2),
    } for r in hot.itertuples()]

    plan = pd.read_parquet(C.PATROL_PARQUET).sort_values(["marshal", "stop_order"])
    patrol = [{
        "marshal": int(r.marshal) + 1, "stop": int(r.stop_order),
        "lat": round(r.lat, 5), "lon": round(r.lon, 5),
        "gain": int(r.gain_cis),
        "addr": short_addr(addr9.get(r.h3_9)),
    } for r in plan.itertuples()]

    seq = pd.read_parquet(C.PROC / "patrol_sequence.parquet").head(180)
    sequence = [{"order": int(r.order), "lat": round(r.lat, 5), "lon": round(r.lon, 5),
                 "gain": int(r.gain_cis), "cum": round(float(r.cum_pct), 1),
                 "addr": short_addr(addr9.get(h3.latlng_to_cell(r.lat, r.lon, C.H3_RES)))}
                for r in seq.itertuples()]

    curve = pd.read_parquet(C.PROC / "patrol_curve.parquet")
    curve_pts = [{"m": int(r.n_marshals), "pct": round(float(r.pct_cis_captured), 1)}
                 for r in curve.drop_duplicates("n_marshals").itertuples()]

    chronic = pd.read_parquet(C.CHRONIC_PARQUET).head(40)
    chronic_sites = [{
        "lat": round(r.lat, 5), "lon": round(r.lon, 5),
        "addr": short_addr(r.sample_addr), "full_addr": str(r.sample_addr)[:90],
        "days": int(r.active_days), "n": int(r.n), "cis": int(r.cis_sum),
        "rec": r.recommendation, "road": r.top_road,
    } for r in chronic.itertuples()]

    fc = pd.read_parquet(C.FORECAST_PARQUET).head(120)
    forecast = [{"lat": round(r.lat, 5), "lon": round(r.lon, 5),
                 "pred": round(float(r.pred_cis), 1)} for r in fc.itertuples()]

    rej = pd.read_parquet(C.PROC / "rejection_by_station.parquet").head(12)
    rejection = [{"station": r.police_station, "prob": round(float(r.mean_reject_prob), 3),
                  "wasted": int(r.est_wasted_tickets)} for r in rej.itertuples()]

    rep = pd.read_parquet(C.PROC / "repeat_offenders.parquet").head(12)
    repeat = [{"veh": r.vehicle_number, "n": int(r.violations), "cis": int(r.cis_sum),
               "type": r.vehicle_type, "station": r.fav_station} for r in rep.itertuples()]

    # impact breakdowns for analyst charts
    by_veh = (scored.groupby("vehicle_type")["cis"].sum().sort_values(ascending=False).head(8))
    by_vio = (scored.groupby("primary_violation")["cis"].sum().sort_values(ascending=False).head(8))
    impact_by_vehicle = [{"name": k, "cis": int(v)} for k, v in by_veh.items()]
    impact_by_violation = [{"name": k.title(), "cis": int(v)} for k, v in by_vio.items()]
    by_hour = scored.groupby("hour")["cis"].sum().reindex(range(24), fill_value=0)
    impact_by_hour = [int(v) for v in by_hour.values]

    data = {
        "summary": summary, "hotspots": hotspots, "patrol": patrol,
        "sequence": sequence, "curve": curve_pts, "chronic": chronic_sites,
        "forecast": forecast, "rejection": rejection, "repeat": repeat,
        "impact_by_vehicle": impact_by_vehicle, "impact_by_violation": impact_by_violation,
        "impact_by_hour": impact_by_hour,
        "center": [12.9716, 77.5946],
    }
    (OUT / "data.json").write_text(json.dumps(data), encoding="utf-8")
    # also embed as a JS global so the pages work when opened directly (file://),
    # where fetch() is blocked by the browser.
    (OUT / "data.js").write_text("window.GLIQ_DATA=" + json.dumps(data) + ";", encoding="utf-8")
    print(f"[web] wrote data.json + data.js | hotspots={len(hotspots)} patrol={len(patrol)} "
          f"chronic={len(chronic_sites)} seq={len(sequence)}")
    return data


if __name__ == "__main__":
    run()
