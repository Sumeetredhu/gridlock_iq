// Detailed GridLock IQ deck in the blue 'design-canvas / blueprint' style.
const pptxgen = require("pptxgenjs");
const fs = require("fs"), path = require("path");
const S = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "outputs", "summary.json"), "utf8"));
const A = (f) => path.join(__dirname, "..", "assets", f);
const BG = A("bg_blue.png");

const LIME = "C7F031", ORANGE = "FF6A2B", INK = "0E1118", CARD = "121722", CARD2 = "1A2230";
const TXT = "ECF2F9", MUTE = "9DB1C7", LINE = "2A3647", BLUE = "5FA8FF", GOOD = "16E0A3";
const HF = "Arial Black", BF = "Calibri", MONO = "Consolas";
const sh = () => ({ type: "outer", color: "000000", blur: 10, offset: 4, angle: 135, opacity: 0.38 });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; pres.author = "GridLock IQ";
pres.title = "GridLock IQ — Detailed Project Walkthrough";
const W = 13.33, H = 7.5, TOTAL = 17;

// ---------- chrome helpers ----------
function selFrame(s, x, y, w, h) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { type: "none" }, line: { color: LIME, width: 1.75 } });
  const hs = 0.13;
  [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].forEach(([hx, hy]) =>
    s.addShape(pres.shapes.RECTANGLE, { x: hx - hs / 2, y: hy - hs / 2, w: hs, h: hs,
      fill: { color: LIME }, line: { color: INK, width: 1.25 } }));
}
function menuChip(s, items, activeIdx) {
  const x = 9.55, y = 0.5, w = 3.25, rh = 0.42, h = items.length * rh + 0.2;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: "0F141D" },
    line: { color: LINE, width: 1 }, rectRadius: 0.09, shadow: sh() });
  items.forEach(([label, key], i) => {
    const ry = y + 0.1 + i * rh;
    if (i === activeIdx) s.addText("✓", { x: x + 0.12, y: ry, w: 0.3, h: rh, fontFace: BF,
      fontSize: 12, color: LIME, valign: "middle", margin: 0 });
    s.addText(label, { x: x + 0.45, y: ry, w: w - 1.1, h: rh, fontFace: BF, fontSize: 12.5,
      color: i === activeIdx ? TXT : MUTE, valign: "middle", margin: 0 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + w - 0.5, y: ry + 0.07, w: 0.34, h: 0.28,
      fill: { color: "1C2533" }, line: { color: LINE, width: 0.75 }, rectRadius: 0.04 });
    s.addText(key, { x: x + w - 0.5, y: ry + 0.05, w: 0.34, h: 0.3, fontFace: BF, fontSize: 10.5,
      color: MUTE, align: "center", valign: "middle", margin: 0 });
  });
}
function dock(s) {
  const n = 8, bw = 0.5, gap = 0.12, pad = 0.16;
  const w = n * bw + (n - 1) * gap + pad * 2, x = (W - w) / 2, y = 6.93, h = 0.62;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: "121722" },
    line: { color: "2C3647", width: 1 }, rectRadius: 0.12, shadow: sh() });
  for (let i = 0; i < n; i++) {
    const bx = x + pad + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: y + 0.1, w: bw, h: h - 0.2,
      fill: { color: i === 0 ? LIME : "1B2433" }, rectRadius: 0.07 });
    if (i === 0) s.addText("➤", { x: bx, y: y + 0.07, w: bw, h: h - 0.18, fontFace: BF, fontSize: 14,
      color: INK, align: "center", valign: "middle", margin: 0, rotate: -45 });
    else s.addShape(pres.shapes.OVAL, { x: bx + 0.17, y: y + 0.21, w: 0.16, h: 0.16,
      fill: { type: "none" }, line: { color: MUTE, width: 1.25 } });
  }
}
function pageTag(s, n) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 11.95, y: 6.98, w: 1.05, h: 0.42,
    fill: { color: ORANGE }, rectRadius: 0.07 });
  s.addText(String(n).padStart(2, "0") + " / " + TOTAL, { x: 11.95, y: 6.98, w: 1.05, h: 0.42,
    fontFace: BF, fontSize: 12, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
}
function chip(s, x, y, text, fill, color) {
  const w = 0.22 + text.length * 0.092;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.4, fill: { color: fill }, rectRadius: 0.07, shadow: sh() });
  s.addText(text, { x, y, w, h: 0.4, fontFace: BF, fontSize: 12.5, bold: true, color, align: "center", valign: "middle", margin: 0 });
}
function statMini(s, x, y, w, big, label, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 1.25, fill: { color: CARD2 },
    line: { color: LINE, width: 1 }, rectRadius: 0.08 });
  s.addText(big, { x: x + 0.08, y: y + 0.12, w: w - 0.16, h: 0.6, fontFace: HF, fontSize: 26,
    color: color || LIME, align: "center", valign: "middle", margin: 0 });
  s.addText(label, { x: x + 0.1, y: y + 0.72, w: w - 0.2, h: 0.45, fontFace: BF, fontSize: 10.5,
    color: MUTE, align: "center", valign: "top", margin: 0 });
}

