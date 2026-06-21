"""
Step 05 - Next-shift congestion-impact forecast.

Backward heatmaps tell you where enforcement already happened. To deploy
patrols *ahead* of the problem we forecast each hex cell's expected CIS for a
future (day-of-week x hour) shift, using a LightGBM regressor on temporal +
static-location features. Evaluated with a TEMPORAL holdout and, crucially,
Precision@K - of the cells we flag as tomorrow's worst, how many truly are.
"""
import warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, r2_score

import config as C

warnings.filterwarnings("ignore")


def run():
    ht = pd.read_parquet(C.HEX_TIME_PARQUET)           # h3_9, date, hour, dow, n, cis_sum
    hexagg = pd.read_parquet(C.HEX_PARQUET)[
        ["h3_9", "lat", "lon", "junction_share", "mean_lanes", "top_road"]]
    ht = ht.merge(hexagg, on="h3_9", how="left")
    ht["date"] = pd.to_datetime(ht["date"])
    ht["is_weekend"] = ht["dow"].isin([5, 6]).astype(int)
    ht["dom"] = ht["date"].dt.day
    ht["top_road"] = ht["top_road"].astype("category")

    # temporal split: last 20% of dates = test
    cutoff = ht["date"].quantile(0.8)
    tr = ht[ht["date"] <= cutoff].copy()
    te = ht[ht["date"] > cutoff].copy()

    # leakage-safe location priors from TRAIN only
    prior = tr.groupby("h3_9").agg(hex_mean_cis=("cis_sum", "mean"),
                                   hex_n=("cis_sum", "size")).reset_index()
    tr = tr.merge(prior, on="h3_9", how="left")
    te = te.merge(prior, on="h3_9", how="left")
    te["hex_mean_cis"] = te["hex_mean_cis"].fillna(tr["cis_sum"].mean())
    te["hex_n"] = te["hex_n"].fillna(0)

    feats = ["hour", "dow", "is_weekend", "dom", "lat", "lon",
             "junction_share", "mean_lanes", "hex_mean_cis", "hex_n", "top_road"]
    ytr = np.log1p(tr["cis_sum"].values)
    reg = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.05, num_leaves=63,
                            subsample=0.8, colsample_bytree=0.8,
                            random_state=C.RANDOM_STATE, verbose=-1)
    reg.fit(tr[feats], ytr, categorical_feature=["top_road"])
    pred = np.expm1(reg.predict(te[feats]))
    pred = np.clip(pred, 0, None)
    mae = mean_absolute_error(te["cis_sum"], pred)
    r2 = r2_score(te["cis_sum"], pred)
    print(f"[fcast] temporal holdout: MAE={mae:.2f} CIS | R2={r2:.3f} "
          f"(n_test={len(te):,})")

    # NAIVE PERSISTENCE BASELINE (review high-value add): rank cells by train-only
    # historical mean CIS, no model. Proves the LightGBM adds real lift vs. just
    # "yesterday's worst cells are tomorrow's worst".
    base_pred = te["hex_mean_cis"].fillna(te["hex_mean_cis"].mean()).values
    base_mae = mean_absolute_error(te["cis_sum"], base_pred)
    print(f"[fcast] baseline (historical-mean) MAE={base_mae:.2f}")

    # operational metric: Precision@K of predicted worst cells per test day
    te = te.assign(pred=pred, base=base_pred)
    K = 30
    precs, base_precs = [], []
    for d, grp in te.groupby(te["date"].dt.date):
        agg = grp.groupby("h3_9").agg(actual=("cis_sum", "sum"),
                                      pred=("pred", "sum"), base=("base", "sum"))
        if len(agg) < K:
            continue
        top_act = set(agg.sort_values("actual", ascending=False).head(K).index)
        precs.append(len(set(agg.sort_values("pred", ascending=False).head(K).index) & top_act) / K)
        base_precs.append(len(set(agg.sort_values("base", ascending=False).head(K).index) & top_act) / K)
    prec_at_k = float(np.mean(precs)) if precs else None
    base_prec = float(np.mean(base_precs)) if base_precs else None
    if precs:
        lift = (prec_at_k - base_prec) if base_prec is not None else None
        print(f"[fcast] Precision@{K}: model={prec_at_k:.3f} vs baseline={base_prec:.3f} "
              f"(lift +{lift:.3f}) over {len(precs)} days")
    import json
    (C.OUTPUTS / "metric_forecast.json").write_text(json.dumps({
        "mae": round(float(mae), 2), "r2": round(float(r2), 3),
        "precision_at_k": round(prec_at_k, 3) if prec_at_k else None,
        "baseline_precision_at_k": round(base_prec, 3) if base_prec else None,
        "baseline_mae": round(float(base_mae), 2), "k": K,
    }))

    # --- produce the actual NEXT-SHIFT forecast ----------------------------
    # refit on all data, predict the upcoming morning peak (dow after last date)
    prior_all = ht.groupby("h3_9").agg(hex_mean_cis=("cis_sum", "mean"),
                                       hex_n=("cis_sum", "size")).reset_index()
    full = ht.merge(prior_all, on="h3_9", how="left")
    reg.fit(full[feats], np.log1p(full["cis_sum"].values), categorical_feature=["top_road"])

    last_date = ht["date"].max()
    target_dow = int((last_date.dayofweek + 1) % 7)
    base = hexagg.merge(prior_all, on="h3_9", how="left")
    grid = []
    for hr in (9, 10, 11):                       # morning peak window
        tmp = base.copy()
        tmp["hour"] = hr
        grid.append(tmp)
    grid = pd.concat(grid, ignore_index=True)
    grid["dow"] = target_dow
    grid["is_weekend"] = int(target_dow in (5, 6))
    grid["dom"] = int(last_date.day)
    grid["top_road"] = grid["top_road"].astype("category")
    grid["pred_cis"] = np.clip(np.expm1(reg.predict(grid[feats])), 0, None)

    fc = (grid.groupby(["h3_9", "lat", "lon"])
              .agg(pred_cis=("pred_cis", "sum"),
                   junction_share=("junction_share", "first"))
              .reset_index().sort_values("pred_cis", ascending=False))
    fc["rank"] = np.arange(1, len(fc) + 1)
    fc["target_dow"] = target_dow
    fc.to_parquet(C.FORECAST_PARQUET, index=False)
    print(f"[fcast] forecast for next dow={target_dow} morning peak; "
          f"top cell pred_cis={fc['pred_cis'].iloc[0]:.1f}")
    print(f"[fcast] wrote {C.FORECAST_PARQUET}")
    return fc


if __name__ == "__main__":
    run()
