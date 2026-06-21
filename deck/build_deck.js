const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const S = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "outputs", "summary.json"), "utf8"));
const ASSET = (f) => path.join(__dirname, "..", "assets", f);

// ---- palette (matches the dashboard command-center look) -------------------
const BG = "0E1520", PANEL = "16202E", PANEL2 = "1B2A3A";
const MINT = "16E0A3", CORAL = "F5772A", BLUE = "4FA8FF";
const TXT = "EAF1F8", MUTE = "9FB3C8", LINE = "24384A";
const HF = "Georgia", BF = "Calibri";
const shadow = () => ({ type: "outer", color: "000000", blur: 8, offset: 3, angle: 135, opacity: 0.30 });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";          // 13.3 x 7.5
pres.author = "GridLock IQ";
pres.title = "GridLock IQ — Parking-Induced Congestion Intelligence";
const W = 13.3, H = 7.5;

function header(slide, kicker, title, dark) {
  slide.addText(kicker.toUpperCase(), { x: 0.6, y: 0.42, w: 12, h: 0.3, fontFace: BF,
    fontSize: 12, color: MINT, bold: true, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.6, y: 0.7, w: 12.1, h: 0.9, fontFace: HF,
    fontSize: 30, color: dark ? TXT : "12202E", bold: true, margin: 0 });
}

function statCard(slide, x, y, w, h, big, label, color) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: PANEL },
    line: { color: LINE, width: 1 }, rectRadius: 0.08, shadow: shadow() });
  slide.addText(big, { x: x + 0.1, y: y + 0.18, w: w - 0.2, h: h * 0.52, fontFace: HF,
    fontSize: 30, color: color || MINT, bold: true, align: "center", valign: "middle", margin: 0 });
  slide.addText(label, { x: x + 0.12, y: y + h * 0.62, w: w - 0.24, h: h * 0.34, fontFace: BF,
    fontSize: 11.5, color: MUTE, align: "center", valign: "top", margin: 0 });
}

// ============================================================ SLIDE 1 — TITLE
let s = pres.addSlide(); s.background = { color: BG };
s.addImage({ path: ASSET("fig_cis_heatmap.png"), x: 8.35, y: 0.0, w: 4.95, h: 4.95,
  sizing: { type: "cover", w: 4.95, h: 4.95 }, transparency: 18 });
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 8.6, h: H, fill: { color: BG } });
s.addText("FLIPKART GRiD · ML TRACK", { x: 0.7, y: 0.8, w: 8, h: 0.3, fontFace: BF,
  fontSize: 13, color: MINT, bold: true, charSpacing: 3, margin: 0 });
s.addText("GridLock IQ", { x: 0.65, y: 1.35, w: 9, h: 1.2, fontFace: HF, fontSize: 60,
  color: TXT, bold: true, margin: 0 });
s.addText("Parking-Induced Congestion Intelligence", { x: 0.7, y: 2.55, w: 8.4, h: 0.5,
  fontFace: BF, fontSize: 22, color: MUTE, margin: 0 });
s.addText([{ text: "“We don't count tickets — we measure the traffic they steal.”",
  options: { italic: true } }], { x: 0.7, y: 3.35, w: 7.6, h: 0.8, fontFace: HF, fontSize: 19,
  color: MINT, margin: 0 });
const econ = S.economics || {}, cis = S.cis || {};
statCard(s, 0.7, 4.7, 2.4, 1.7, cis.hot_cells_cis_share_pct + "%", "of all congestion impact sits in " + cis.n_hot_cells + " hotspot cells", MINT);
statCard(s, 3.25, 4.7, 2.4, 1.7, "50%", "of impact relieved by just 24 optimally-placed patrol units", CORAL);
statCard(s, 5.8, 4.7, 2.4, 1.7, econ.enforcement_roi_x + "×", "return on patrol payroll (planning estimate)", BLUE);
s.addText("298,450 real Bengaluru enforcement tickets  ·  Nov 2023 – Apr 2024", { x: 0.7, y: 6.7,
  w: 9, h: 0.3, fontFace: BF, fontSize: 12, color: MUTE, margin: 0 });