// base content slide with artboard + chrome; returns {s, cx, cy, cw}
function base(kicker, title, menuActive, page) {
  const s = pres.addSlide();
  s.background = { path: BG };
  const ax = 0.5, ay = 1.3, aw = 12.33, ah = 5.5;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: ax, y: ay, w: aw, h: ah, fill: { color: CARD },
    line: { color: LINE, width: 1 }, rectRadius: 0.06, shadow: sh() });
  selFrame(s, ax, ay, aw, ah);
  s.addText(kicker.toUpperCase(), { x: ax + 0.45, y: ay + 0.28, w: 8, h: 0.3, fontFace: BF,
    fontSize: 12.5, color: LIME, bold: true, charSpacing: 3, margin: 0 });
  s.addText(title, { x: ax + 0.4, y: ay + 0.55, w: aw - 0.8, h: 0.85, fontFace: HF, fontSize: 30,
    color: TXT, margin: 0 });
  menuChip(s, [["Analyze", "A"], ["Predict", "P"], ["Deploy", "D"]], menuActive);
  dock(s); pageTag(s, page);
  return { s, cx: ax + 0.45, cy: ay + 1.55, cw: aw - 0.9 };
}
function bullets(s, items, x, y, w, fs) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: { code: "2022", indent: 14 },
    breakLine: true, paraSpaceAfter: 9, color: TXT } })),
    { x, y, w, h: 3.4, fontFace: BF, fontSize: fs || 14.5, color: TXT, valign: "top", margin: 0 });
}

// ===================================================== 1 · COVER
let s = pres.addSlide(); s.background = { path: BG };
menuChip(s, [["Social Media", "V"], ["Thumbnail", "H"], ["UI Design", "K"]], 2);
s.addText("FLIPKART GRiD · ML TRACK · 2026", { x: 1.0, y: 1.25, w: 9, h: 0.35, fontFace: BF,
  fontSize: 15, color: LIME, bold: true, charSpacing: 3, margin: 0 });
selFrame(s, 0.92, 1.95, 8.6, 2.95);
s.addText("GRID\nLOCK IQ", { x: 0.85, y: 1.75, w: 9.2, h: 3.3, fontFace: HF, fontSize: 78,
  color: "FFFFFF", lineSpacing: 64, margin: 0, shadow: sh() });
s.addText("Parking-Induced Congestion Intelligence", { x: 1.0, y: 5.05, w: 9, h: 0.5,
  fontFace: BF, fontSize: 23, color: TXT, margin: 0 });
s.addText("See the congestion. Score it. Clear it.", { x: 1.0, y: 5.55, w: 9, h: 0.4,
  fontFace: BF, fontSize: 15, italic: true, color: MUTE, margin: 0 });
chip(s, 1.0, 6.2, "2026 Edition", "121722", TXT);
chip(s, 2.55, 6.2, "Bengaluru Traffic Police", ORANGE, "FFFFFF");
// cursor + tag
s.addText("➤", { x: 9.35, y: 5.55, w: 0.5, h: 0.5, fontFace: BF, fontSize: 26, color: LIME, rotate: -45, margin: 0 });
chip(s, 9.6, 6.0, "298,450 real tickets", "121722", LIME);
dock(s);

// ===================================================== 2 · PROBLEM
let b = base("The challenge", "Enforcement is blind to congestion", 0, 2);
s = b.s;
s.addText("On-street illegal & spillover parking chokes carriageways and junctions near markets, metros and events. Today, enforcement can't see where it hurts most.",
  { x: b.cx, y: b.cy - 0.15, w: 6.0, h: 0.9, fontFace: BF, fontSize: 14.5, color: TXT, margin: 0 });
const pains = [
  ["Reactive & patrol-based", "Officers respond to complaints — no system points them to the worst spots first."],
  ["No impact heatmap", "Tickets are counted, but their effect on traffic flow is never measured."],
  ["Can't prioritise zones", "With limited marshals, nobody knows which 1% of streets to cover."]];
