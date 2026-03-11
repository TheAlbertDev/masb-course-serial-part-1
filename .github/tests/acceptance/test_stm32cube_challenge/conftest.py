import pytest
import time
import subprocess
import serial

SERIAL_PORT_USART2 = "/dev/ttyACM0"   # USB — EVB USART2 (computer side)
SERIAL_PORT_USART1 = "/dev/ttyAMA0"   # RPi GPIO 14 (TX) / GPIO 15 (RX) — EVB USART1
BAUD_RATE = 115200


@pytest.fixture(scope="function")
def setup_hardware():
    """Setup and teardown for STM32Cube serial challenge hardware testing.

    The RPi acts as the second computer: /dev/ttyACM0 connects to the EVB
    USART2 (USB), and /dev/serial0 (GPIO 14/15) connects to EVB USART1.
    """
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

    ser_usart2 = serial.Serial(SERIAL_PORT_USART2, BAUD_RATE, timeout=1)
    ser_usart1 = serial.Serial(SERIAL_PORT_USART1, BAUD_RATE, timeout=1)
    ser_usart2.reset_input_buffer()
    ser_usart1.reset_input_buffer()

    yield ser_usart2, ser_usart1

    # Teardown
    ser_usart2.close()
    ser_usart1.close()