// ============================================================ SLIDE 2 — PROBLEM
s = pres.addSlide(); s.background = { color: "F4F7FA" };
header(s, "The operational challenge", "Enforcement is blind to congestion impact", false);
const probs = [
  ["Reactive & patrol-based", "Officers chase reports; no system points them to the worst spots first."],
  ["No impact heatmap", "Tickets are counted, but their effect on traffic flow is never measured."],
  ["Can't prioritize zones", "With limited marshals, nobody knows which 1% of streets to cover."],
];
let py = 1.85;
probs.forEach(([t, d], i) => {
  s.addShape(pres.shapes.OVAL, { x: 0.7, y: py, w: 0.5, h: 0.5, fill: { color: CORAL } });
  s.addText(String(i + 1), { x: 0.7, y: py, w: 0.5, h: 0.5, fontFace: HF, fontSize: 20,
    color: "FFFFFF", bold: true, align: "center", valign: "middle", margin: 0 });
  s.addText(t, { x: 1.4, y: py - 0.05, w: 6.6, h: 0.4, fontFace: BF, fontSize: 18, bold: true,
    color: "12202E", margin: 0 });
  s.addText(d, { x: 1.4, y: py + 0.38, w: 6.6, h: 0.6, fontFace: BF, fontSize: 13.5, color: "47596B", margin: 0 });
  py += 1.25;
});
// data panel on right
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.6, y: 1.85, w: 4.1, h: 4.0, fill: { color: "12202E" },
  rectRadius: 0.1, shadow: shadow() });
s.addText("THE DATA", { x: 8.8, y: 2.1, w: 3.7, h: 0.3, fontFace: BF, fontSize: 12, color: MINT,
  bold: true, charSpacing: 3, margin: 0 });
const ds = S.dataset || {};
const dlines = [
  [ds.tickets.toLocaleString(), "parking-enforcement tickets"],
  [ds.stations + " stations", "across Bengaluru"],
  [ds.junction_share_pct + "%", "occur at a mapped junction"],
  [ds.unique_vehicles.toLocaleString(), "unique vehicles tracked"],
];
let dy = 2.5;
dlines.forEach(([b, l]) => {
  s.addText(b, { x: 8.8, y: dy, w: 3.7, h: 0.45, fontFace: HF, fontSize: 24, color: TXT, bold: true, margin: 0 });
  s.addText(l, { x: 8.8, y: dy + 0.45, w: 3.7, h: 0.3, fontFace: BF, fontSize: 12.5, color: MUTE, margin: 0 });
  dy += 0.85;
});

// ============================================================ SLIDE 3 — THE IDEA (CIS)
s = pres.addSlide(); s.background = { color: "F4F7FA" };
header(s, "The winning idea", "We turn each violation into capacity lost", false);
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 1.8, w: 11.9, h: 1.15, fill: { color: "12202E" },
  rectRadius: 0.1, shadow: shadow() });
s.addText([
  { text: "CIS", options: { color: MINT, bold: true } },
  { text: "  =  severity  ×  vehicle footprint  ×  ", options: { color: TXT } },
  { text: "(1 / lane_count)", options: { color: CORAL, bold: true } },
  { text: "  ×  junction  ×  peak", options: { color: TXT } },
], { x: 0.9, y: 1.8, w: 11.5, h: 1.15, fontFace: "Consolas", fontSize: 21, valign: "middle", margin: 0 });
const ideas = [
  ["Real OSM road fusion", cis.osm_geometry_match_pct + "% of coords snapped to OpenStreetMap; " + cis.explicit_osm_lane_tag_pct + "% carry an explicit lane tag. Blocking 1 of 2 lanes ≫ 1 of 6."],
  ["A priority index, not a count", "A bus double-parked in 1 of 2 lanes at a junction in rush hour scores ~30× a scooter on a footpath."],
  ["Robust to the weights", "Under ±25% weight noise (300 draws) the top-20 hotspots stay " + Math.round((S.robustness||{}).top20_jaccard_median*100) + "% stable."],
];
let iy = 3.35;
ideas.forEach(([t, d]) => {
  s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: iy + 0.05, w: 0.12, h: 0.95, fill: { color: MINT } });
  s.addText(t, { x: 1.0, y: iy, w: 11.4, h: 0.4, fontFace: BF, fontSize: 17, bold: true, color: "12202E", margin: 0 });
  s.addText(d, { x: 1.0, y: iy + 0.42, w: 11.4, h: 0.55, fontFace: BF, fontSize: 13.5, color: "47596B", margin: 0 });
  iy += 1.15;
});