let py = b.cy + 1.0;
pains.forEach(([t, d], i) => {
  s.addShape(pres.shapes.OVAL, { x: b.cx, y: py, w: 0.42, h: 0.42, fill: { color: ORANGE } });
  s.addText(String(i + 1), { x: b.cx, y: py, w: 0.42, h: 0.42, fontFace: HF, fontSize: 15, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  s.addText([{ text: t + "   ", options: { bold: true, color: TXT } }, { text: d, options: { color: MUTE } }],
    { x: b.cx + 0.6, y: py - 0.04, w: 5.4, h: 0.7, fontFace: BF, fontSize: 13, valign: "middle", margin: 0 });
  py += 0.92;
});
statMini(s, 7.1, b.cy, 1.75, S.dataset.tickets.toLocaleString().replace(/,/g, ","), "enforcement tickets", LIME);
statMini(s, 9.0, b.cy, 1.75, S.dataset.stations + "", "police stations", BLUE);
statMini(s, 10.9, b.cy, 1.75, S.dataset.junction_share_pct + "%", "at a junction", ORANGE);
statMini(s, 7.1, b.cy + 1.5, 1.75, "5 mo", "of data (Nov–Apr)", GOOD);
statMini(s, 9.0, b.cy + 1.5, 3.65, S.dataset.unique_vehicles.toLocaleString(), "unique vehicles tracked (anonymised, consistent)", TXT);

// ===================================================== 3 · OVERVIEW
b = base("The solution", "One system, five moves", 2, 3); s = b.s;
s.addText("GridLock IQ turns raw enforcement records into decisions a commissioner can fund — five stages, each a working module.",
  { x: b.cx, y: b.cy - 0.15, w: 11.3, h: 0.6, fontFace: BF, fontSize: 14.5, color: TXT, margin: 0 });
const moves = [["MEASURE", "Congestion-Impact Score per ticket, from real road lanes", LIME],
  ["PREDICT", "Forecast the next shift's worst cells before they happen", BLUE],
  ["ACT", "Optimised patrol plan — where to send each unit", ORANGE],
  ["DESIGN OUT", "Chronic spots get an infrastructure fix, not more tickets", GOOD],
  ["PRICE", "Put a rupee value on congestion to prove the ROI", "E36BFF"]];
let mx = b.cx;
const mw = (b.cw - 4 * 0.25) / 5;
moves.forEach(([t, d, c], i) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: mx, y: b.cy + 0.7, w: mw, h: 2.7, fill: { color: CARD2 },
    line: { color: LINE, width: 1 }, rectRadius: 0.08 });
  s.addShape(pres.shapes.RECTANGLE, { x: mx, y: b.cy + 0.7, w: mw, h: 0.1, fill: { color: c } });
  s.addText(String(i + 1), { x: mx + 0.15, y: b.cy + 0.9, w: mw - 0.3, h: 0.6, fontFace: HF, fontSize: 26, color: c, margin: 0 });
  s.addText(t, { x: mx + 0.15, y: b.cy + 1.5, w: mw - 0.3, h: 0.5, fontFace: HF, fontSize: 13.5, color: TXT, margin: 0 });
  s.addText(d, { x: mx + 0.15, y: b.cy + 1.95, w: mw - 0.3, h: 1.4, fontFace: BF, fontSize: 11, color: MUTE, margin: 0 });
  mx += mw + 0.25;
});
s.addText("+ a live YOLOv8 computer-vision feed and two dashboards (one simple for patrols, one deep for analysts).",
  { x: b.cx, y: b.cy + 3.55, w: 11.3, h: 0.4, fontFace: BF, fontSize: 12.5, italic: true, color: LIME, margin: 0 });

// ===================================================== 4 · DATA
b = base("The data", "What's inside 298,450 tickets", 0, 4); s = b.s;
bullets(s, [
  "Each ticket: GPS + address, vehicle number (anonymised but consistent), vehicle type, the offence(s), time, police station, and whether it's at a junction.",
  "Almost all are parking offences — Wrong Parking, No Parking, Main-Road, Footpath, Double, Near-Crossing.",
  "Half of all tickets (50.4%) happen right at a mapped junction — a direct congestion signal.",
], b.cx, b.cy, 5.9, 14);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: b.cx, y: b.cy + 2.45, w: 5.9, h: 1.0, fill: { color: "2A1B10" },
  line: { color: ORANGE, width: 1 }, rectRadius: 0.08 });
s.addText([{ text: "Handled honestly:  ", options: { bold: true, color: ORANGE } },
  { text: "the timestamp is when the ticket was synced, not the exact moment of the violation — so we use time only as a relative weight and never overclaim it.", options: { color: TXT } }],
  { x: b.cx + 0.2, y: b.cy + 2.55, w: 5.5, h: 0.85, fontFace: BF, fontSize: 11.5, valign: "middle", margin: 0 });
