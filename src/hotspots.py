"""
Step 04 - Statistically-significant hotspot detection (Getis-Ord Gi*).

A raw heatmap shows where counts are high; Gi* tells you where they are high
*beyond what spatial chance would produce*. We build a spatial-weights graph
over H3 cell centroids and compute a Gi* z-score per cell on total CIS, then
label statistically significant hot / cold spots with pseudo p-values.
"""
import warnings
import numpy as np
import pandas as pd

import config as C

warnings.filterwarnings("ignore")


def bh_fdr(pvals):
    """Benjamini-Hochberg FDR-adjusted p-values (q-values). 2,534 cells are tested,
    so an uncorrected alpha=0.05 admits ~127 false positives by chance alone; we
    control the false-discovery rate instead (review must-fix #2)."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n)
    out[order] = np.clip(q, 0, 1)
    return out


def classify(z, q):
    if q > 0.05:
        return "not significant"
    if z > 0:
        return "hot 99%" if q <= 0.01 else "hot 95%"
    return "cold 99%" if q <= 0.01 else "cold 95%"


def run():
    hexagg = pd.read_parquet(C.HEX_PARQUET)
    from libpysal.weights import KNN
    from esda.getisord import G_Local

    coords = hexagg[["lon", "lat"]].values  # (x, y)
    k = min(6, len(hexagg) - 1)
    w = KNN.from_array(coords, k=k)
    w.transform = "B"  # binary weights for Gi*

    from scipy.stats import norm
    y = hexagg["cis_sum"].values.astype(float)
    g = G_Local(y, w, transform="B", star=True, permutations=199, seed=C.RANDOM_STATE)
    hexagg["gi_z"] = g.Zs
    hexagg["gi_p_perm"] = g.p_sim                          # empirical permutation p (coarse, floored)
    # Analytical two-sided normal p from the Gi* z-score: NOT floored, so it works
    # with FDR across thousands of cells (permutation p floors at 1/(perm+1)).
    p_norm = 2.0 * norm.sf(np.abs(g.Zs))
    hexagg["gi_p"] = p_norm
    hexagg["gi_q"] = bh_fdr(p_norm)                        # BH-FDR adjusted
    hexagg["hotspot_class"] = [classify(z, q) for z, q in zip(g.Zs, hexagg["gi_q"])]

    summary = hexagg["hotspot_class"].value_counts()
    print(f"[gi*] hotspot classes (BH-FDR q<=0.05):\n{summary.to_string()}")
    hot = hexagg[hexagg["hotspot_class"].str.startswith("hot")]
    print(f"[gi*] {len(hot):,} FDR-significant HOT cells hold "
          f"{hot['cis_sum'].sum()/hexagg['cis_sum'].sum()*100:.1f}% of total CIS")

    hexagg.to_parquet(C.HOTSPOTS_PARQUET, index=False)
    print(f"[gi*] wrote {C.HOTSPOTS_PARQUET}")
    print(hexagg.sort_values("gi_z", ascending=False)
          [["h3_9", "lat", "lon", "n", "cis_sum", "gi_z", "gi_q", "hotspot_class", "top_station"]]
          .head(8).to_string(index=False))
    return hexagg


if __name__ == "__main__":
    run()
