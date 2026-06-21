"""
Step 10 - Weight-sensitivity / rank-stability sweep.

The #1 critique of any hand-weighted index is "your weights are arbitrary".
We answer it empirically: jitter every CIS weight by +/-25% across 300 random
draws, re-score, re-aggregate, and measure how stable the hotspot RANKING is.
If the top hotspots barely move, the conclusions don't depend on the exact
numbers. We also compare CIS ranking vs a naive raw-ticket-count ranking to show
CIS is doing something a count map is not.
"""
import json
import warnings
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import config as C

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(C.RANDOM_STATE)
N_DRAWS = 300
JITTER = 0.25          # +/-25%
TOPK = 20


def _jit(x):
    return x * RNG.uniform(1 - JITTER, 1 + JITTER)


def run():
    df = pd.read_parquet(C.SCORED_PARQUET,
                         columns=["h3_9", "primary_violation", "vehicle_type",
                                  "is_junction", "hour", "lane_count"])
    lane_factor = 1.0 / df["lane_count"].clip(1, 6)

    # baseline hex ranking (current weights)
    base_hex = (df.assign(cis=(df["primary_violation"].map(C.SEVERITY).fillna(C.SEVERITY_DEFAULT)
                               * df["vehicle_type"].map(C.FOOTPRINT).fillna(C.FOOTPRINT_DEFAULT)
                               * lane_factor
                               * np.where(df["is_junction"], C.JUNCTION_MULT, 1.0)
                               * df["hour"].map(lambda h: C.peak_multiplier(int(h)) if pd.notna(h) else 1.0)))
                .groupby("h3_9")["cis"].sum())
    base_rank = base_hex.rank(ascending=False)
    base_top = set(base_hex.sort_values(ascending=False).head(TOPK).index)

    # raw-count ranking (the "everyone else" baseline)
    count_hex = df.groupby("h3_9").size()
    count_top = set(count_hex.sort_values(ascending=False).head(TOPK).index)
    count_jac = len(base_top & count_top) / len(base_top | count_top)
    rho_count = spearmanr(base_rank, count_hex.reindex(base_rank.index).rank(ascending=False)).correlation

    jaccards, spearmans = [], []
    for _ in range(N_DRAWS):
        sev = {k: _jit(v) for k, v in C.SEVERITY.items()}
        foot = {k: _jit(v) for k, v in C.FOOTPRINT.items()}
        jmult = _jit(C.JUNCTION_MULT)
        pscale = RNG.uniform(1 - JITTER, 1 + JITTER)
        s = df["primary_violation"].map(sev).fillna(C.SEVERITY_DEFAULT)
        f = df["vehicle_type"].map(foot).fillna(C.FOOTPRINT_DEFAULT)
        j = np.where(df["is_junction"], jmult, 1.0)
        p = 1.0 + (df["hour"].map(lambda h: C.peak_multiplier(int(h)) if pd.notna(h) else 1.0) - 1.0) * pscale
        cis = s * f * lane_factor * j * p
        hexv = cis.groupby(df["h3_9"]).sum()
        top = set(hexv.sort_values(ascending=False).head(TOPK).index)
        jaccards.append(len(base_top & top) / len(base_top | top))
        spearmans.append(spearmanr(base_rank, hexv.reindex(base_rank.index).rank(ascending=False)).correlation)

    out = {
        "n_draws": N_DRAWS, "jitter_pct": int(JITTER * 100), "topk": TOPK,
        "top20_jaccard_median": round(float(np.median(jaccards)), 3),
        "top20_jaccard_p05": round(float(np.percentile(jaccards, 5)), 3),
        "ranking_spearman_median": round(float(np.median(spearmans)), 3),
        "cis_vs_count_top20_jaccard": round(float(count_jac), 3),
        "cis_vs_count_spearman": round(float(rho_count), 3),
    }
    (C.OUTPUTS / "metric_sensitivity.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print(f"[sens] INTERPRETATION: under +/-{int(JITTER*100)}% weight noise, the top-{TOPK} hotspots keep "
          f"~{out['top20_jaccard_median']*100:.0f}% overlap (Spearman {out['ranking_spearman_median']}). "
          f"CIS vs raw-count ranking differ (Spearman {out['cis_vs_count_spearman']}), so CIS is not just a count map.")
    return out


if __name__ == "__main__":
    run()