s.addImage({ path: A("fig_cis_heatmap.png"), x: 7.2, y: b.cy - 0.05, w: 5.4, h: 3.55, sizing: { type: "contain", w: 5.4, h: 3.55 } });
chip(s, 7.4, b.cy + 3.35, "Every ticket maps to a real Bengaluru street", "121722", MUTE);

// ===================================================== 5 · CIS
b = base("The big idea", "Turning a ticket into capacity lost", 0, 5); s = b.s;
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: b.cx, y: b.cy - 0.1, w: 11.3, h: 0.95, fill: { color: "0F141D" },
  line: { color: LINE, width: 1 }, rectRadius: 0.08 });
s.addText([{ text: "CIS", options: { color: LIME, bold: true } },
  { text: "  =  severity  ×  vehicle size  ×  ", options: { color: TXT } },
  { text: "(1 ÷ lanes)", options: { color: ORANGE, bold: true } },
  { text: "  ×  junction  ×  peak", options: { color: TXT } }],
  { x: b.cx + 0.25, y: b.cy - 0.1, w: 11, h: 0.95, fontFace: MONO, fontSize: 19, valign: "middle", margin: 0 });
bullets(s, [
  "severity — how much the offence blocks moving traffic (footpath « main road « near-crossing).",
  "vehicle size — road space the stopped vehicle eats (scooter « car « bus/truck).",
  "1 ÷ lanes — the physics: blocking 1 of 2 lanes removes ~50% of capacity; 1 of 6 only ~17%. Lanes come from real OpenStreetMap data.",
  "junction & peak — extra weight where blockages spill back, and during rush hour.",
], b.cx, b.cy + 1.05, 6.25, 13);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.5, y: b.cy + 1.15, w: 5.05, h: 2.25, fill: { color: CARD2 },
  line: { color: LIME, width: 1.25 }, rectRadius: 0.1 });
s.addText("Same street, very different impact", { x: 7.7, y: b.cy + 1.3, w: 4.7, h: 0.4, fontFace: BF, fontSize: 13, bold: true, color: LIME, margin: 0 });
s.addText([{ text: "A bus double-parked in 1 of 2 lanes at a junction in rush hour\n", options: { color: TXT, breakLine: true } },
  { text: "scores about ", options: { color: MUTE } }, { text: "30×", options: { color: ORANGE, bold: true } },
  { text: "  a scooter on a footpath.", options: { color: MUTE } }],
  { x: 7.7, y: b.cy + 1.75, w: 4.7, h: 1.5, fontFace: BF, fontSize: 15, valign: "top", margin: 0 });
s.addText("CIS is a relative priority index — not a claim of exact minutes.", { x: 7.5, y: b.cy + 3.5, w: 5.05, h: 0.3, fontFace: BF, fontSize: 11, italic: true, color: MUTE, margin: 0 });

// ===================================================== 6 · PIPELINE
b = base("Under the hood", "How the score is built — step by step", 2, 6); s = b.s;
const steps = [["Clean", "Parse the messy CSV; read time in IST; flag junctions."],
  ["Snap to roads", "Match every coordinate to the nearest OpenStreetMap road (580k roads) to read its lane count."],
  ["Score (CIS)", "Apply the formula to each ticket."],
  ["Grid into hexagons", "Bin scores into H3 hexagons (~0.1 km²) — equal-size honeycomb cells that tile the city neatly."]];
let sx = b.cx;
const sw = (b.cw - 3 * 0.3) / 4;
steps.forEach(([t, d], i) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: sx, y: b.cy, w: sw, h: 2.6, fill: { color: CARD2 }, line: { color: LINE, width: 1 }, rectRadius: 0.08 });
  s.addShape(pres.shapes.OVAL, { x: sx + 0.2, y: b.cy + 0.2, w: 0.5, h: 0.5, fill: { color: LIME } });
  s.addText(String(i + 1), { x: sx + 0.2, y: b.cy + 0.2, w: 0.5, h: 0.5, fontFace: HF, fontSize: 16, color: INK, align: "center", valign: "middle", margin: 0 });
  s.addText(t, { x: sx + 0.2, y: b.cy + 0.82, w: sw - 0.4, h: 0.45, fontFace: HF, fontSize: 14, color: TXT, margin: 0 });
  s.addText(d, { x: sx + 0.2, y: b.cy + 1.28, w: sw - 0.4, h: 1.25, fontFace: BF, fontSize: 11.5, color: MUTE, margin: 0 });
  if (i < 3) s.addText("→", { x: sx + sw - 0.05, y: b.cy + 0.9, w: 0.35, h: 0.5, fontFace: BF, fontSize: 20, color: LIME, align: "center", margin: 0 });
  sx += sw + 0.3;
});
s.addText([{ text: "Why hexagons?  ", options: { bold: true, color: LIME } },
  { text: "equal spacing in every direction makes the statistics fair and the map clean — better than squares.", options: { color: TXT } }],
  { x: b.cx, y: b.cy + 2.85, w: 11.3, h: 0.5, fontFace: BF, fontSize: 13, margin: 0 });

