# Deploying GridLock IQ — permanent public URL

**Good news:** the entire app is now a **self-contained static site**. The dashboards,
the data, the maps, the charts **and the live YOLOv8 CV** (which now runs **in your browser**
via ONNX — no backend) all live in the `app_web/` folder. So you can host it on any free
static host and get a **permanent URL that needs no server and no PC running**.

> You only need to do the final step (it needs a 30-second free sign-in to a host — I can't
> log into your accounts). Everything else is done.

---

## ✅ Easiest — Netlify Drop (permanent, free, ~2 minutes, no Git)
1. Go to **<https://app.netlify.com/drop>**.
2. Drag the **`gridlock_iq/app_web`** folder onto the page. *(Or drag `gridlock_iq_site.zip` — a ready bundle is in the project root.)*
3. It uploads and gives you a live URL like `https://your-name.netlify.app` — **this is your permanent submission link.**
4. Sign in (free, GitHub/email) and click **"Claim/keep this site"** so the URL stays forever. Rename it in Site settings → e.g. `gridlock-iq.netlify.app`.

Open it: `/` = Police dashboard, `/analyst.html` = Analyst dashboard. Go to the **CV tab**, drag in a street photo → it detects vehicles **right in the browser**. Works with your PC off. ✔️

---

## Alternative hosts (all permanent + free, pick any one)
- **Vercel:** <https://vercel.com/new> → drag the `app_web` folder (or `vercel --prod --cwd app_web`). `vercel.json` is already included.
- **Cloudflare Pages:** dash.cloudflare.com → Workers & Pages → Create → Pages → "Upload assets" → drag `app_web`.
- **GitHub Pages:** push the repo, then repo **Settings → Pages → Deploy from branch → `main` / root**, and set the site folder to `app_web` (or move its contents to a `/docs` folder). URL: `https://<user>.github.io/<repo>/`.

---

## What works where
| Feature | Static deploy (Netlify/Vercel/Pages) |
|---|---|
| Police + Analyst dashboards, maps, charts, KPIs, patrol slider | ✅ fully |
| **Live CV — image** (YOLOv8 in-browser, ONNX) | ✅ no backend needed |
| Live CV — **video** | ⚠️ needs the local server (`python server.py`); image works everywhere |

For video CV or faster server-side inference, run `python server.py` locally, or host it
(Docker `Dockerfile` included → Hugging Face Spaces / Render) and put that URL in
`app_web/config.js` as `window.GLIQ_API`. **Not required** for a fully-working public demo.

---

## Putting the code on GitHub (separate from hosting)
Hosting (above) does **not** need GitHub. To also publish the source:
1. Create the repo at <https://github.com/new> — name it `gridlock_iq`, **Public**, no README. Copy the exact URL it shows.
2. In the project folder:
   ```bash
   git remote set-url origin https://github.com/<your-username>/<exact-repo-name>.git
   git push -u origin main
   ```
   A browser window will pop to authorize (that sign-in is the one step only you can do).
   *Tip:* if you don't have GitHub auth set up, the easiest is **GitHub Desktop** → "Add existing repository" → select this folder → **Publish**.

> The earlier `git push` failed with "Repository not found" because the repo didn't exist at
> that exact name (or was private). Create it Public with the name `gridlock_iq` and the push above works.

## Cost
Netlify / Vercel / Cloudflare Pages / GitHub Pages static hosting: **free, permanent, no card**. The 12 MB model downloads once in the visitor's browser, then caches.
