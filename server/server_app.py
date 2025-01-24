from flask import Flask, Response, request, jsonify
import logging
import time
import cv2
import os
from .config import picam2
from .gpio_setup import setup_gpio
from .camera_manager import (
    snapshot_event,
    init_camera,
    cleanup_camera,
    switch_camera_mode,
    camera_active,
    capture_frame,
    select_camera
)

app = Flask(__name__)

@app.before_first_request
def startup():
    # Setup GPIO + camera once at startup
    setup_gpio()
    init_camera()

def generate_video(camera_id):
    while True:
        if snapshot_event.is_set():
            time.sleep(0.1)
            continue

        frame = capture_frame(camera_id)
        if frame is None:
            continue
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.05)

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    return Response(generate_video(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot/<camera_id>')
def snapshot(camera_id):
    if not select_camera(camera_id):
        return "Invalid camera ID", 400

    snapshot_event.set()
    with snapshot_event._cond:  # or lock, but we rely on snapshot_event for pausing
        try:
            # Stop camera, go to still mode
            switch_camera_mode('none')
            switch_camera_mode('still')

            frame = picam2.capture_array()
            if frame is None:
                snapshot_event.clear()
                return "Failed to capture frame", 500

            # Save server-side if you want
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"snapshot_{camera_id}_{timestamp}.jpg"
            os.makedirs("snapshots", exist_ok=True)
            filepath = os.path.join("snapshots", filename)
            cv2.imwrite(filepath, frame)

            # Return to video mode
            switch_camera_mode('none')
            switch_camera_mode('video')
            snapshot_event.clear()

            ret, encoded = cv2.imencode('.jpg', frame)
            if not ret:
                return "Failed to encode JPEG", 500
            return Response(encoded.tobytes(), mimetype='image/jpeg')

        except Exception as e:
            snapshot_event.clear()
            logging.error(f"Error capturing snapshot: {e}")
            return f"Error: {e}", 500

@app.route('/health')
def health():
    return jsonify({"status": "OK"}), 200

@app.teardown_appcontext
def shutdown(_):
    cleanup_camera()