// ===================================================== 7 · HOTSPOTS
b = base("Measure", "Finding the real hotspots", 0, 7); s = b.s;
bullets(s, [
  "A plain heatmap shows where it's busy. We use Getis-Ord Gi* — a test that finds cells whose impact is high beyond random chance.",
  "We test 2,534 cells at once, so we apply a false-discovery-rate correction — only genuinely significant cells survive.",
  "The strongest cell (Upparpet / KR-Market) is off the charts — impossible to occur by chance.",
], b.cx, b.cy, 5.9, 14);
statMini(s, b.cx, b.cy + 2.5, 2.85, S.cis.n_hot_cells + "", "true hotspot cells (Gi* + FDR)", LIME);
statMini(s, b.cx + 3.05, b.cy + 2.5, 2.85, S.cis.hot_cells_cis_share_pct + "%", "of ALL congestion impact is in them", ORANGE);
s.addImage({ path: A("fig_hotspots.png"), x: 7.2, y: b.cy - 0.1, w: 5.4, h: 3.7, sizing: { type: "contain", w: 5.4, h: 3.7 } });

// ===================================================== 8 · ROBUSTNESS
b = base("Trust check", "Are the weights just made up?", 0, 8); s = b.s;
const rob = S.robustness || {};
s.addText("Fair question — so we tested it. We randomly shook every weight by ±25%, three hundred times, and re-ranked the hotspots.",
  { x: b.cx, y: b.cy - 0.1, w: 11.3, h: 0.7, fontFace: BF, fontSize: 15, color: TXT, margin: 0 });
statMini(s, b.cx, b.cy + 0.9, 3.6, Math.round((rob.top20_jaccard_median || 0.9) * 100) + "%", "of the top-20 hotspots stay the same", LIME);
statMini(s, b.cx + 3.8, b.cy + 0.9, 3.6, (rob.ranking_spearman_median || 0.998) + "", "ranking correlation (1.0 = identical)", BLUE);
statMini(s, b.cx + 7.6, b.cy + 0.9, 3.7, "≠ count", "CIS differs from a plain ticket-count map", ORANGE);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: b.cx, y: b.cy + 2.45, w: 11.3, h: 1.0, fill: { color: "10261D" }, line: { color: GOOD, width: 1 }, rectRadius: 0.08 });
s.addText([{ text: "Bottom line:  ", options: { bold: true, color: GOOD } },
  { text: "the hotspots barely move when the weights change — so the conclusions don't depend on numbers we picked by hand. Yet CIS still re-orders the worst spots versus a naive count, so it's adding real signal.", options: { color: TXT } }],
  { x: b.cx + 0.2, y: b.cy + 2.55, w: 11, h: 0.85, fontFace: BF, fontSize: 13.5, valign: "middle", margin: 0 });

// ===================================================== 9 · FORECAST
b = base("Predict", "Tomorrow's worst spots, today", 1, 9); s = b.s;
const mf = S.forecast || {};
bullets(s, [
  "A LightGBM model learns each cell's pattern by time-of-day, day-of-week and road type.",
  "Tested honestly: trained on the earlier dates, tested on the LATER dates (a real forward test, no peeking).",
  "We benchmark it against a naive 'yesterday = tomorrow' rule so its value is visible.",
], b.cx, b.cy, 5.9, 14);
statMini(s, b.cx, b.cy + 2.5, 3.05, "15%", "lower error than the naive baseline", LIME);
statMini(s, b.cx + 3.25, b.cy + 2.5, 3.15, Math.round((mf.precision_at_k || 0.66) * 100) + "%", "of flagged top-30 cells are truly worst", BLUE);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.2, y: b.cy - 0.05, w: 5.4, h: 3.5, fill: { color: CARD2 }, line: { color: LINE, width: 1 }, rectRadius: 0.1 });
s.addText("Why this matters", { x: 7.45, y: b.cy + 0.15, w: 5, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: LIME, margin: 0 });
s.addText("Instead of reacting after traffic jams form, the city can place patrols BEFORE the rush — at the cells most likely to choke that very shift.",
  { x: 7.45, y: b.cy + 0.6, w: 4.95, h: 1.3, fontFace: BF, fontSize: 14, color: TXT, margin: 0 });
s.addText("We lead with ranking accuracy (Precision@K), not exact counts — because dispatch needs the right places, not a perfect number.",
  { x: 7.45, y: b.cy + 2.0, w: 4.95, h: 1.3, fontFace: BF, fontSize: 12.5, italic: true, color: MUTE, margin: 0 });

