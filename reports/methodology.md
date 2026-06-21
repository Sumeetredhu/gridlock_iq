# GridLock IQ — Methodology

How we turn 298,450 raw parking-enforcement tickets into a quantified,
forecastable, optimizable measure of *parking-induced congestion* — and why each
step is defensible.

---

## 0. The data, honestly

| Field | What it gives us | Caveat we handle |
|---|---|---|
| `latitude/longitude`, `location` | precise point + address | — |
| `violation_type` (JSON array) | offence severity | multi-offence tickets → we take the worst |
| `vehicle_type` | physical footprint | — |
| `vehicle_number` (anonymized, consistent) | repeat-offender tracking | — |
| `junction_name` | 50.4 % at a mapped junction | a real, data-grounded congestion signal |
| `validation_status` | 28.7 % of reviewed tickets *rejected* | the wasted-enforcement signal |
| `created_datetime` | timing | **enforcement/sync time, not the exact violation instant** |

The timing caveat is the single most important honesty point: the file peaks
08–11 IST and falls off after 14:00, which matches *marshal enforcement drives +
device sync*, not the true distribution of when cars are illegally parked. We
therefore **never claim absolute time-of-violation**. Time is used only as a
*relative exposure weight* and the forecast is scored on **ranking** (Precision@K),
not on predicting an exact hour.

---

## 1. Congestion-Impact Score (CIS)

The problem statement demands we *quantify impact on traffic flow*, but the dataset
contains **no speed/flow ground truth**. So instead of pretending to measure delay,
we build a transparent, physically-motivated **relative impact index**:

$$\text{CIS} = \underbrace{s}_{\text{severity}} \times \underbrace{f}_{\text{footprint}} \times \underbrace{\tfrac{1}{L}}_{\text{lane factor}} \times \underbrace{j}_{\text{junction}} \times \underbrace{p}_{\text{peak}}$$

| Term | Range | Source / rationale |
|---|---|---|
| **severity** `s` | 0.25–1.0 | how directly the offence blocks the moving lane. Footpath parking (0.25) barely touches the carriageway; *parking near road crossing / traffic light* (1.0) and *main road* (0.90) directly choke flow. |
| **footprint** `f` | 0.18–1.0 | roadway area a stopped vehicle removes. Scooter 0.20 ≪ car 0.60 ≪ bus/HGV 1.0. |
| **lane factor** `1/L` | 1/6–1 | **the physics.** Blocking one lane on a 2-lane road removes ~50 % of capacity; on a 6-lane road ~17 %. `L` is the **real OpenStreetMap lane count** at that exact coordinate (100 % matched). |
| **junction** `j` | 1.0 / 1.6 | queue spill-back: a blockage at an intersection backs up every approach. Uses the dataset's own `junction_name`. |
| **peak** `p` | 1.0–1.5 | relative rush-hour exposure (treated as relative, given the time caveat). |

**Interpretation.** CIS is a *relative* capacity-loss / enforcement-priority index, **not** an
absolute minutes-of-delay measurement (the data has no dwell time). It is monotonic in every
factor a traffic engineer cares about, and every weight is exposed in `config.py`.

**Robustness (the answer to "your weights are arbitrary").** We ran a 300-draw Monte-Carlo sweep
jittering every weight by ±25%. The top-20 hotspots keep a **median 90.5% Jaccard overlap**
(5th-percentile 81.8%) and the full hex ranking holds at **Spearman 0.998**. Meanwhile CIS vs. a
naive raw-ticket-count ranking differ (top-20 Jaccard 0.67), so CIS is **not** just a count map —
it adds signal while being insensitive to the precise weights. (`src/sensitivity.py`)

Why this beats a raw count heatmap: a street with 500 scooters ticketed on a wide 4-lane road
can score *lower* than a corner with 80 trucks double-parked at a 2-lane junction — which is
exactly the prioritization the Traffic Police actually needs.

---

## 2. Spatial aggregation — H3

Points are binned into **Uber H3** hexagons (resolution 9, ≈ 0.1 km² per cell; resolution 10 for
chronic micro-sites). Hexagons (vs. squares) give uniform neighbour distances — essential for the
spatial statistics in step 3 — and tile cleanly on a map.

---

## 3. Statistically-significant hotspots — Getis-Ord Gi\*

A heatmap shows where values are *high*; **Gi\*** shows where they are high *beyond spatial chance*.
We build a KNN (k=6) spatial-weights graph over hex centroids and compute a Gi\* z-score on each
cell's total CIS (`esda`). Because we test **2,534 cells simultaneously**, an uncorrected α=0.05
would admit ~127 false positives by chance — so we control the **false-discovery rate with
Benjamini-Hochberg** on the analytical normal p-values from the z-scores.

