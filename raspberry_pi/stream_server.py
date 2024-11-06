# stream_server.py

from flask import Flask, Response, request, jsonify
import threading
import logging
import time
import cv2
import numpy as np
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import os

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

picam2 = None
stream_thread = None
frame_lock = threading.Lock()
current_frame = None
current_camera_id = 'a'
camera_running = threading.Event()

def setup_gpio_and_i2c(camera_id):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(12, GPIO.OUT)

    # Reset GPIO pins
    GPIO.output(7, False)
    GPIO.output(11, False)
    GPIO.output(12, False)
    time.sleep(1)

    # Define your camera settings
    camera_settings = {
        'a': ('0x04', (False, False, True)),
        'b': ('0x05', (True, False, True)),
        'c': ('0x06', (False, True, False)),
        'd': ('0x07', (True, True, False)),
    }

    if camera_id not in camera_settings:
        raise ValueError("Invalid camera ID")

    i2c_address, pin_states = camera_settings[camera_id]
    # Switch I2C multiplexer
    os.system(f"i2cset -y 1 0x70 0x00 {i2c_address}")
    # Set GPIO pins
    GPIO.output(7, pin_states[0])
    GPIO.output(11, pin_states[1])
    GPIO.output(12, pin_states[2])
    time.sleep(1)

def initialize_camera():
    global picam2
    try:
        setup_gpio_and_i2c(current_camera_id)
        time.sleep(2)  # Allow time for the hardware to settle

        if picam2:
            picam2.stop()
            picam2.close()

        picam2 = Picamera2()
        video_config = picam2.create_video_configuration(main={"size": (640, 480)})
        picam2.configure(video_config)
        picam2.start()
        logging.debug(f"Camera {current_camera_id} initialized")
    except Exception as e:
        logging.error(f"Error initializing camera {current_camera_id}: {e}")

def capture_frames():
    global current_frame
    while camera_running.is_set():
        try:
            frame = picam2.capture_array()
            with frame_lock:
                current_frame = frame.copy()
        except Exception as e:
            logging.error(f"Error capturing frame: {e}")
            break

def start_streaming():
    global stream_thread
    camera_running.set()
    stream_thread = threading.Thread(target=capture_frames)
    stream_thread.start()

def stop_streaming():
    camera_running.clear()
    if stream_thread and stream_thread.is_alive():
        stream_thread.join()
    if picam2:
        picam2.stop()
        picam2.close()

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with frame_lock:
                if current_frame is not None:
                    # Convert the frame from RGB to BGR (OpenCV uses BGR)
                    frame_bgr = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)
                    ret, jpeg = cv2.imencode('.jpg', frame_bgr)
                    if ret:
                        frame_bytes = jpeg.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.01)  # Adjust frame rate as needed
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/switch_camera', methods=['POST'])
def switch_camera():
    global current_camera_id
    data = request.get_json()
    camera_id = data.get('camera_id')
    if camera_id not in ['a', 'b', 'c', 'd']:
        return jsonify({'status': 'error', 'message': 'Invalid camera ID'}), 400
    try:
        logging.debug(f"Switching to camera {camera_id}")
        stop_streaming()
        current_camera_id = camera_id
        initialize_camera()
        start_streaming()
        return jsonify({'status': 'success', 'message': f'Camera switched to {camera_id}'})
    except Exception as e:
        logging.error(f"Error switching camera: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    try:
        initialize_camera()
        start_streaming()
        app.run(host='0.0.0.0', port=5001)
    finally:
        stop_streaming()
        GPIO.cleanup()