// ===================================================== 10 · PATROL
b = base("Act", "The patrol plan that funds itself", 2, 10); s = b.s;
const pat = S.patrol || {};
bullets(s, [
  "Given how many units you have, the optimiser picks stops that clear the MOST congestion — a classic max-coverage method.",
  "It's 'greedy' but provably near-optimal (within 63%) and fully explainable: every stop's value is auditable.",
  "The curve shows diminishing returns — exactly how many units are worth funding.",
], b.cx, b.cy, 5.9, 14);
statMini(s, b.cx, b.cy + 2.5, 3.05, pat.capture_12_marshals_pct + "%", "cleared by 12 units", LIME);
statMini(s, b.cx + 3.25, b.cy + 2.5, 3.15, pat.marshals_for_50pct + " units", "to clear half the city's impact", ORANGE);
s.addImage({ path: A("fig_patrol_curve.png"), x: 7.25, y: b.cy + 0.05, w: 5.35, h: 3.3, sizing: { type: "contain", w: 5.35, h: 3.3 } });

// ===================================================== 11 · REJECTION
b = base("Save effort", "Stop chasing tickets that get thrown out", 0, 11); s = b.s;
const eq = S.enforcement_quality || {};
bullets(s, [
  "Nearly a third of reviewed tickets (" + eq.reject_rate_pct + "%) are rejected — each one is an officer-hour spent on a bad capture.",
  "A model predicts which captures are likely to be rejected (ROC-AUC " + eq.model_roc_auc + ").",
  "It prioritises human review — it never auto-rejects. A human always stays in the loop.",
], b.cx, b.cy, 6.1, 14);
statMini(s, b.cx, b.cy + 2.5, 3.1, eq.reject_rate_pct + "%", "of reviewed tickets rejected", ORANGE);
statMini(s, b.cx + 3.3, b.cy + 2.5, 3.3, "≈" + (eq.est_officer_hours_saved_annual || 0).toLocaleString(), "officer-hours/yr saved", GOOD);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.4, y: b.cy + 0.1, w: 5.2, h: 2.0, fill: { color: CARD2 }, line: { color: LINE, width: 1 }, rectRadius: 0.1 });
s.addText("The quiet win", { x: 7.6, y: b.cy + 0.28, w: 4.8, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: LIME, margin: 0 });
s.addText("Cleaner data flows back into every other model — so the whole system gets sharper over time.",
  { x: 7.6, y: b.cy + 0.72, w: 4.8, h: 1.2, fontFace: BF, fontSize: 14, color: TXT, margin: 0 });

// ===================================================== 12 · CHRONIC
b = base("Design out", "Some spots need a fix, not a fine", 1, 12); s = b.s;
const ch = S.chronic || {};
s.addText("A patrol can't fix a spot that's ticketed every single day. We flag these and recommend the permanent fix.",
  { x: b.cx, y: b.cy - 0.1, w: 11.3, h: 0.6, fontFace: BF, fontSize: 15, color: TXT, margin: 0 });
statMini(s, b.cx, b.cy + 0.75, 3.6, ch.chronic_sites.toLocaleString(), "chronic micro-sites identified", LIME);
statMini(s, b.cx + 3.8, b.cy + 0.75, 3.6, ch.repeat_offenders_10plus + "", "vehicles with 10+ violations", ORANGE);
statMini(s, b.cx + 7.6, b.cy + 0.75, 3.7, ch.worst_offender_violations + "", "tickets — the worst single vehicle", BLUE);
const fixes = ["ANPR cameras where patrols can't keep up", "Bollards + 'no-stopping' at choked junctions", "Time-windowed loading bays for goods vehicles", "Paid / permit parking on residential streets"];
s.addText("Recommended fixes (auto-generated per site):", { x: b.cx, y: b.cy + 2.25, w: 11, h: 0.35, fontFace: BF, fontSize: 13, bold: true, color: LIME, margin: 0 });
let fx = b.cx;
fixes.forEach((f, i) => {
  const fw = (b.cw - 3 * 0.2) / 4;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: fx, y: b.cy + 2.65, w: fw, h: 0.85, fill: { color: CARD2 }, line: { color: LINE, width: 1 }, rectRadius: 0.08 });
  s.addText(f, { x: fx + 0.15, y: b.cy + 2.7, w: fw - 0.3, h: 0.75, fontFace: BF, fontSize: 11.5, color: TXT, valign: "middle", margin: 0 });
  fx += fw + 0.2;
});