// ============================================================ SLIDE 4 — WHERE IT HURTS
s = pres.addSlide(); s.background = { color: BG };
header(s, "Measure", "Where it hurts — statistically, not by eye", true);
s.addImage({ path: ASSET("fig_hotspots.png"), x: 7.0, y: 1.55, w: 5.8, h: 5.8,
  sizing: { type: "contain", w: 5.8, h: 5.8 } });
statCard(s, 0.7, 1.9, 2.95, 1.6, cis.n_hot_cells, "cells survive Getis-Ord Gi* with Benjamini-Hochberg FDR", MINT);
statCard(s, 3.8, 1.9, 2.95, 1.6, cis.hot_cells_cis_share_pct + "%", "of all congestion impact concentrated there", CORAL);
s.addText([
  { text: "Significant, not just busy.  ", options: { bold: true, color: TXT } },
  { text: "Gi* finds cells whose impact exceeds spatial chance; FDR controls 2,534 simultaneous tests, so every flagged cell is real (top cell z ≈ 27, p ≈ 10⁻¹⁶²).",
    options: { color: MUTE } },
], { x: 0.7, y: 3.8, w: 6.1, h: 1.3, fontFace: BF, fontSize: 15, margin: 0 });
s.addText([
  { text: "🧪 Robustness.  ", options: { bold: true, color: MINT } },
  { text: "Ranking is 90% stable under ±25% weight perturbation (Spearman 0.998) — the conclusion does not depend on hand-set weights.",
    options: { color: MUTE } },
], { x: 0.7, y: 5.2, w: 6.1, h: 1.3, fontFace: BF, fontSize: 15, margin: 0 });

// ============================================================ SLIDE 5 — PREDICT + ACT
s = pres.addSlide(); s.background = { color: "F4F7FA" };
header(s, "Predict & act", "Forecast tomorrow's worst cells, then optimize patrols", false);
s.addImage({ path: ASSET("fig_patrol_curve.png"), x: 6.9, y: 2.4, w: 6.0, h: 3.4,
  sizing: { type: "contain", w: 6.0, h: 3.4 } });
const mf = S.forecast || {}, pat = S.patrol || {};
s.addText("FORECAST (temporal holdout, vs naive baseline)", { x: 0.7, y: 1.8, w: 6, h: 0.3,
  fontFace: BF, fontSize: 12, color: CORAL, bold: true, charSpacing: 2, margin: 0 });
s.addText([
  { text: "15% lower MAE", options: { bold: true, color: "12202E" } },
  { text: " than persistence (" + mf.mae + " vs " + mf.baseline_mae + "); Precision@30 " + mf.precision_at_k + " — matches persistence on ranking, wins on magnitude. A true forward forecast for any shift.",
    options: { color: "47596B" } },
], { x: 0.7, y: 2.15, w: 6.0, h: 1.4, fontFace: BF, fontSize: 14.5, margin: 0 });
s.addText("PATROL OPTIMIZER (greedy submodular, ≥63% of optimal)", { x: 0.7, y: 3.7, w: 6, h: 0.3,
  fontFace: BF, fontSize: 12, color: CORAL, bold: true, charSpacing: 2, margin: 0 });
s.addText([
  { text: pat.capture_12_marshals_pct + "% of city impact from 12 units", options: { bold: true, color: "12202E" } },
  { text: ";  " + pat.marshals_for_50pct + " units relieve 50% — then the curve flattens. That is the city's exact funding answer, drag-the-slider live in the demo.",
    options: { color: "47596B" } },
], { x: 0.7, y: 4.05, w: 6.0, h: 1.6, fontFace: BF, fontSize: 14.5, margin: 0 });

