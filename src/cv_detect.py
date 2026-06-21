"""
Optional CV extension - YOLOv8 illegal-parking detector (image + video).

The hackathon dataset is captured manually by marshals. This module shows the
forward path: an edge model on junction CCTV / patrol dashcams that detects
stopped vehicles inside a no-parking zone and auto-emits a ticket into the same
CIS pipeline - real-time, no human latency.

Runs real YOLOv8 if `ultralytics` is installed; otherwise HAS_YOLO=False and the
dashboard shows the architecture instead of failing.
"""
import io
import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw

# COCO vehicle classes
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

try:
    from ultralytics import YOLO
    HAS_YOLO = True
except Exception:
    HAS_YOLO = False

try:
    import cv2
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        _MODEL = YOLO("yolov8n.pt")  # auto-downloads weights on first call
    return _MODEL


def _no_parking_zone(w, h):
    """Demo no-parking polygon = the kerb-side band (lower 45% of frame)."""
    return [(0, h * 0.55), (w, h * 0.55), (w, h), (0, h)]


def _in_zone(cx, cy, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > cy) != (yj > cy)) and (cx < (xj - xi) * (cy - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def _detect_frame(pil_img, conf=0.35):
    """Annotate one RGB PIL image. Returns (annotated PIL, n_vehicles, n_illegal)."""
    img = pil_img.convert("RGB")
    w, h = img.size
    poly = _no_parking_zone(w, h)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.polygon(poly, fill=(220, 40, 40, 50), outline=(220, 40, 40, 200))
    n_vehicles = n_illegal = 0
    if HAS_YOLO:
        res = _model().predict(np.array(img), verbose=False, conf=conf)[0]
        for b in res.boxes:
            cls = int(b.cls[0])
            if cls not in VEHICLE_CLASSES:
                continue
            n_vehicles += 1
            x1, y1, x2, y2 = [float(v) for v in b.xyxy[0]]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            illegal = _in_zone(cx, cy, poly)
            n_illegal += int(illegal)
            col = (235, 40, 40) if illegal else (40, 220, 140)
            draw.rectangle([x1, y1, x2, y2], outline=col, width=3)
            draw.text((x1, max(0, y1 - 12)),
                      f"{VEHICLE_CLASSES[cls]}{' ILLEGAL' if illegal else ''}", fill=col)
    return img, n_vehicles, n_illegal


def detect_image(image_bytes, conf=0.35):
    """Return (annotated PIL.Image, results dict)."""
    img, nv, ni = _detect_frame(Image.open(io.BytesIO(image_bytes)), conf)
    return img, {"n_vehicles": nv, "n_illegal": ni,
                 "zone": "kerb-side no-parking band",
                 "model": "YOLOv8n" if HAS_YOLO else "not installed"}


def detect_video(video_bytes, max_frames=8, conf=0.35):
    """Sample evenly-spaced frames from a video, detect on each.
    Returns (list[annotated PIL], results dict). Needs OpenCV."""
    if not HAS_CV2:
        raise RuntimeError("OpenCV (cv2) not available — install opencv-python for video.")
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    try:
        tmp.write(video_bytes)
        tmp.close()
        cap = cv2.VideoCapture(tmp.name)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        if total <= 0:
            # some containers don't report count — read sequentially
            idxs = None
        else:
            n = min(max_frames, total)
            idxs = sorted(set(int(i) for i in np.linspace(0, total - 1, n)))
        frames, per_frame = [], []
        tot_v = tot_i = peak_i = 0
        grabbed = 0
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            take = (idxs is None and grabbed < max_frames) or (idxs is not None and i in idxs)
            if take:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil, nv, ni = _detect_frame(Image.fromarray(rgb), conf)
                frames.append(pil)
                per_frame.append({"frame": i, "vehicles": nv, "illegal": ni})
                tot_v += nv
                tot_i += ni
                peak_i = max(peak_i, ni)
                grabbed += 1
                if idxs is None and grabbed >= max_frames:
                    break
            i += 1
        cap.release()
        return frames, {
            "frames_sampled": len(frames), "total_frames": total,
            "total_vehicles": tot_v, "total_illegal_detections": tot_i,
            "peak_illegal_in_a_frame": peak_i, "per_frame": per_frame,
            "model": "YOLOv8n" if HAS_YOLO else "not installed",
        }
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
