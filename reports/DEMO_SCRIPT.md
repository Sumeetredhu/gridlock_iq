# GridLock IQ — 90-Second Demo Script & Judge Q&A

*(All numbers are read live from `outputs/summary.json`. Confirm the exact hotspot
count and ₹ figure from the latest run before presenting — they update with the data.)*

---

## The one-line hook

> *"Every other team will show you a map of where parking tickets were written.
> We measure the **traffic those violations actually steal** — and turn it into a
> patrol plan you can fund tomorrow."*

The problem statement's own words: enforcement is **reactive and patrol-based**, there's
**no heatmap of violations vs. congestion impact**, and **no way to prioritize zones**.
GridLock IQ answers exactly those three gaps.

---

## The 3 KPIs to say out loud

1. **Concentration →** *"A small set of hotspot cells — each the size of a football field
   — holds ~43% of the city's entire parking-induced congestion impact. Enforcement is
   chasing the whole city when half the problem is in a handful of spots."*
2. **Action leverage →** *"12 patrol units, optimally placed, relieve ~32% of that impact.
   24 units relieve 50% — then the curve flattens. That's the city's exact funding answer."*
3. **It pays for itself →** *"28.7% of reviewed tickets are rejected. We flag the likely-wasted
   ones, freeing thousands of officer-hours a year — and the optimized patrol delivers a
   multiple-X return on its own payroll."*

---

## The 90-second click path (rehearse to muscle memory)

> Arc: **Problem → Impact → Predict → Act → ROI**, ending on the interactive wow.

| Time | Tab | Do / Say |
|---|---|---|
| 0:00–0:12 | **1 · Command Center** | Open on the 3D hexmap (pre-warmed). Say the hook + the 3 hero KPIs across the top cards. |
| 0:12–0:25 | 1 | Hover the tallest spike (Upparpet / KR-Market core). Tooltip shows CIS, ticket count, station — *"this one corner."* |
| 0:25–0:40 | **2 · Hotspots (Gi\*)** | *"Not just busy — **statistically significant**. Getis-Ord Gi\* with FDR correction. These cells hold 43% of all impact."* Point at the robustness caption: *"and this ranking survives ±25% weight noise — 90% stable."* |
| 0:40–0:52 | **3 · Forecast** | *"We don't just look back — we predict tomorrow's worst cells. Precision@30 = 66%, and it beats the naive 'yesterday=today' baseline."* |
| 0:52–1:15 | **4 · Patrol Optimizer** | **THE MOMENT.** Grab the slider, drag **12 → 24** live. Narrate the captured-impact metric climbing **~32% → 50%**, routes re-drawing, the diminishing-returns curve filling. *"How many marshals should the city fund? Answered, on screen."* |
| 1:15–1:30 | **5 · Enforcement Quality** | *"And we save effort the other way: thousands of wasted officer-hours flagged before review."* Close on the ₹ ROI line. |

**Hold in reserve for Q&A:** Tab 6 (Chronic sites → infrastructure fixes) and Tab 7 (live YOLO CV detection).

---

## The jaw-drop

**Dragging the Patrol slider 12 → 24 (Tab 4).** It's the only interactive element and it
*visibly recomputes*: KMeans re-clusters the marshals, colored routes redraw, the metric
cards update, and the green diminishing-returns marker slides — turning a static dashboard
into a **live decision tool**. The greedy-submodular guarantee (≥63% of optimal, fully
auditable) is the credibility chaser.

---

## Judge Q&A — the 6 you will get

**Q1 · "How do you actually quantify impact?"**
CIS = severity × vehicle-footprint × (1/lane_count) × junction-multiplier × peak-multiplier,
per ticket. A relative capacity-loss index — a bus double-parked in 1 of 2 lanes at a junction
in rush hour scores ~30× a scooter on a footpath. Lane counts are **real**, snapped to
OpenStreetMap road geometry (100% of coords matched). It's a *priority index*, not a claim of
measured minutes — and we show it's robust to the weights.

**Q2 · "Why should we trust the forecast?"**
Temporal holdout — train on the first 80% of dates, test on the future 20%, location priors
computed train-only, so no leakage. The honest operational metric is **Precision@30 = 0.66**:
of the 30 cells we call tomorrow's worst, two-thirds truly are — and that **beats the naive
persistence baseline**. R² is modest (sparse hex-hour counts), but dispatch needs *ranking*,
and ranking is strong.

**Q3 · "What about the data's time bias?"**
Known and handled. `created_datetime` is the enforcement/sync time, not the violation instant —
it peaks 8–11am and dies after 2pm. So we **never** claim it's the violation time; the peak
multiplier is a documented *relative* exposure weight, and our core findings are spatial
(*where*), which the bias doesn't affect.

**Q4 · "Your weights look arbitrary."**
We tested exactly that: a 300-draw Monte-Carlo sweep jittering every weight ±25%. The top-20
hotspots keep a **median 90% overlap** (ranking Spearman 0.998). The conclusions don't hinge on
the numbers — and CIS still reorders ~⅓ of the top cells vs a naive count map, so it's adding
signal, not just re-drawing a count.

**Q5 · "Why greedy, not exact optimization?"**
Max-coverage is NP-hard but **submodular**, so greedy is provably within 63% of optimal *and*
explainable to a commissioner — every stop's marginal impact is auditable. An exact solver buys
<1% for zero interpretability.

**Q6 · "28.7% rejected — would you auto-reject?"**
No. ROC-AUC 0.71 (PR-AUC 0.53 vs 0.30 base) — it nearly doubles precision over chance. We use it
to **prioritize human review**, not replace it: screen the highest-risk captures first. That's
the officer-hours saved, with a human still in the loop.

**Bonus · "Is the rupee figure real?"** It's a transparent **planning estimate** — every
constant (value-of-time, dwell, calibration) is in `economics.py` and tunable. The durable
results are the *concentration* (share of cost in hotspots) and the *enforcement ROI*, which
hold across reasonable assumptions.

---

## Deck order (≤8 slides)

1. **Title + hook** — *"We don't count tickets — we measure the traffic they steal"* + 3 hero KPIs.
2. **Problem** — reactive/patrol-based, no impact map, no prioritization (quote the brief) + data scale (298,450 real tickets).
3. **The idea** — CIS formula visual + bus-vs-scooter example; **real OSM lane fusion**.
4. **Where it hurts** — Gi\* hotspot map, "significant, not just busy", concentration + robustness sweep.
5. **Predict + Act** — forecast Precision@30 (vs baseline) beside the patrol coverage curve.
6. **It pays for itself** — rejection model + the ₹ ROI of optimized patrol.
7. **Beyond enforcement** — chronic-site infrastructure recommendations + live CV auto-detection loop.
8. **Impact + ask** — recap KPIs + "fund N marshals."

---

## Demo safety

- **Pre-warm the app** before presenting (first render compiles; the Patrol tab runs KMeans on
  each slider move — click it once beforehand so the live drag is instant).
- Keep the static figures in `assets/` and a short screen-recording as a **fallback**.
- Confirm `ultralytics` is installed so the CV tab is live (it degrades gracefully if not, but
  don't discover that on stage).
