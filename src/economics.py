"""
Step 11 - Economic layer: price parking-induced congestion in rupees.

This converts the CIS index into a money figure a BBMP / Traffic Police buyer can
act on, via a FULLY TRANSPARENT, TUNABLE assumption chain (every constant below is
explicit and lives in one place). It is a PLANNING ESTIMATE, not a measured cost -
the absolute rupee figure scales linearly with these assumptions; the durable
results are the *concentration* (share of cost in hotspots) and the enforcement ROI.
"""
import json
import warnings
import numpy as np
import pandas as pd

import config as C

warnings.filterwarnings("ignore")

# ---- ASSUMPTIONS (all explicit & tunable) ----------------------------------
VOT_INR_PER_VEH_HR = 250.0     # value of travel time, Rs per vehicle-hour (mixed fleet, planning)
# Reference event used to calibrate CIS -> vehicle-hours of delay:
#   a car (footprint .60) wrong-parked (sev .65) blocking 1 of 2 lanes (1/L=.5),
#   non-junction, peak (1.5)  => cis_raw_ref below.
REF_CIS_RAW = 0.65 * 0.60 * 0.5 * 1.0 * 1.5
REF_DELAY_VEH_HR = 15.0        # assumed delay that reference event imposes (0.5h x ~1000 veh/h x ~0.03 coupling)
CALIB = REF_DELAY_VEH_HR / REF_CIS_RAW   # vehicle-hours of delay per unit cis_raw
# enforcement cost assumptions for ROI
OFFICER_COST_INR_PER_HR = 300.0
SHIFT_HOURS = 6.0


def run():
    df = pd.read_parquet(C.SCORED_PARQUET, columns=["h3_9", "cis", "cis_raw", "police_station"])
    dates = pd.read_parquet(C.SCORED_PARQUET, columns=["date"])
    window_days = max((pd.to_datetime(dates["date"].max()) - pd.to_datetime(dates["date"].min())).days, 1)
    ann = 365.0 / window_days

    df["delay_veh_hr"] = df["cis_raw"] * CALIB
    df["cost_inr"] = df["delay_veh_hr"] * VOT_INR_PER_VEH_HR
    total_window = df["cost_inr"].sum()
    total_year = total_window * ann

    # hotspot concentration
    try:
        hot = pd.read_parquet(C.HOTSPOTS_PARQUET)
        hot_cells = set(hot[hot["hotspot_class"].astype(str).str.startswith("hot")]["h3_9"])
    except Exception:
        hot_cells = set()
    hot_cost_year = df[df["h3_9"].isin(hot_cells)]["cost_inr"].sum() * ann

    # per-hotspot rupee value
    by_cell = (df.groupby("h3_9")["cost_inr"].sum().mul(ann)
                 .sort_values(ascending=False).head(15).reset_index()
                 .rename(columns={"cost_inr": "cost_inr_year"}))

    # enforcement ROI: 12 units capture ~32% of CIS (=cost). Compare relieved cost
    # to the patrol payroll required to capture it.
    try:
        curve = pd.read_parquet(C.PROC / "patrol_curve.parquet")
        cap12 = float(curve[curve["n_marshals"] <= 12]["pct_cis_captured"].max()) / 100.0
    except Exception:
        cap12 = 0.32
    relieved_year = total_year * cap12
    patrol_cost_year = 12 * SHIFT_HOURS * OFFICER_COST_INR_PER_HR * 365
    roi = relieved_year / patrol_cost_year if patrol_cost_year else None

    out = {
        "assumptions": {"vot_inr_per_veh_hr": VOT_INR_PER_VEH_HR,
                        "ref_delay_veh_hr": REF_DELAY_VEH_HR,
                        "calib_vehhr_per_cisraw": round(CALIB, 1),
                        "officer_cost_inr_per_hr": OFFICER_COST_INR_PER_HR},
        "total_cost_inr_year": round(total_year),
        "total_cost_cr_year": round(total_year / 1e7, 1),          # 1 crore = 1e7
        "hotspot_cost_cr_year": round(hot_cost_year / 1e7, 1),
        "hotspot_cost_share_pct": round(hot_cost_year / total_year * 100, 1) if total_year else 0,
        "delay_veh_hr_year": round(df["delay_veh_hr"].sum() * ann),
        "patrol12_relieved_cr_year": round(relieved_year / 1e7, 1),
        "patrol12_cost_cr_year": round(patrol_cost_year / 1e7, 2),
        "enforcement_roi_x": round(roi, 1) if roi else None,
    }
    by_cell.to_parquet(C.PROC / "economics_by_cell.parquet", index=False)
    (C.OUTPUTS / "metric_economics.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"[econ] HEADLINE: ~Rs {out['total_cost_cr_year']} cr/yr of parking-induced congestion "
          f"(planning estimate); {out['hotspot_cost_share_pct']}% sits in the Gi* hotspots. "
          f"12 patrol units relieve ~Rs {out['patrol12_relieved_cr_year']} cr/yr at ~Rs "
          f"{out['patrol12_cost_cr_year']} cr cost -> {out['enforcement_roi_x']}x ROI.")
    return out


if __name__ == "__main__":
    run()
