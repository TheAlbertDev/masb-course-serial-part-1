import pytest
import time
import subprocess
import serial

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


@pytest.fixture(scope="function")
def setup_hardware():
    """Setup and teardown for serial LED hardware testing."""
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
    ser.close()
