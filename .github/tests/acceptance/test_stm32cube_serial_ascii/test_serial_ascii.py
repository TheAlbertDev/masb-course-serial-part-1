import pytest
import time

from conftest import press_button

EXPECTED_MESSAGE = b"Hello, I am STM32.\r\n"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_output_initially(setup_hardware):
    """No serial output must appear before any button press."""
    ser = setup_hardware
    data = b""
    start = time.time()
    while time.time() - start < 2.0:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            data += chunk
    assert len(data) == 0, (
        f"Expected no serial output initially, but received: {data!r}"
    )
    print("No output received before button press")


def test_hello_on_button_press(setup_hardware):
    """Pressing the button must send 'Hello, I am STM32.\\r\\n' via serial."""
    ser = setup_hardware

    print("Pressing button...")
    press_button()

    line = ser.readline()
    assert line == EXPECTED_MESSAGE, (
        f"Expected {EXPECTED_MESSAGE!r}, got {line!r}"
    )
    print(f"Received correct message: {line!r}")


def test_multiple_presses_produce_multiple_messages(setup_hardware):
    """Each button press must generate exactly one message."""
    ser = setup_hardware
    n_presses = 3

    for _ in range(n_presses):
        press_button()

    messages = []
    for _ in range(n_presses):
        line = ser.readline()
        messages.append(line)

    assert len(messages) == n_presses, (
        f"Expected {n_presses} messages, got {len(messages)}"
    )
    for i, msg in enumerate(messages):
        assert msg == EXPECTED_MESSAGE, (
            f"Message {i + 1} mismatch: expected {EXPECTED_MESSAGE!r}, got {msg!r}"
        )
    print(f"Received {n_presses} correct messages, one per button press")
