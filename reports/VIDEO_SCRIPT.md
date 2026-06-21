# GridLock IQ — 5-Minute Demo Video Script

**Format:** screen recording + voiceover. `[SCREEN]` = what to show/click. `[SAY]` = read aloud.
**Target:** ~5:00 at a calm ~165 words/min. Trim the *italic* lines if you run long.

---

### Before you hit record (60-sec setup)
1. Start the server so everything (incl. live CV) works: `python server.py` → open `http://localhost:8531/`.
2. Open these in tabs, in order: **police dashboard** (`/`), **analyst dashboard** (`/analyst.html`), the **detailed deck** (`GridLock_IQ_Detailed.pptx`).
3. On the analyst CV tab, hit it once so the YOLO weights are downloaded (so the live demo is instant). Have **one street-parking photo** ready on your desktop.
4. Pre-warm the analyst Patrol tab once (the slider runs clustering on first move).

---

## 0:00 – 0:25 · Hook + the problem
`[SCREEN]` Police dashboard hero ("SEE IT. CLEAR IT.") with the KPI cards.
`[SAY]`
> "This is **GridLock IQ** — an AI system that finds where illegal parking is actually choking traffic in Bengaluru, and tells the police exactly where to act. The problem today: parking enforcement is reactive and patrol-based. Cities write thousands of tickets, but they have **no map of which violations actually hurt traffic flow**, and no way to prioritise. We built that missing layer — on **298,450 real enforcement records**."

## 0:25 – 0:55 · The data
`[SCREEN]` Detailed deck → "The Data" slide (or analyst Overview KPIs).
`[SAY]`
> "The dataset is every Bengaluru parking ticket over five months — location, vehicle type, the offence, and the police station. Half of all tickets happen right at a junction. One honest detail we handle carefully: the timestamp is when the ticket was *synced*, not the exact second of the violation — so we use time only as a relative weight and never overclaim it. That kind of honesty matters, and it runs through the whole project."

## 0:55 – 1:45 · The big idea — the Congestion-Impact Score
`[SCREEN]` Deck → "The Big Idea" CIS formula slide.
`[SAY]`
> "Here's the core idea. Most teams would build a heatmap of *where tickets happen*. But a busy street isn't the same as a blocked one. So instead, we score every single ticket with a **Congestion-Impact Score** — how much moving-traffic capacity that violation removes.
> It's five factors multiplied: how badly the offence blocks the road, the **size of the vehicle**, and critically **one-over-the-number-of-lanes** — because blocking one of two lanes removes half the capacity, but one of six lanes barely matters. Those lane counts are **real**, pulled from OpenStreetMap — we snapped all 183,000 locations onto Bengaluru's actual road network. Then a junction and a rush-hour multiplier.
> The result: a bus double-parked in one of two lanes at a junction in rush hour scores about **thirty times** a scooter on a footpath. That's the difference between counting tickets and *measuring congestion*."

## 1:45 – 2:25 · Finding the real hotspots (Gi* + robustness)
`[SCREEN]` Analyst dashboard → **Hotspots** tab (the red Gi* map + table). Scroll to the robustness line.
`[SAY]`
> "Now, where does it concentrate? We don't just eyeball the map — we run a statistical test called **Getis-Ord Gi-star**, with a false-discovery-rate correction across 2,500 cells, so only genuinely significant hotspots survive. The result is striking: just **64 cells** — each about the size of a football field — hold **41% of the entire city's parking-induced congestion**.
> And to prove our weights aren't arbitrary, we shook every weight by twenty-five percent, three hundred times. The top hotspots stayed **90% the same**. So the conclusion doesn't depend on numbers we picked by hand."

## 2:25 – 3:00 · Forecasting the next shift
`[SCREEN]` Analyst → **Forecast** tab (model vs baseline KPIs + map).
`[SAY]`
> "Knowing today's hotspots is good. Predicting tomorrow's is better. A machine-learning model forecasts each cell's congestion for the next shift. We tested it *honestly* — trained on the earlier dates, tested on the later ones, no peeking — and benchmarked it against a naive 'yesterday equals tomorrow' rule. It cuts the error by **15%**, and correctly flags two-thirds of tomorrow's worst spots. So patrols can be placed **before** the jam forms, not after."

## 3:00 – 3:40 · The patrol optimiser — the payoff
`[SCREEN]` Analyst → **Patrol** tab. **Drag the slider from 12 to 24** — let the map markers and the big % redraw live.
`[SAY]`
> "This is where it becomes a decision. Given how many patrol units you have, the optimiser places them to clear the **most** congestion possible — and it's provably near-optimal. Watch — with **twelve units**, optimally placed, we clear about a third of the city's entire parking congestion. Push it to **twenty-four**, and we hit **fifty percent** — then the curve flattens. That flattening point *is* the city's funding answer: exactly how many marshals are worth deploying."

## 3:40 – 4:15 · Beyond enforcement — save money, fix root causes, price it
`[SCREEN]` Analyst → **Quality** tab, then **Chronic** tab.
`[SAY]`
> "It also saves effort. Nearly a third of reviewed tickets get *rejected* — wasted officer time. A model flags the likely-wasted ones first, freeing roughly **fourteen thousand officer-hours a year**.
> `[SCREEN: Chronic tab]` And some spots get ticketed almost every single day yet never improve — patrolling them is pointless. We flag **919** of these and recommend the real fix: cameras, bollards, or a loading bay — not more fines.
> Finally, we put a rupee value on it: a transparent estimate of about **₹212 crore a year**, with **forty percent sitting inside those hotspots** — which is why targeted enforcement pays for itself many times over."

## 4:15 – 4:45 · Live computer vision
`[SCREEN]` Analyst → **CV** tab. Drag your street photo in. Wait for the boxed result.
`[SAY]`
> "And here's the future, running live right now. This is a real **YOLOv8** detector. I'll drop in a street photo… and it instantly finds the vehicles, and flags the ones parked illegally inside the no-parking zone in red. On a CCTV or dashcam feed, every detection would auto-feed the exact same scoring pipeline — zero human delay. *It works on video too, frame by frame.*"

## 4:45 – 5:00 · Close
`[SCREEN]` Quick pan: police dashboard → analyst dashboard → deck title.
`[SAY]`
> "So that's GridLock IQ: it **measures** congestion, **predicts** it, **acts** on it with an optimised patrol plan, **designs out** the chronic spots, and **prices** the whole problem — wrapped in two dashboards, a simple one for patrols and a deep one for planners. We don't count tickets. We measure the traffic they steal. Thank you."

---

### Delivery tips
- Let the **slider drag (3:00)** and the **CV result (4:15)** breathe — those are the two "wow" moments; pause and let them land.
- Say the **bold numbers** slowly and clearly; skim the rest.
- If you're over 5:00, cut the italic lines and shorten the data section (0:25).
- Record screen at 1080p; zoom the browser to ~110% so text reads on small screens.
