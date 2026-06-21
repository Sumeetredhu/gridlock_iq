"""
GridLock IQ web server.

Serves the static dashboards in app_web/ AND exposes real YOLOv8 detection
endpoints so the in-page CV tab runs the SAME model as the Streamlit app
(not a mock).  Run:  python server.py    ->  http://localhost:8531/

Endpoints:
  GET  /                  -> police dashboard
  GET  /analyst.html      -> analyst workbench
  GET  /api/health        -> {ok, yolo}
  POST /api/detect        -> image  -> {n_vehicles, n_illegal, image(b64), ...}
  POST /api/detect_video  -> video  -> {frames_sampled, images[b64], ...}
"""
import base64
import io
import os
import sys

from flask import Flask, request, jsonify, send_from_directory

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))
import cv_detect  # noqa: E402

WEB = os.path.join(ROOT, "app_web")
app = Flask(__name__, static_folder=WEB, static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB (allow short videos)


@app.after_request
def _cors(resp):
    # allow a separately-hosted (e.g. Vercel) frontend to call this backend
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp


@app.route("/api/<path:_any>", methods=["OPTIONS"])
def _preflight(_any):
    return ("", 204)


def _b64(pil, fmt="JPEG", q=85):
    buf = io.BytesIO()
    pil.save(buf, fmt, quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@app.route("/")
def index():
    return send_from_directory(WEB, "index.html")


@app.route("/api/health")
def health():
    return jsonify(ok=True, yolo=cv_detect.HAS_YOLO, cv2=cv_detect.HAS_CV2)


@app.route("/api/detect", methods=["POST"])
def detect():
    f = request.files.get("file")
    if f is None:
        return jsonify(error="no file"), 400
    img, res = cv_detect.detect_image(f.read())
    res["image"] = _b64(img)
    return jsonify(res)


@app.route("/api/detect_video", methods=["POST"])
def detect_video():
    f = request.files.get("file")
    if f is None:
        return jsonify(error="no file"), 400
    if not cv_detect.HAS_CV2:
        return jsonify(error="OpenCV not installed"), 500
    frames, res = cv_detect.detect_video(f.read(), max_frames=8)
    res["images"] = [_b64(fr, q=78) for fr in frames]
    return jsonify(res)


if __name__ == "__main__":
    # honour $PORT (Render / HF Spaces / Railway inject it), else GLIQ_PORT, else 8531
    port = int(os.environ.get("PORT", os.environ.get("GLIQ_PORT", "8531")))
    print(f"GridLock IQ  ->  http://localhost:{port}/  (police)")
    print(f"             ->  http://localhost:{port}/analyst.html  (analyst)")
    print(f"YOLO available: {cv_detect.HAS_YOLO} | OpenCV: {cv_detect.HAS_CV2}")
    app.run(host="0.0.0.0", port=port, threaded=True)
