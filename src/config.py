"""
GridLock IQ - central configuration & shared contract.

Every module imports from here so column names, file paths, and the
Congestion-Impact-Score (CIS) weights stay consistent across the pipeline.
"""
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]            # gridlock_iq/
PROJECT_ROOT = ROOT.parent                            # Desktop/Flipkart/
RAW_CSV = PROJECT_ROOT / "jan to may police violation_anonymized791b166.csv"

DATA = ROOT / "data"
PROC = DATA / "processed"
CACHE = DATA / "cache"
OUTPUTS = ROOT / "outputs"
REPORTS = ROOT / "reports"
ASSETS = ROOT / "assets"
for _p in (DATA, PROC, CACHE, OUTPUTS, REPORTS, ASSETS):
    _p.mkdir(parents=True, exist_ok=True)

# Pipeline artifacts (the shared contract between modules)
CLEAN_PARQUET     = PROC / "violations_clean.parquet"   # one row per ticket, cleaned
SCORED_PARQUET    = PROC / "violations_scored.parquet"  # + CIS columns
ROAD_LOOKUP       = PROC / "road_lookup.parquet"        # unique coord -> road attrs
HEX_PARQUET       = PROC / "hex_aggregate.parquet"      # H3 cell aggregates
HEX_TIME_PARQUET  = PROC / "hex_time_aggregate.parquet" # H3 x time-bucket
HOTSPOTS_PARQUET  = PROC / "hotspots_gistar.parquet"    # Gi* significant hotspots
FORECAST_PARQUET  = PROC / "forecast_next_shift.parquet"
PATROL_PARQUET    = PROC / "patrol_plan.parquet"
REJECTION_PARQUET = PROC / "rejection_scored.parquet"
CHRONIC_PARQUET   = PROC / "chronic_sites.parquet"
OSM_GRAPH_CACHE   = CACHE / "bengaluru_drive.graphml"
SUMMARY_JSON      = OUTPUTS / "summary.json"            # headline KPIs for the deck

# ----------------------------------------------------------------------------
# Geography (Bengaluru) - bounds derived from the data
# ----------------------------------------------------------------------------
BLR_BBOX = dict(min_lat=12.80, max_lat=13.30, min_lon=77.44, max_lon=77.78)
BLR_CENTER = (12.9716, 77.5946)
IST = "Asia/Kolkata"

# H3 resolutions: res 9 ~174m edge (hotspot grid), res 10 ~65m (fine display)
H3_RES = 9
H3_RES_FINE = 10

# ----------------------------------------------------------------------------
# Congestion-Impact-Score (CIS) weights
#   CIS = severity x footprint x lane_factor x junction_mult x peak_mult
#   Interpretable as a relative "lane-capacity-minutes lost" proxy.
# ----------------------------------------------------------------------------

# Violation severity = how much a given offence type blocks moving traffic.
# Footpath parking is bad for pedestrians but barely touches the carriageway;
# main-road / near-crossing / double parking directly choke flow.
SEVERITY = {
    "PARKING NEAR ROAD CROSSING": 1.00,
    "PARKING NEAR TRAFFIC LIGHT OR ZEBRA CROSS": 1.00,
    "DOUBLE PARKING": 0.95,
    "PARKING IN A MAIN ROAD": 0.90,
    "PARKING OPPOSITE TO ANOTHER PARKED VEHICLE": 0.85,
    "PARKING NEAR BUSTOP/SCHOOL/HOSPITAL ETC": 0.80,
    "PARKING OTHER THAN BUS STOP": 0.70,
    "WRONG PARKING": 0.65,
    "NO PARKING": 0.55,
    "PARKING ON FOOTPATH": 0.25,
}
SEVERITY_DEFAULT = 0.40  # non-parking offences (number plate, fare, etc.)

# Vehicle footprint = roadway area a stopped vehicle removes from circulation.
FOOTPRINT = {
    "BUS (BMTC/KSRTC)": 1.00, "PRIVATE BUS": 1.00, "HGV": 1.00, "LORRY/GOODS VEHICLE": 0.95,
    "LGV": 0.80, "TEMPO": 0.75, "VAN": 0.70, "MAXI-CAB": 0.70, "GOODS AUTO": 0.65,
    "CAR": 0.60, "JEEP": 0.60, "PASSENGER AUTO": 0.45,
    "MOTOR CYCLE": 0.20, "SCOOTER": 0.20, "MOPED": 0.18,
}
FOOTPRINT_DEFAULT = 0.50

# Lane factor: blocking 1 of N lanes removes ~1/N of capacity. Fewer lanes => worse.
# Mapped from OSM highway class -> typical effective lanes (per direction-ish).
ROADCLASS_LANES = {
    "motorway": 4, "trunk": 3, "primary": 3, "secondary": 2,
    "tertiary": 2, "residential": 1, "unclassified": 1, "living_street": 1,
    "service": 1,
}
DEFAULT_LANES = 2  # used when OSM lane/class unknown

# Junction proximity multiplier: parking at/near an intersection causes
# disproportionate queue spill-back. We have junction_name in the data.
JUNCTION_MULT = 1.6
NONJUNCTION_MULT = 1.0

# Peak-hour multiplier (by IST hour). NOTE: created_datetime reflects the
# enforcement/sync time, not the exact violation instant, so this is treated
# as a *relative* exposure weight, documented in the methodology.
def peak_multiplier(hour_ist: int) -> float:
    if hour_ist in (8, 9, 10, 11, 18, 19, 20):   # morning + evening rush
        return 1.5
    if hour_ist in (7, 12, 13, 17, 21):
        return 1.2
    return 1.0

# Canonical parking-violation labels used for filtering "congestion-relevant"
PARKING_VIOLATIONS = set(SEVERITY.keys())

RANDOM_STATE = 42