// ============================================================ SLIDE 6 — PAYS FOR ITSELF
s = pres.addSlide(); s.background = { color: "F4F7FA" };
header(s, "It pays for itself", "Recover wasted effort — and price the problem", false);
const eq = S.enforcement_quality || {};
// left column: enforcement quality
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 1.85, w: 5.85, h: 4.4, fill: { color: "FFFFFF" },
  line: { color: "DCE4EC", width: 1 }, rectRadius: 0.1, shadow: shadow() });
s.addText("WASTED-ENFORCEMENT MODEL", { x: 1.0, y: 2.1, w: 5.3, h: 0.3, fontFace: BF, fontSize: 12.5,
  color: CORAL, bold: true, charSpacing: 2, margin: 0 });
s.addText(eq.reject_rate_pct + "%", { x: 1.0, y: 2.5, w: 5.3, h: 0.8, fontFace: HF, fontSize: 40,
  color: "12202E", bold: true, margin: 0 });
s.addText("of reviewed tickets are rejected — each a wasted officer-hour.", { x: 1.0, y: 3.35, w: 5.3,
  h: 0.5, fontFace: BF, fontSize: 13.5, color: "47596B", margin: 0 });
s.addText([
  { text: "ROC-AUC " + eq.model_roc_auc, options: { bold: true, breakLine: true, color: "12202E" } },
  { text: "≈ " + eq.est_officer_hours_saved_annual.toLocaleString() + " officer-hours/yr saveable", options: { bold: true, color: MINT } },
], { x: 1.0, y: 4.0, w: 5.3, h: 1.0, fontFace: BF, fontSize: 16, margin: 0, paraSpaceAfter: 6 });
s.addText("Used to prioritize human review, not auto-reject — human stays in the loop.",
  { x: 1.0, y: 5.5, w: 5.3, h: 0.6, fontFace: BF, fontSize: 12, italic: true, color: "47596B", margin: 0 });
// right column: economics
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.75, y: 1.85, w: 5.85, h: 4.4, fill: { color: "12202E" },
  rectRadius: 0.1, shadow: shadow() });
s.addText("ECONOMIC LAYER (transparent, tunable)", { x: 7.05, y: 2.1, w: 5.3, h: 0.3, fontFace: BF,
  fontSize: 12.5, color: MINT, bold: true, charSpacing: 2, margin: 0 });
s.addText("₹" + econ.total_cost_cr_year + " cr/yr", { x: 7.05, y: 2.5, w: 5.3, h: 0.8, fontFace: HF,
  fontSize: 38, color: TXT, bold: true, margin: 0 });
s.addText("estimated parking-induced congestion cost (planning estimate).", { x: 7.05, y: 3.35, w: 5.3,
  h: 0.5, fontFace: BF, fontSize: 13.5, color: MUTE, margin: 0 });
s.addText([
  { text: econ.hotspot_cost_share_pct + "% of that cost sits in the hotspots", options: { bold: true, breakLine: true, color: CORAL } },
  { text: "Optimized patrol → " + econ.enforcement_roi_x + "× ROI on its payroll", options: { bold: true, color: MINT } },
], { x: 7.05, y: 4.0, w: 5.3, h: 1.0, fontFace: BF, fontSize: 16, margin: 0, paraSpaceAfter: 6 });
s.addText("Targeted enforcement is high-leverage: small spend, large relief.",
  { x: 7.05, y: 5.5, w: 5.3, h: 0.6, fontFace: BF, fontSize: 12, italic: true, color: MUTE, margin: 0 });

