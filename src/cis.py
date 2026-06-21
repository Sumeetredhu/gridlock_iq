"""
Step 03 - Congestion-Impact Score (CIS) + H3 aggregation.

CIS turns each parking violation into a physically-grounded estimate of how
much moving-traffic capacity it removes:

    CIS = severity x footprint x (1 / lane_count) x junction_mult x peak_mult

  - severity     : how directly the offence blocks the carriageway (footpath << main road)
  - footprint    : roadway area the stopped vehicle occupies (scooter << bus)
  - 1/lane_count : capacity fraction lost - blocking 1 of 2 lanes >> 1 of 6
  - junction_mult: queue spill-back penalty at intersections (data-grounded flag)
  - peak_mult    : relative rush-hour exposure

Interpretable as a relative "lane-capacity-minutes lost" proxy. We then bin
every ticket into H3 hex cells (res 9 ~0.1 km2) and build hex and hex-time
aggregates for hotspot detection, forecasting and the dashboard.
"""
import warnings
import numpy as np
import pandas as pd
import h3

import config as C

warnings.filterwarnings("ignore")


def run():
    df = pd.read_parquet(C.CLEAN_PARQUET)
    road = pd.read_parquet(C.ROAD_LOOKUP)

    df["latc"] = df["latitude"].round(5)
    df["lonc"] = df["longitude"].round(5)
    df = df.merge(road, on=["latc", "lonc"], how="left")
    df["lane_count"] = df["lane_count"].fillna(C.DEFAULT_LANES).clip(1, 6)
    df["road_class"] = df["road_class"].fillna("tertiary")
    df["road_source"] = df["road_source"].fillna("heuristic")
    if "lane_source" in df.columns:
        df["lane_source"] = df["lane_source"].fillna("class_inferred")
    else:
        df["lane_source"] = "class_inferred"

    # --- CIS ----------------------------------------------------------------
    df["lane_factor"] = 1.0 / df["lane_count"]
    df["cis_raw"] = (df["severity"] * df["footprint"] * df["lane_factor"]
                     * df["junction_mult"] * df["peak_mult"])
    # readable units: scale so a "typical bad ticket" ~ a few points
    df["cis"] = (df["cis_raw"] * 100).round(3)
    # 0-100 percentile index for display
    df["cis_index"] = (df["cis_raw"].rank(pct=True) * 100).round(1)

    # --- H3 cells -----------------------------------------------------------
    df["h3_9"] = [h3.latlng_to_cell(la, lo, C.H3_RES)
                  for la, lo in zip(df["latitude"], df["longitude"])]
    df["h3_10"] = [h3.latlng_to_cell(la, lo, C.H3_RES_FINE)
                   for la, lo in zip(df["latitude"], df["longitude"])]

    df.to_parquet(C.SCORED_PARQUET, index=False)
    print(f"[cis] scored {len(df):,} tickets | total CIS = {df['cis'].sum():,.0f}")
    print(f"[cis] CIS describe:\n{df['cis'].describe(percentiles=[.5,.9,.99]).round(3).to_string()}")
    print(f"[cis] road source mix: {df['road_source'].value_counts(normalize=True).round(3).to_dict()}")

    # --- hex aggregate ------------------------------------------------------
    def cen(cell):
        la, lo = h3.cell_to_latlng(cell)
        return pd.Series({"lat": la, "lon": lo})

    g = df.groupby("h3_9")
    hexagg = g.agg(
        n=("id", "size"),
        cis_sum=("cis", "sum"),
        cis_mean=("cis", "mean"),
        n_junction=("is_junction", "sum"),
        n_car=("vehicle_type", lambda s: (s == "CAR").sum()),
        n_heavy=("vehicle_type", lambda s: s.isin(
            ["BUS (BMTC/KSRTC)", "PRIVATE BUS", "HGV", "LGV", "LORRY/GOODS VEHICLE"]).sum()),
        mean_lanes=("lane_count", "mean"),
        top_station=("police_station", lambda s: s.mode().iloc[0] if len(s.mode()) else "NA"),
        top_road=("road_class", lambda s: s.mode().iloc[0] if len(s.mode()) else "NA"),
    ).reset_index()
    cents = hexagg["h3_9"].apply(cen)
    hexagg = pd.concat([hexagg, cents], axis=1)
    hexagg["junction_share"] = (hexagg["n_junction"] / hexagg["n"]).round(3)
    hexagg = hexagg.sort_values("cis_sum", ascending=False).reset_index(drop=True)
    hexagg["cis_rank"] = np.arange(1, len(hexagg) + 1)
    hexagg.to_parquet(C.HEX_PARQUET, index=False)
    print(f"[cis] {len(hexagg):,} hex cells | top cell CIS={hexagg['cis_sum'].iloc[0]:,.0f}")

    # --- hex x time aggregate (for forecasting) -----------------------------
    ht = (df.groupby(["h3_9", "date", "hour", "dow"])
            .agg(n=("id", "size"), cis_sum=("cis", "sum"))
            .reset_index())
    ht.to_parquet(C.HEX_TIME_PARQUET, index=False)
    print(f"[cis] hex-time rows: {len(ht):,}")
    print(f"[cis] wrote scored + hex + hex_time parquets")
    return df


if __name__ == "__main__":
    run()