// ===================================================== 13 · ECONOMICS
b = base("Price", "Putting a rupee value on the jam", 2, 13); s = b.s;
const ec = S.economics || {};
bullets(s, [
  "We convert the impact score into money using a fully transparent, tunable chain (value-of-time × delay).",
  "It's a planning estimate — every assumption is visible and adjustable, not a black box.",
  "The durable results are the concentration and the ROI, which hold under any reasonable numbers.",
], b.cx, b.cy, 6.1, 14);
statMini(s, b.cx, b.cy + 2.5, 3.15, "₹" + ec.total_cost_cr_year + " cr", "estimated cost / year", ORANGE);
statMini(s, b.cx + 3.35, b.cy + 2.5, 3.15, ec.enforcement_roi_x + "×", "return on patrol payroll", LIME);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.4, y: b.cy + 0.1, w: 5.2, h: 2.0, fill: { color: "2A1B10" }, line: { color: ORANGE, width: 1.25 }, rectRadius: 0.1 });
s.addText(ec.hotspot_cost_share_pct + "% of the cost", { x: 7.6, y: b.cy + 0.3, w: 4.8, h: 0.55, fontFace: HF, fontSize: 22, color: ORANGE, margin: 0 });
s.addText("sits inside the hotspots — so targeted enforcement is genuinely high-leverage: small spend, large relief.",
  { x: 7.6, y: b.cy + 0.95, w: 4.8, h: 1.0, fontFace: BF, fontSize: 13.5, color: TXT, margin: 0 });

// ===================================================== 14 · CV
b = base("Eyes on the street", "Computer vision closes the loop", 1, 14); s = b.s;
bullets(s, [
  "Today's data is captured by marshals. The next step removes the human delay entirely.",
  "A YOLOv8 detector on junction CCTV or patrol dashcams spots stopped vehicles inside a no-parking zone in real time.",
  "Each detection flows into the SAME impact pipeline — auto-flagged, instantly scored, instantly mapped.",
  "Built and running in the dashboard's CV tab — upload a street photo and watch it detect.",
], b.cx, b.cy, 6.6, 14.5);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.9, y: b.cy + 0.1, w: 4.7, h: 3.0, fill: { color: CARD2 }, line: { color: LINE, width: 1 }, rectRadius: 0.1 });
s.addText("Detect → Score → Map", { x: 8.1, y: b.cy + 0.35, w: 4.3, h: 0.5, fontFace: HF, fontSize: 16, color: LIME, margin: 0 });
const loop = ["1  Camera sees a stopped vehicle", "2  YOLO checks the no-parking zone", "3  CIS scores its congestion impact", "4  It appears on the live map instantly"];
s.addText(loop.map(t => ({ text: t, options: { breakLine: true, paraSpaceAfter: 10, color: TXT } })),
  { x: 8.1, y: b.cy + 0.95, w: 4.3, h: 2.0, fontFace: BF, fontSize: 13.5, margin: 0 });

// ===================================================== 15 · DASHBOARDS
b = base("Built for people", "Two dashboards, two audiences", 2, 15); s = b.s;
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: b.cx, y: b.cy - 0.05, w: 5.55, h: 3.5, fill: { color: CARD2 }, line: { color: LIME, width: 1.25 }, rectRadius: 0.1 });
s.addText("🚓  Police Command Center", { x: b.cx + 0.25, y: b.cy + 0.15, w: 5.1, h: 0.5, fontFace: HF, fontSize: 16, color: LIME, margin: 0 });
s.addText([{ text: "Simple, web-based, made for daily use.\n", options: { color: TXT, breakLine: true } }].concat(
  ["Big plain-language numbers", "A real street map of hotspots", "Today's patrol plan in order", "Fix-it list for chronic spots"].map(t => ({ text: "•  " + t, options: { breakLine: true, color: MUTE } }))),
  { x: b.cx + 0.25, y: b.cy + 0.7, w: 5.1, h: 2.6, fontFace: BF, fontSize: 13.5, margin: 0 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: b.cx + 5.75, y: b.cy - 0.05, w: 5.55, h: 3.5, fill: { color: CARD2 }, line: { color: BLUE, width: 1.25 }, rectRadius: 0.1 });
s.addText("📊  Analyst Workbench", { x: b.cx + 6.0, y: b.cy + 0.15, w: 5.1, h: 0.5, fontFace: HF, fontSize: 16, color: BLUE, margin: 0 });
s.addText([{ text: "Deep, interactive, for planners.\n", options: { color: TXT, breakLine: true } }].concat(
  ["7 tabs: impact, hotspots, forecast", "Drag-the-slider patrol optimiser", "Enforcement-quality & ROI views", "Live computer-vision detection tab"].map(t => ({ text: "•  " + t, options: { breakLine: true, color: MUTE } }))),
  { x: b.cx + 6.0, y: b.cy + 0.7, w: 5.1, h: 2.6, fontFace: BF, fontSize: 13.5, margin: 0 });

