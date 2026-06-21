# GridLock IQ — all-in-one container: serves the web dashboards AND the live
# YOLOv8 CV endpoints from one URL. Works on Hugging Face Spaces (Docker SDK),
# Render, Railway, Fly.io, or any Docker host.
FROM python:3.11-slim

# system libs OpenCV / ultralytics need at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# pre-download YOLO weights into the image so first request is fast
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" || true

COPY server.py .
COPY src/cv_detect.py src/cv_detect.py
COPY app_web app_web

# Hugging Face Spaces expects the app on 7860; $PORT overrides for Render/Railway.
ENV PORT=7860
EXPOSE 7860
CMD ["python", "server.py"]
