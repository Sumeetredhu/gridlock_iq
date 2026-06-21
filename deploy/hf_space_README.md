---
title: GridLock IQ CV
emoji: 🚦
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# GridLock IQ — CV backend (+ dashboards)

This Hugging Face Space runs `server.py`, which serves the GridLock IQ web
dashboards **and** the live YOLOv8 detection API:

- `/`               → police dashboard
- `/analyst.html`   → analyst dashboard
- `GET  /api/health`       → `{ ok, yolo, cv2 }`
- `POST /api/detect`       → image → annotated result + counts
- `POST /api/detect_video` → short video → sampled annotated frames

To use it as the CV backend for a Vercel-hosted frontend, set
`window.GLIQ_API` in `app_web/config.js` to this Space's URL and redeploy the
frontend. CORS is already enabled in `server.py`.

**Files to push to this Space:** `Dockerfile`, `requirements-server.txt`,
`server.py`, `src/cv_detect.py`, `app_web/`, and this `README.md`.
