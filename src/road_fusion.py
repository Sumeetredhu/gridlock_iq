"""
Step 02 - Fuse violations with the road network to recover LANE COUNT &
ROAD CLASS for every location. This is what lets us turn a dot on a map
into "fraction of carriageway capacity removed".

Two sources, merged for robustness:
  (A) HEURISTIC from the address text (always available, instant) - infers
      road class from name cues ("Ring Road", "Main Road", "100 Feet", "Cross"...).
  (B) OPENSTREETMAP (osmnx) - snaps each unique coordinate to the nearest
      drivable road segment and reads its real `highway` class & `lanes` tag.

OSM wins when available; heuristic fills the gaps. The result is a per-coordinate
lookup of (road_class, lane_count, road_source).
"""
import re
import warnings
import numpy as np
import pandas as pd

import config as C

warnings.filterwarnings("ignore")

# road-class ranking (higher = more major / more lanes)
CLASS_RANK = {
    "motorway": 6, "trunk": 5, "primary": 4, "secondary": 3,
    "tertiary": 2, "residential": 1, "living_street": 0,
    "unclassified": 1, "service": 0,
}


# ---------------------------------------------------------------------------
# (A) Heuristic from address text
# ---------------------------------------------------------------------------
def heuristic_class(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["ring road", "nh ", "nh-", "national highway",
                            "flyover", "elevated", "expressway", "outer ring"]):
        return "trunk"
    if any(k in t for k in ["100 feet", "100feet", "100 ft", "80 feet", "80 ft",
                            "airport road", "hosur road", "old madras", "bannerghatta",
                            "sarjapur", "magadi road", "mysore road", "tumkur road"]):
        return "primary"
    if "main road" in t or "main rd" in t or "60 feet" in t or "40 feet" in t:
        return "secondary"
    if re.search(r"\b\d+(st|nd|rd|th)?\s+cross\b", t) or "cross road" in t:
        return "residential"
    if "road" in t or " rd" in t:
        return "tertiary"
    return "residential"