// ============================================================ SLIDE 7 — BEYOND + CV
s = pres.addSlide(); s.background = { color: BG };
header(s, "Beyond enforcement", "Design the problem out — and close the loop", true);
const ch = S.chronic || {};
const cards = [
  ["♻️  Chronic sites", ch.chronic_sites.toLocaleString() + " micro-sites are ticketed almost daily yet never improve. We recommend the fix — ANPR cameras, bollards, loading bays — not more tickets."],
  ["🚗  Repeat offenders", ch.repeat_offenders_10plus + " vehicles have 10+ violations (worst: " + ch.worst_offender_violations + "). A leaderboard for escalation and targeted action."],
  ["📷  CV auto-detection (live)", "A YOLOv8 detector on junction CCTV / patrol dashcams flags illegal parking in real time and feeds the SAME CIS pipeline — zero human latency. Built and running."],
];
let cx = 0.7;
cards.forEach(([t, d]) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 1.95, w: 3.85, h: 4.2, fill: { color: PANEL },
    line: { color: LINE, width: 1 }, rectRadius: 0.1, shadow: shadow() });
  s.addText(t, { x: cx + 0.28, y: 2.25, w: 3.3, h: 0.6, fontFace: HF, fontSize: 19, color: MINT, bold: true, margin: 0 });
  s.addText(d, { x: cx + 0.28, y: 3.0, w: 3.3, h: 3.0, fontFace: BF, fontSize: 14, color: TXT, margin: 0 });
  cx += 4.0;
});

// ============================================================ SLIDE 8 — IMPACT + ASK
s = pres.addSlide(); s.background = { color: BG };
s.addText("FROM DATA TO DEPLOYMENT", { x: 0.7, y: 0.9, w: 12, h: 0.3, fontFace: BF, fontSize: 13,
  color: MINT, bold: true, charSpacing: 3, margin: 0 });
s.addText("Targeted enforcement, on a screen the city can fund", { x: 0.7, y: 1.3, w: 12, h: 0.9,
  fontFace: HF, fontSize: 32, color: TXT, bold: true, margin: 0 });
statCard(s, 0.7, 2.5, 3.0, 1.7, cis.hot_cells_cis_share_pct + "%", "impact in " + cis.n_hot_cells + " hotspot cells", MINT);
statCard(s, 3.85, 2.5, 3.0, 1.7, pat.marshals_for_50pct + " units", "to relieve 50% of impact", CORAL);
statCard(s, 7.0, 2.5, 3.0, 1.7, "₹" + econ.total_cost_cr_year + " cr", "priced congestion / yr", BLUE);
statCard(s, 10.15, 2.5, 2.45, 1.7, econ.enforcement_roi_x + "×", "enforcement ROI", MINT);
// deployment path
s.addText("DEPLOYMENT PATH", { x: 0.7, y: 4.6, w: 12, h: 0.3, fontFace: BF, fontSize: 12, color: MUTE,
  bold: true, charSpacing: 2, margin: 0 });
const steps = ["Today: nightly batch → next-shift heatmap + patrol routes pushed to marshals",
  "Next: live ticket feed → daily retraining of forecast & rejection models",
  "Future: CV edge detection on CCTV → auto-tickets into the same CIS pipeline"];
let sy = 5.0;
steps.forEach((t, i) => {
  s.addShape(pres.shapes.OVAL, { x: 0.7, y: sy, w: 0.42, h: 0.42, fill: { color: MINT } });
  s.addText(String(i + 1), { x: 0.7, y: sy, w: 0.42, h: 0.42, fontFace: HF, fontSize: 16, color: BG,
    bold: true, align: "center", valign: "middle", margin: 0 });
  s.addText(t, { x: 1.3, y: sy - 0.02, w: 11.2, h: 0.45, fontFace: BF, fontSize: 15, color: TXT, valign: "middle", margin: 0 });
  sy += 0.62;
});
s.addText("GridLock IQ — built end-to-end on 298,450 real Bengaluru tickets.", { x: 0.7, y: 7.0, w: 12,
  h: 0.3, fontFace: BF, fontSize: 12, italic: true, color: MUTE, margin: 0 });

pres.writeFile({ fileName: path.join(__dirname, "..", "GridLock_IQ_Pitch.pptx") }).then((f) =>
  console.log("WROTE", f));
