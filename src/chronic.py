"""
Step 08 - Chronic-site & repeat-offender intelligence.

Some locations get ticketed almost every single day yet never improve - those
don't need more patrols, they need an engineering fix. This module finds the
persistently-reoffending micro-locations and emits a concrete infrastructure
recommendation per site, plus a repeat-offender leaderboard.
"""
import warnings
import numpy as np
import pandas as pd
import h3

import config as C

warnings.filterwarnings("ignore")

HEAVY = ["BUS (BMTC/KSRTC)", "PRIVATE BUS", "HGV", "LGV", "LORRY/GOODS VEHICLE", "TEMPO"]


def recommend(row) -> str:
    # most chronic = ticketed almost daily yet never improves -> patrols don't work
    if row["recurrence"] >= 0.80:
        return "Automated ANPR camera enforcement (ticketed daily, patrol-resistant)"
    if row["footpath_share"] >= 0.35:
        return "Footpath guard-railing / bollards to stop pavement parking"
    if row["heavy_share"] >= 0.25:
        return "Time-windowed loading bay; restrict heavy-vehicle loading to off-peak"
    if row["junction_share"] >= 0.5:
        return "Bollards + 'No Stopping' zone at junction; tow-on-sight"
    if row["top_road"] in ("primary", "trunk", "secondary"):
        return "Continuous no-parking marking + paid off-street parking nearby"
    return "Resident-permit / paid on-street parking scheme"


def run():
    df = pd.read_parquet(C.SCORED_PARQUET)
    df["is_footpath"] = df["primary_violation"].eq("PARKING ON FOOTPATH")
    df["is_heavy"] = df["vehicle_type"].isin(HEAVY)

    g = df.groupby("h3_10")
    sites = g.agg(
        n=("id", "size"),
        cis_sum=("cis", "sum"),
        active_days=("date", "nunique"),
        junction_share=("is_junction", "mean"),
        heavy_share=("is_heavy", "mean"),
        footpath_share=("is_footpath", "mean"),
        top_road=("road_class", lambda s: s.mode().iloc[0] if len(s.mode()) else "NA"),
        top_station=("police_station", lambda s: s.mode().iloc[0] if len(s.mode()) else "NA"),
        sample_addr=("location", lambda s: s.dropna().iloc[0] if s.notna().any() else "NA"),
    ).reset_index()

    n_days = df["date"].nunique()
    sites["recurrence"] = (sites["active_days"] / n_days).round(3)   # share of days active
    cen = sites["h3_10"].apply(lambda c: pd.Series(h3.cell_to_latlng(c), index=["lat", "lon"]))
    sites = pd.concat([sites, cen], axis=1)

    # "chronic" = active on many distinct days AND high cumulative impact
    sites["chronic_score"] = (sites["active_days"] * sites["cis_sum"]).round(1)
    chronic = sites[sites["active_days"] >= 20].sort_values("chronic_score", ascending=False).copy()
    chronic["recommendation"] = chronic.apply(recommend, axis=1)
    chronic = chronic.reset_index(drop=True)
    chronic.to_parquet(C.CHRONIC_PARQUET, index=False)
    print(f"[chronic] {len(chronic):,} chronic micro-sites (active >=20 days of {n_days})")
    print(chronic[["active_days", "n", "cis_sum", "top_road", "recommendation", "sample_addr"]]
          .head(8).to_string(index=False))

    # repeat offenders
    rep = (df.groupby("vehicle_number")
             .agg(violations=("id", "size"), cis_sum=("cis", "sum"),
                  vehicle_type=("vehicle_type", "first"),
                  fav_station=("police_station", lambda s: s.mode().iloc[0] if len(s.mode()) else "NA"))
             .reset_index().sort_values("violations", ascending=False))
    rep.head(200).to_parquet(C.PROC / "repeat_offenders.parquet", index=False)
    print(f"\n[chronic] vehicles with >=10 violations: {(rep['violations']>=10).sum():,}")
    print(f"[chronic] worst repeat offender: {rep['violations'].iloc[0]} violations")
    print(f"[chronic] wrote {C.CHRONIC_PARQUET}")
    return chronic


if __name__ == "__main__":
    run()
