"""
GridLock IQ - end-to-end pipeline runner.

Runs every stage in dependency order and prints a headline summary.
    python pipeline.py            # full run
    python pipeline.py --fast     # skip OSM download (heuristic road classes)
"""
import sys
import time
import importlib

sys.path.insert(0, "src")

STAGES = [
    ("clean",          "01 clean & parse"),
    ("road_fusion",    "02 road-network fusion"),
    ("cis",            "03 congestion-impact score + H3"),
    ("hotspots",       "04 Getis-Ord Gi* hotspots"),
    ("forecast",       "05 next-shift risk forecast"),
    ("patrol",         "06 patrol optimizer"),
    ("rejection",      "07 wasted-enforcement model"),
    ("chronic",        "08 chronic-site intelligence"),
    ("sensitivity",    "10 weight-sensitivity sweep"),
    ("economics",      "11 economic (rupee) layer"),
    ("summary",        "09 KPI summary export"),
    ("make_figures",   "12 static deck figures"),
    ("export_web",     "13 export data for police web dashboard"),
]


def main():
    fast = "--fast" in sys.argv
    if fast:
        import os
        os.environ["GLIQ_FAST"] = "1"
    t0 = time.time()
    for mod, label in STAGES:
        print(f"\n{'='*70}\n>>> {label}\n{'='*70}")
        ts = time.time()
        try:
            m = importlib.import_module(mod)
            importlib.reload(m)
            m.run()
            print(f"[ok] {label} in {time.time()-ts:.1f}s")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[FAIL] {label}: {e}")
            if mod in ("clean", "cis"):
                print("Critical stage failed; stopping.")
                sys.exit(1)
    print(f"\nALL DONE in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
