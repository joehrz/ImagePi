import RPi.GPIO as GPIO
import sys
import os
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    """Load configuration from a JSON file."""
    try:
        with open('params.json', 'r') as file:
            data = json.load(file)
            camera_config = {k: v for k, v in data.items() if k.startswith('camera_') and k[-1] in 'abcd'}
            folder_with_date = data.get("folder_with_date", "")
            plant_name = data.get("plant_name", "")
            the_time = data.get("timestamp", "")
            return camera_config, folder_with_date, plant_name, the_time
    except FileNotFoundError:
        logging.error("The configuration file 'params.json' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("There was an issue decoding 'params.json'.")
        sys.exit(1)

def setup_gpio():
    """Set up GPIO pins for the Raspberry Pi."""
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(11, GPIO.OUT)
    GPIO.setup(12, GPIO.OUT)

def select_camera(camera_id, camera_pins):
    """Select the specified camera using I2C and GPIO."""
    pin_states = camera_pins[camera_id]
    i2c_command = f"sudo i2cset -y 1 0x70 0x00 {pin_states[3]}"
    os.system(i2c_command)
    GPIO.output(7, pin_states[0])
    GPIO.output(11, pin_states[1])
    GPIO.output(12, pin_states[2])
    logging.info(f"Camera {camera_id} selected.")

def capture(camera_id, plant_name, date_str, plant_folder, image_folder):
    """Capture an image with the selected camera."""
    file_name = f"{plant_name}_Camera_{camera_id}_{date_str}.jpg"
    cmd = f"libcamera-still --vflip -n -o /home/imagepi/Images/{plant_folder}/{image_folder}/{file_name}"
    os.system(cmd)
    logging.info(f"Captured image with Camera {camera_id}: {file_name}")

def run_cameras(config, plant_name, date_str, plant_folder, image_folder):
    """Run enabled cameras based on the configuration."""
    camera_pins = {
        "A": (False, False, True, "0x04"),
        "B": (True, False, True, "0x05"),
        "C": (False, True, False, "0x06"),
        "D": (True, True, False, "0x07"),
    }
    
    for cam_key, enabled in config.items():
        camera_id = cam_key[-1].upper()  # Assumes key format 'camera_x'
        if enabled:  # Only proceed if camera is enabled
            select_camera(camera_id, camera_pins)
            capture(camera_id, plant_name, date_str, plant_folder, image_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python script.py <image_folder>")
        sys.exit(1)
    
    image_folder = sys.argv[1]
    camera_config, folder_with_date, plant_name, the_time = load_config()
    setup_gpio()
    plant_folder = folder_with_date.rsplit('/', 1)[-1] if folder_with_date else 'default_folder'

    match = re.search(r'\d{4}-\d{2}-\d{2}', the_time)
    date_str = match.group(0) if match else 'unknown_date'
    
    run_cameras(camera_config, plant_name, date_str, plant_folder, image_folder)

    # Reset GPIO pins to a safe state
    GPIO.output(7, False)
    GPIO.output(11, False)
    GPIO.output(12, True)
    GPIO.cleanup()
    logging.info("GPIO cleanup done. Script completed.")
