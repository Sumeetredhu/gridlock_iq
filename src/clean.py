"""
Step 01 - Load & clean the raw enforcement CSV.

Produces one tidy row per ticket with parsed violation lists, IST time
features, a junction flag, and a worst-case severity label. Writes
violations_clean.parquet (the spine every downstream module reads).
"""
import ast
import warnings
import numpy as np
import pandas as pd

import config as C

warnings.filterwarnings("ignore")

# Columns that profiling showed are 100% NULL or pure bookkeeping noise.
DROP_COLS = ["description", "action_taken_timestamp", "closed_datetime",
             "data_sent_to_scita_timestamp", "modified_datetime", "device_id"]


def _parse_list(x):
    """Parse a stringified JSON array like '[\"WRONG PARKING\"]' -> list[str]."""
    if isinstance(x, list):
        return x
    if not isinstance(x, str) or not x.strip() or x == "NULL":
        return []
    try:
        v = ast.literal_eval(x)
        return v if isinstance(v, list) else [v]
    except Exception:
        return [x]


def _worst_severity(viol_list):
    if not viol_list:
        return C.SEVERITY_DEFAULT, "OTHER"
    best, label = -1.0, "OTHER"
    for v in viol_list:
        s = C.SEVERITY.get(str(v).strip().upper(), C.SEVERITY_DEFAULT)
        if s > best:
            best, label = s, str(v).strip().upper()
    return best, label


def run():
    print(f"[clean] reading {C.RAW_CSV.name} ...")
    df = pd.read_csv(C.RAW_CSV, low_memory=False)
    n0 = len(df)
    print(f"[clean] raw rows: {n0:,}")

    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")

    # --- parse list fields ------------------------------------------------
    df["violations"] = df["violation_type"].apply(_parse_list)
    df["offence_codes"] = df["offence_code"].apply(_parse_list)
    df["n_violations"] = df["violations"].apply(len)
    sev = df["violations"].apply(_worst_severity)
    df["severity"] = sev.apply(lambda t: t[0])
    df["primary_violation"] = sev.apply(lambda t: t[1])

    # is the ticket congestion-relevant (a parking offence at all)?
    df["is_parking"] = df["violations"].apply(
        lambda lst: any(str(v).strip().upper() in C.PARKING_VIOLATIONS for v in lst)
    )

    # --- time features (UTC -> IST) --------------------------------------
    t = pd.to_datetime(df["created_datetime"], errors="coerce", utc=True)
    ist = t.dt.tz_convert(C.IST)
    df["ts_ist"] = ist
    df["date"] = ist.dt.date.astype("string")
    df["hour"] = ist.dt.hour.astype("Int16")
    df["dow"] = ist.dt.dayofweek.astype("Int16")          # 0=Mon
    df["is_weekend"] = df["dow"].isin([5, 6])
    df["month"] = ist.dt.to_period("M").astype("string")
    df["peak_mult"] = df["hour"].apply(
        lambda h: C.peak_multiplier(int(h)) if pd.notna(h) else 1.0
    )

    # --- geography --------------------------------------------------------
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    b = C.BLR_BBOX
    in_box = (
        df["latitude"].between(b["min_lat"], b["max_lat"])
        & df["longitude"].between(b["min_lon"], b["max_lon"])
    )
    dropped_geo = int((~in_box).sum())
    df = df[in_box].copy()

    df["is_junction"] = df["junction_name"].fillna("No Junction").ne("No Junction")
    df["junction_mult"] = np.where(df["is_junction"], C.JUNCTION_MULT, C.NONJUNCTION_MULT)

    # --- vehicle / validation --------------------------------------------
    df["vehicle_type"] = df["vehicle_type"].fillna("UNKNOWN").str.upper().str.strip()
    df["footprint"] = df["vehicle_type"].map(C.FOOTPRINT).fillna(C.FOOTPRINT_DEFAULT)
    df["validation_status"] = df["validation_status"].fillna("not_reviewed")

    # --- dedup ------------------------------------------------------------
    df = df.drop_duplicates(subset=["id"])

    keep = [
        "id", "latitude", "longitude", "location", "vehicle_number", "vehicle_type",
        "footprint", "violations", "offence_codes", "n_violations", "primary_violation",
        "severity", "is_parking", "violation_type",
        "ts_ist", "date", "hour", "dow", "is_weekend", "month", "peak_mult",
        "police_station", "junction_name", "is_junction", "junction_mult",
        "center_code", "validation_status",
    ]
    keep = [c for c in keep if c in df.columns]
    out = df[keep].reset_index(drop=True)

    # parquet can't store python lists of str cleanly via fastparquet; use json
    out["violations"] = out["violations"].apply(lambda x: list(map(str, x)))
    out["offence_codes"] = out["offence_codes"].apply(lambda x: list(map(str, x)))

    out.to_parquet(C.CLEAN_PARQUET, index=False)
    print(f"[clean] dropped out-of-bbox: {dropped_geo:,} | final rows: {len(out):,}")
    print(f"[clean] parking-relevant: {out['is_parking'].mean()*100:.1f}%")
    print(f"[clean] at junction: {out['is_junction'].mean()*100:.1f}%")
    print(f"[clean] wrote {C.CLEAN_PARQUET}")
    return out


if __name__ == "__main__":
    run()
