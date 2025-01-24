import logging
import os
import RPi.GPIO as GPIO
from picamera2 import Picamera2

logging.basicConfig(level=logging.DEBUG)

# Multiplexer camera info
ADAPTER_INFO = {
    "a": {"i2c_cmd": "i2cset -y 10 0x70 0x00 0x04", "gpio_sta": [0, 0, 1]},
    "b": {"i2c_cmd": "i2cset -y 10 0x70 0x00 0x05", "gpio_sta": [1, 0, 1]},
    "c": {"i2c_cmd": "i2cset -y 10 0x70 0x00 0x06", "gpio_sta": [0, 1, 0]},
    "d": {"i2c_cmd": "i2cset -y 10 0x70 0x00 0x07", "gpio_sta": [1, 1, 0]},
}

GPIO_PINS = [7, 11, 12]

# Picamera2 instance
picam2 = Picamera2()

# Create separate configs for video and still
VIDEO_CONFIG = picam2.create_video_configuration(
    main={"size": (320, 240), "format": "BGR888"}, buffer_count=6
)
STILL_CONFIG = picam2.create_still_configuration(
    main={"size": (4056, 3040), "format": "BGR888"}, buffer_count=1
)