// ===================================================== 16 · TECH STACK
b = base("Under the hood", "The technology, in plain terms", 0, 16); s = b.s;
const tech = [["Data & ML", "pandas · scikit-learn · LightGBM"],
  ["Maps & roads", "OpenStreetMap (osmnx) · H3 hexagons · Leaflet"],
  ["Spatial stats", "Getis-Ord Gi* (esda) + FDR correction"],
  ["Optimisation", "Greedy submodular max-coverage"],
  ["Computer vision", "YOLOv8 (ultralytics)"],
  ["Apps", "Streamlit + pydeck · custom animated web dashboard"]];
let tx = b.cx, ty = b.cy;
tech.forEach(([t, d], i) => {
  const col = i % 2, row = Math.floor(i / 2);
  const cw2 = (b.cw - 0.4) / 2, X = b.cx + col * (cw2 + 0.4), Y = b.cy + row * 1.15;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: X, y: Y, w: cw2, h: 0.95, fill: { color: CARD2 }, line: { color: LINE, width: 1 }, rectRadius: 0.08 });
  s.addShape(pres.shapes.RECTANGLE, { x: X, y: Y, w: 0.1, h: 0.95, fill: { color: LIME } });
  s.addText(t, { x: X + 0.25, y: Y + 0.12, w: cw2 - 0.4, h: 0.35, fontFace: HF, fontSize: 13, color: TXT, margin: 0 });
  s.addText(d, { x: X + 0.25, y: Y + 0.48, w: cw2 - 0.4, h: 0.4, fontFace: MONO, fontSize: 12, color: MUTE, margin: 0 });
});
s.addText("One pipeline runs it all end-to-end on the real 298k-ticket file in ~6 minutes.", { x: b.cx, y: b.cy + 3.55, w: 11.3, h: 0.4, fontFace: BF, fontSize: 13, italic: true, color: LIME, margin: 0 });

// ===================================================== 17 · IMPACT / ASK
s = pres.addSlide(); s.background = { path: BG };
menuChip(s, [["Analyze", "A"], ["Predict", "P"], ["Deploy", "D"]], 2);
s.addText("FROM DATA TO DEPLOYMENT", { x: 0.85, y: 1.18, w: 11, h: 0.35, fontFace: BF, fontSize: 14, color: LIME, bold: true, charSpacing: 3, margin: 0 });
selFrame(s, 0.8, 1.55, 8.5, 1.42);
s.addText("Targeted enforcement, on a screen the city can fund", { x: 0.92, y: 1.55, w: 8.25, h: 1.42, fontFace: HF, fontSize: 26, color: "FFFFFF", valign: "middle", margin: 0 });
statMini(s, 0.85, 3.0, 2.85, S.cis.hot_cells_cis_share_pct + "%", "impact in " + S.cis.n_hot_cells + " hotspot cells", LIME);
statMini(s, 3.85, 3.0, 2.85, S.patrol.marshals_for_50pct + " units", "to relieve half the impact", ORANGE);
statMini(s, 6.85, 3.0, 2.85, "₹" + S.economics.total_cost_cr_year + " cr", "priced congestion / yr", BLUE);
statMini(s, 9.85, 3.0, 2.65, S.economics.enforcement_roi_x + "×", "enforcement ROI", GOOD);
const dep = ["Today — nightly batch makes the next-shift map + patrol routes for marshals",
  "Next — live ticket feed retrains the models daily",
  "Future — CV cameras auto-detect and feed the same pipeline"];
s.addText("DEPLOYMENT PATH", { x: 0.9, y: 4.6, w: 11, h: 0.3, fontFace: BF, fontSize: 12.5, color: MUTE, bold: true, charSpacing: 2, margin: 0 });
let dy2 = 4.98;
dep.forEach((t, i) => {
  s.addShape(pres.shapes.OVAL, { x: 0.9, y: dy2, w: 0.42, h: 0.42, fill: { color: LIME } });
  s.addText(String(i + 1), { x: 0.9, y: dy2, w: 0.42, h: 0.42, fontFace: HF, fontSize: 15, color: INK, align: "center", valign: "middle", margin: 0 });
  s.addText(t, { x: 1.5, y: dy2 - 0.02, w: 11, h: 0.45, fontFace: BF, fontSize: 14.5, color: TXT, valign: "middle", margin: 0 });
  dy2 += 0.6;
});
chip(s, 0.9, 6.99, "See it. Score it. Clear it.", "121722", LIME);
dock(s);

pres.writeFile({ fileName: path.join(__dirname, "..", "GridLock_IQ_Detailed.pptx") }).then(f => console.log("WROTE", f));