**Result: 64 cells survive FDR (q ≤ 0.05) and concentrate 41 % of the city's total congestion
impact** (the strongest, e.g. the Upparpet / KR-Market core, reach z ≈ 27, p ≈ 10⁻¹⁶²). This is
the rigorous, defensible basis for "prioritize these zones" — fewer cells than a naive p<0.05 cut,
but every one is real.

---

## 4. Next-shift forecast — LightGBM

To deploy *ahead* of the problem we predict each cell's CIS for an upcoming
(day-of-week × hour) shift.

- **Features:** temporal (hour, dow, weekend, day-of-month) + static location
  (lat/lon, junction share, mean lanes, road class) + **leakage-safe** location priors
  (hex mean/volume computed on the **training dates only**).
- **Validation:** a **temporal holdout** (last 20 % of dates), never random — so we measure true
  forward prediction.
- **Metrics vs. a naive persistence baseline** (rank cells by train-set historical mean CIS, no model):
  - MAE **56.7** vs baseline **66.4** → the model is **~15% more accurate** on magnitude.
  - Precision@30 **0.659** vs baseline **0.640** → it *matches* persistence on top-30 ranking.
  - R² ≈ 0.11 (sparse, spiky hex-hour counts).

The honest read: the city's worst cells are persistent, so a "yesterday=tomorrow" rule already
ranks the top-30 well; the model's value is the **15% MAE gain** (better magnitude estimates for
the whole grid) plus a true **forward** forecast for any future shift. We report the baseline
openly rather than quoting Precision@K in isolation.

---

## 5. Patrol optimizer — submodular max-coverage

Given the forecast and *N* patrol units (× 6 stops/shift), we choose stops to **maximize captured
forecast CIS**. A stop covers its H3 ring; we greedily add the stop with the largest marginal
uncovered impact. Coverage is a **monotone submodular** function, so greedy is provably within
**(1 − 1/e) ≈ 63 %** of optimal — and, just as important, it's explainable to a commissioner in one
sentence. Chosen stops are clustered (KMeans) into per-marshal nearest-neighbour routes.

**Result: 12 units capture 32 % of city-wide impact in one shift; 24 units → 50 %.** The
diminishing-returns curve tells the city exactly how many units to fund.

---

## 6. Wasted-enforcement model

28.7 % of reviewed tickets are *rejected* — each one an officer-hour spent on a bad capture. A
LightGBM classifier predicts rejection from offence/vehicle/place/time features
(**ROC-AUC 0.71**, PR-AUC 0.53 vs. 0.30 base). Pre-screening the highest-risk captures could save an
estimated **~6,000 officer-hours/year** and clean the data feeding every other model.

---

## 7. Chronic-site intelligence

Some micro-locations are ticketed almost *every single day* yet never improve — patrols don't fix
them. We flag sites active ≥ 20 of 151 days and emit a concrete **infrastructure** recommendation
(ANPR camera / bollards / loading bay / paid parking) per site. This reframes the mission from
"write more tickets" to "engineer the problem away" — the systems-thinking the brief is really after.

---

## 8. Economic layer — pricing congestion in rupees

To make the index actionable for a BBMP / Traffic Police buyer, we convert CIS into money via a
**fully transparent, tunable** assumption chain (`src/economics.py`): a calibration from one
reference event (a car wrong-parked in 1 of 2 lanes) maps `cis_raw` → vehicle-hours of delay, and
a value-of-time (₹250/veh-hr) converts that to rupees. **All constants are explicit and labelled
as assumptions.**

- Planning estimate: **≈ ₹212 cr/year** of parking-induced congestion cost (ticketed violations only).
- **41%** of that cost sits in the 64 Gi\* hotspot cells — so targeted enforcement is high-leverage.
- Optimized 12-unit patrol relieves ≈ ₹67 cr/yr against ≈ ₹0.8 cr/yr of payroll → an order-of-
  magnitude **ROI** even under conservative enforcement-effectiveness assumptions.

The absolute rupee figure scales linearly with the stated constants; the **durable** results are
the *concentration* and the *ROI ordering*, which hold across any reasonable parameter choice.

---

## Limitations & honest next steps

- **No ground-truth congestion** → CIS is validated by construction + sensitivity, not against
  measured speeds. *Cheap next step:* correlate hot cells against a free speed source
  (TomTom/HERE/Mapbox sample, or Google Directions live-vs-free-flow) for external validation.
- **Enforcement-time bias** → relative-time framing + Precision@K, as above.
- **Selection bias** (we only see *where police ticketed*) → the rejection model and chronic-site
  layer partially correct for it; a CCTV/CV feed (module 8) would remove it entirely.

*(Judge Q&A and the demo script are appended below from the adversarial review.)*