# ---------------------------------------------------------------------------
# (B) OSM helpers
# ---------------------------------------------------------------------------
def _parse_lanes(v):
    """lanes tag may be '2', ['2','3'], '2;3', '1.5' -> return max int found."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (list, tuple)):
        vals = []
        for x in v:
            vals += re.findall(r"\d+", str(x))
    else:
        vals = re.findall(r"\d+", str(v))
    vals = [int(x) for x in vals if x.isdigit()]
    return max(vals) if vals else None


def _pick_class(v):
    """highway tag may be a list -> pick most-major class."""
    if isinstance(v, (list, tuple)):
        best = None
        for x in v:
            x = str(x)
            if best is None or CLASS_RANK.get(x, 1) > CLASS_RANK.get(best, 1):
                best = x
        return best
    return str(v) if v is not None else None


def try_osm_lookup(unique_pts: pd.DataFrame) -> pd.DataFrame | None:
    """Snap unique (lat,lon) to nearest OSM drive edge. Returns df or None on failure."""
    try:
        import osmnx as ox
        b = C.BLR_BBOX
        if C.OSM_GRAPH_CACHE.exists():
            print("[road] loading cached OSM graph ...")
            G = ox.load_graphml(C.OSM_GRAPH_CACHE)
        else:
            print("[road] downloading Bengaluru drive network from OSM (one-time)...")
            bbox = (b["min_lon"], b["min_lat"], b["max_lon"], b["max_lat"])  # (L,B,R,T)
            G = ox.graph_from_bbox(bbox=bbox, network_type="drive", simplify=True)
            ox.save_graphml(G, C.OSM_GRAPH_CACHE)
        print(f"[road] graph: {len(G.nodes):,} nodes / {len(G.edges):,} edges")

        edges = ox.graph_to_gdfs(G, nodes=False).reset_index(drop=True)
        edges["road_class_osm"] = edges["highway"].apply(_pick_class)
        edges["lanes_osm"] = edges.get("lanes", pd.Series([None] * len(edges))).apply(_parse_lanes)

        print(f"[road] snapping {len(unique_pts):,} unique coords to nearest edge ...")
        ne = ox.distance.nearest_edges(G, X=unique_pts["longitude"].values,
                                       Y=unique_pts["latitude"].values)
        # nearest_edges returns list of (u,v,k); map back via the same gdf order
        idx = ox.graph_to_gdfs(G, nodes=False).reset_index()
        key2row = {(r.u, r.v, r.key): i for i, r in idx.iterrows()}
        rows = [key2row.get((u, v, k)) for (u, v, k) in ne]
        rc = [edges["road_class_osm"].iloc[i] if i is not None else None for i in rows]
        ln = [edges["lanes_osm"].iloc[i] if i is not None else None for i in rows]
        res = unique_pts.copy()
        res["road_class_osm"] = rc
        res["lanes_osm"] = ln
        ok = res["road_class_osm"].notna().mean()
        print(f"[road] OSM matched {ok*100:.1f}% of coords")
        return res
    except Exception as e:
        print(f"[road] OSM lookup failed ({type(e).__name__}: {e}); using heuristic only")
        return None


def run():
    df = pd.read_parquet(C.CLEAN_PARQUET, columns=["latitude", "longitude", "location"])
    df["latc"] = df["latitude"].round(5)
    df["lonc"] = df["longitude"].round(5)
    uniq = (df.groupby(["latc", "lonc"])
              .agg(latitude=("latitude", "first"),
                   longitude=("longitude", "first"),
                   location=("location", "first"))
              .reset_index())
    print(f"[road] unique coords: {len(uniq):,}")

    # (A) heuristic for everything
    uniq["road_class_heur"] = uniq["location"].apply(heuristic_class)

    # (B) OSM enrichment (best-effort)
    osm = try_osm_lookup(uniq)
    if osm is not None:
        uniq = uniq.merge(osm[["latc", "lonc", "road_class_osm", "lanes_osm"]],
                          on=["latc", "lonc"], how="left")
    else:
        uniq["road_class_osm"] = None
        uniq["lanes_osm"] = None

    # merge sources: OSM class preferred, else heuristic
    uniq["road_class"] = uniq["road_class_osm"].fillna(uniq["road_class_heur"])
    uniq["road_source"] = np.where(uniq["road_class_osm"].notna(), "osm", "heuristic")

    # lane_count: real OSM `lanes` tag if present, else inferred from road class.
    # Track provenance honestly (review must-fix #3): OSM lane tags are sparse in
    # India, so most lane counts are class-inferred, not explicit tags.
    class_lanes = uniq["road_class"].map(C.ROADCLASS_LANES).fillna(C.DEFAULT_LANES)
    uniq["lane_source"] = np.where(uniq["lanes_osm"].notna(), "osm_lanes_tag", "class_inferred")
    uniq["lane_count"] = uniq["lanes_osm"].astype("float").fillna(class_lanes)
    uniq["lane_count"] = uniq["lane_count"].clip(lower=1, upper=6).round().astype(int)

    out = uniq[["latc", "lonc", "road_class", "lane_count", "road_source", "lane_source"]]
    out.to_parquet(C.ROAD_LOOKUP, index=False)
    print(f"[road] class source mix:\n{out['road_source'].value_counts().to_string()}")
    print(f"[road] lane source mix:\n{out['lane_source'].value_counts().to_string()}")
    print(f"[road] explicit OSM lane tags: {(out['lane_source']=='osm_lanes_tag').mean()*100:.1f}% of coords")
    print(f"[road] lane_count dist:\n{out['lane_count'].value_counts().sort_index().to_string()}")
    print(f"[road] wrote {C.ROAD_LOOKUP}  ({len(out):,} coords)")
    return out


if __name__ == "__main__":
    run()
