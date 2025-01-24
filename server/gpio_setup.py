import RPi.GPIO as GPIO
import logging
from .config import GPIO_PINS

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    for pin in GPIO_PINS:
        GPIO.setup(pin, GPIO.OUT)
    logging.info("GPIO setup complete.")