# Deploying GridLock IQ (public access)

Your "site" is **two pieces** that deploy differently:

| Piece | What it is | Where it can go |
|---|---|---|
| **Dashboards** (`app_web/`) | static HTML/JS — police + analyst, self-contained (data + libs bundled) | **Vercel** (free), any static host |
| **Live CV** (`server.py`) | Flask + **YOLOv8/PyTorch** — the `/api/detect` endpoints | **Hugging Face Spaces** (free CPU), Render/Railway (paid), or local |

> Vercel **cannot** run the CV model — its serverless functions cap at ~250–500 MB and torch+ultralytics is far bigger (and video uploads exceed the 4.5 MB body limit). That's a platform fact, not a config issue. So CV lives on a Python host.

Everything below is **already wired** in this repo: `server.py` sends CORS headers and honors `$PORT`; `app_web/config.js` lets the frontend point at any backend; `vercel.json` and `Dockerfile` exist.

---

## ✅ Recommended (100% free, everything works): Vercel + Hugging Face Spaces

### 1 — Frontend → Vercel (the dashboards)
Pick one:
- **Drag-and-drop (no install):** go to <https://vercel.com/new> → "Deploy" / Vercel Drop → drag the **`gridlock_iq/app_web` folder** → name it `gridlock-iq` → Deploy. You get a `*.vercel.app` URL in seconds.
- **CLI:** `npm i -g vercel` then
  ```bash
  vercel --prod --cwd "C:\Users\Amy678\Desktop\Flipkart\gridlock_iq\app_web"
  ```
- **GitHub auto-deploy:** push the repo, import it at vercel.com/new, and set **Root Directory = `gridlock_iq/app_web`**, Framework = Other.

Verify: `/` shows the police dashboard, `/analyst` shows the analyst one, maps + charts render. (The CV tab will say "server offline" until step 3.)

### 2 — Backend → Hugging Face Space (the CV model)
Free **CPU-basic** Space (2 vCPU / 16 GB RAM — enough for CPU YOLO; Render free's 512 MB is **not**).
1. <https://huggingface.co> → **New Space** → **Docker** SDK → **Public** → CPU basic.
2. Upload these to the Space (drag in the web UI, or `git push`):
   `Dockerfile`, `requirements-server.txt`, `server.py`, `src/cv_detect.py`, the `app_web/` folder, and a `README.md` with this front-matter (HF needs it):
   ```
   ---
   title: GridLock IQ CV
   sdk: docker
   app_port: 7860
   ---
   ```
   (A ready copy is in `deploy/hf_space_README.md` — rename it to `README.md` in the Space.)
3. Wait for **Running**, then open `https://<you>-gridlock-iq-cv.hf.space/api/health` → should return `{"ok":true,"yolo":true,"cv2":true}`.

### 3 — Connect them (one line)
Edit **`app_web/config.js`**:
```js
window.GLIQ_API = "https://<you>-gridlock-iq-cv.hf.space";
```
Redeploy the Vercel frontend (re-drop the folder, or re-run the CLI). Open your Vercel URL → **analyst → CV tab → upload an image** → annotated result returns. Done — fully public, free, CV working.

> ⏱️ The Space sleeps after ~48 h idle (~30–90 s cold start). Hit `/api/health` a minute before a demo to pre-warm it.

---

## ⚡ Fastest (dashboards only): just Vercel
Do **step 1** above and stop. Everything works except the live CV tab (it shows a friendly "start the backend" note). Perfect if you don't need in-browser detection on the public link.

---

## 🟦 Simplest all-in-one (free, CV best-effort): Streamlit Community Cloud
One URL for the full analyst app incl. CV, no Vercel/HF.
1. Push the repo to **public** GitHub. **Important:** the parquet artifacts are git-ignored — force-add them so the cloud app has data:
   ```bash
   git add -f gridlock_iq/data/processed/*.parquet gridlock_iq/outputs/summary.json
   ```
2. Add a trimmed `requirements.txt` (streamlit, pandas, pyarrow, plotly, pydeck, matplotlib, numpy, h3, Pillow, ultralytics) and a `packages.txt` containing `libgl1` (OpenCV needs it).
3. <https://share.streamlit.io> → New app → pick the repo → main file `gridlock_iq/app/streamlit_app.py` → Deploy.
- Caveat: ~1 GB RAM cap — the 6 data tabs run fine; CV works for a single small image but video/concurrency is flaky. Use the Vercel+HF path if CV matters.

---

## 💵 One URL, everything, no cold starts (~$7/mo, optional)
The `Dockerfile` already serves **both** the dashboards and the CV API from `server.py`. Deploy it to **Render Starter (2 GB)** or a paid HF tier → single URL, no sleep. Only needed if you dislike the free split.

---

## 🔒 Before going public
`data.js` / `data.json` are downloaded by the browser, so their contents become world-readable — that includes the repeat-offender vehicle numbers (these are the dataset's **anonymized** `FKN…` IDs, so fine, but confirm you're OK exposing them). Redact in `src/export_web.py` and re-run it if needed.

## Cost (2026)
- Vercel Hobby: **free** (100 GB/mo, HTTPS, custom domains).
- HF Spaces CPU-basic: **free** (16 GB RAM, sleeps when idle).
- Streamlit Cloud: **free** (~1 GB RAM).
- Render/Railway/Fly free tiers: **not** viable for torch (512 MB / removed) → paid (~$5–7/mo) only if you want the single-URL convenience.
