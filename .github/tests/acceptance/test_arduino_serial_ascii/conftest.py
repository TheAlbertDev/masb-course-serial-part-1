import pytest
import time
import subprocess
import RPi.GPIO as GPIO
import serial

BUTTON_GPIO = 27    # RPi GPIO output wired to Nucleo button (pin 23)
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


def press_button():
    """Simulate a button press on BUTTON_GPIO (active-low, falling edge)."""
    GPIO.output(BUTTON_GPIO, GPIO.LOW)
    time.sleep(0.15)
    GPIO.output(BUTTON_GPIO, GPIO.HIGH)
    time.sleep(0.2)


@pytest.fixture(scope="function")
def setup_hardware():
    """Setup and teardown for serial ASCII hardware testing."""
    GPIO.setwarnings(False)
    try:
        GPIO.setmode(GPIO.BCM)
    except Exception:
        pass

    GPIO.setup(BUTTON_GPIO, GPIO.OUT, initial=GPIO.HIGH)  # button not pressed

    # Reset the MCU so the program starts from scratch
    subprocess.run(
        [
            "pio",
            "pkg",
            "exec",
            "-p",
            "tool-openocd",
            "-c",
            "openocd -f interface/stlink.cfg -f target/stm32f4x.cfg"
            " -c 'init; reset run; shutdown'",
        ],
        check=True,
    )
    time.sleep(0.5)  # Wait for MCU to initialize

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()

    yield ser

    # Teardown
    GPIO.output(BUTTON_GPIO, GPIO.HIGH)
    ser.close()
    GPIO.cleanup()
