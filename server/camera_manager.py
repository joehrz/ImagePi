import time
import os
import logging
import RPi.GPIO as GPIO
from threading import Lock, Event
from picamera2 import Picamera2
import cv2

from .config import (
    ADAPTER_INFO,
    GPIO_PINS,
    picam2,
    VIDEO_CONFIG,
    STILL_CONFIG
)

lock = Lock()
snapshot_event = Event()

camera_active = False  # We'll track if picam2 is running

def select_camera(camera_id):
    """Switch multiplexer to the requested camera."""
    if camera_id not in ADAPTER_INFO:
        logging.error(f"Invalid camera ID: {camera_id}")
        return False
    info = ADAPTER_INFO[camera_id]
    # Set GPIO
    for pin, state in zip(GPIO_PINS, info["gpio_sta"]):
        GPIO.output(pin, state)
    os.system(info["i2c_cmd"])
    time.sleep(0.5)
    logging.info(f"Switched to camera {camera_id}")
    return True

def switch_camera_mode(mode):
    """Stop -> configure -> start picam2 with either VIDEO_CONFIG or STILL_CONFIG."""
    global camera_active

    if camera_active:
        picam2.stop()
        camera_active = False
        time.sleep(0.2)

    if mode == 'none':
        return

    if mode == 'video':
        picam2.configure(VIDEO_CONFIG)
    elif mode == 'still':
        picam2.configure(STILL_CONFIG)
    else:
        logging.error(f"Unknown mode: {mode}")
        return

    picam2.start()
    camera_active = True
    time.sleep(0.5)  # sensor settle

def init_camera():
    """Initial setup for camera (once at startup)."""
    global camera_active
    picam2.configure(VIDEO_CONFIG)
    picam2.start()
    camera_active = True
    logging.info("Camera initialized in VIDEO mode.")

def cleanup_camera():
    """Stop camera + close picam2, called on server shutdown."""
    global camera_active
    if camera_active:
        picam2.stop()
        camera_active = False
    picam2.close()
    logging.info("Camera cleaned up.")

def capture_frame(camera_id):
    """Capture a low-res frame in current config (usually for streaming)."""
    with lock:
        if not select_camera(camera_id):
            return None
        try:
            return picam2.capture_array()
        except Exception as e:
            logging.error(f"Error capturing frame from {camera_id}: {e}")
            return None
