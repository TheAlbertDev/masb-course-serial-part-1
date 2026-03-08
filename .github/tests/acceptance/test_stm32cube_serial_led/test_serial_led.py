import pytest


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_led_on_command(setup_hardware):
    """Sending 0x01 must turn the LED on and return 0x00 (no error)."""
    ser = setup_hardware

    ser.write(bytes([0x01]))
    response = ser.read(1)

    assert response == bytes([0x00]), (
        f"Expected 0x00 response for LED ON command, got {response!r}"
    )
    print("LED ON command returned 0x00 (no error)")


def test_led_off_command(setup_hardware):
    """Sending 0x02 must turn the LED off and return 0x00 (no error)."""
    ser = setup_hardware

    ser.write(bytes([0x02]))
    response = ser.read(1)

    assert response == bytes([0x00]), (
        f"Expected 0x00 response for LED OFF command, got {response!r}"
    )
    print("LED OFF command returned 0x00 (no error)")


def test_invalid_command_returns_error(setup_hardware):
    """Sending an unknown command must return 0x01 (error)."""
    ser = setup_hardware

    for cmd in [0x00, 0x03, 0xFF]:
        ser.reset_input_buffer()
        ser.write(bytes([cmd]))
        response = ser.read(1)
        assert response == bytes([0x01]), (
            f"Expected 0x01 error for unknown command 0x{cmd:02X}, got {response!r}"
        )
        print(f"Unknown command 0x{cmd:02X} returned 0x01 (error)")


def test_led_on_off_sequence(setup_hardware):
    """LED ON/OFF sequence must each return 0x00 (no error)."""
    ser = setup_hardware

    # Turn on
    ser.write(bytes([0x01]))
    assert ser.read(1) == bytes([0x00]), "LED ON: expected 0x00 response"

    # Turn off
    ser.write(bytes([0x02]))
    assert ser.read(1) == bytes([0x00]), "LED OFF: expected 0x00 response"

    # Turn on again
    ser.write(bytes([0x01]))
    assert ser.read(1) == bytes([0x00]), "LED ON again: expected 0x00 response"

    print("LED ON/OFF/ON sequence all returned 0x00 (no error)")
