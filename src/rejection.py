"""
Step 07 - Wasted-Enforcement (false-positive) model.

28.7% of human-reviewed tickets are REJECTED. Each rejected ticket is an
officer-hour spent on a bad capture. We learn the pattern of likely-rejected
tickets so enforcement can be pre-screened and review effort focused.

Target  : validation_status in {approved, rejected} (supervised on reviewed only)
Predicts: rejection probability for EVERY ticket -> station-level "wasted effort"
"""
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score
import lightgbm as lgb

import config as C

warnings.filterwarnings("ignore")

CAT = ["vehicle_type", "primary_violation", "police_station", "road_class"]
NUM = ["n_violations", "hour", "dow", "is_junction", "is_weekend", "severity", "footprint"]


def run():
    # prefer scored (has road_class); fall back to clean
    src = C.SCORED_PARQUET if C.SCORED_PARQUET.exists() else C.CLEAN_PARQUET
    df = pd.read_parquet(src)
    if "road_class" not in df.columns:
        df["road_class"] = "unknown"

    df["is_junction"] = df["is_junction"].astype(int)
    df["is_weekend"] = df["is_weekend"].astype(int)

    # FIX (review must-fix #1): lock categorical dtypes on the FULL frame so the
    # category->code mapping is identical at fit time and at scoring time.
    # (Re-running .astype('category') on a subset re-derives codes -> silent corruption.)
    for c in CAT:
        df[c] = df[c].astype("category")

    reviewed = df[df["validation_status"].isin(["approved", "rejected"])].copy()
    reviewed["y"] = (reviewed["validation_status"] == "rejected").astype(int)
    print(f"[rej] reviewed tickets: {len(reviewed):,} | base reject rate: {reviewed['y'].mean()*100:.1f}%")

    X = reviewed[CAT + NUM].copy()   # categories inherited from df, not re-derived
    y = reviewed["y"]

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.25, random_state=C.RANDOM_STATE, stratify=y)
    clf = lgb.LGBMClassifier(
        n_estimators=400, learning_rate=0.05, num_leaves=63,
        subsample=0.8, colsample_bytree=0.8, random_state=C.RANDOM_STATE, verbose=-1)
    clf.fit(Xtr, ytr, categorical_feature=CAT)
    p = clf.predict_proba(Xte)[:, 1]
    auc = roc_auc_score(yte, p)
    ap = average_precision_score(yte, p)
    print(f"[rej] holdout ROC-AUC={auc:.3f} | PR-AUC={ap:.3f} (base={yte.mean():.3f})")

    # top features
    imp = pd.Series(clf.feature_importances_, index=CAT + NUM).sort_values(ascending=False)
    print(f"[rej] top features:\n{imp.head(8).to_string()}")

    # score ALL tickets (same locked category dtypes -> codes match the fit)
    Xall = df[CAT + NUM].copy()
    df["reject_prob"] = clf.predict_proba(Xall)[:, 1]

    # station-level wasted-effort summary
    st = (df.groupby("police_station")
            .agg(n=("id", "size"), mean_reject_prob=("reject_prob", "mean"))
            .reset_index().sort_values("mean_reject_prob", ascending=False))
    st["est_wasted_tickets"] = (st["n"] * st["mean_reject_prob"]).round(0).astype(int)

    import json
    (C.OUTPUTS / "metric_rejection.json").write_text(json.dumps({
        "roc_auc": round(float(auc), 3), "pr_auc": round(float(ap), 3),
        "base_rate": round(float(yte.mean()), 3),
        "est_wasted_tickets": int(st["est_wasted_tickets"].sum()),
    }))
    df[["id", "police_station", "reject_prob"]].to_parquet(C.REJECTION_PARQUET, index=False)
    st.to_parquet(C.PROC / "rejection_by_station.parquet", index=False)
    print(f"[rej] est. wasted tickets (all data): {st['est_wasted_tickets'].sum():,}")
    print(f"[rej] worst stations:\n{st.head(6).to_string(index=False)}")
    print(f"[rej] wrote {C.REJECTION_PARQUET}")
    return df


if __name__ == "__main__":
    run()
