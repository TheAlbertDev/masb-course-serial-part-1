import pytest


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_echo_single_byte(setup_hardware):
    """Microcontroller must echo back a single sent byte."""
    ser = setup_hardware

    sent = bytes([0x42])
    ser.write(sent)
    received = ser.read(1)

    assert received == sent, (
        f"Expected echo of {sent!r}, got {received!r}"
    )
    print(f"✓ Single byte 0x42 echoed correctly")


def test_echo_multiple_bytes(setup_hardware):
    """Microcontroller must echo back all bytes of a multi-byte sequence."""
    ser = setup_hardware

    sent = bytes([0x01, 0x42, 0xFF, 0xA5])
    ser.write(sent)
    received = ser.read(len(sent))

    assert received == sent, (
        f"Expected echo of {sent!r}, got {received!r}"
    )
    print(f"✓ Multi-byte sequence echoed correctly: {sent!r}")


def test_echo_boundary_values(setup_hardware):
    """Microcontroller must correctly echo boundary byte values."""
    ser = setup_hardware

    boundary_values = [0x00, 0x7F, 0x80, 0xFF]
    for val in boundary_values:
        ser.reset_input_buffer()
        sent = bytes([val])
        ser.write(sent)
        received = ser.read(1)
        assert received == sent, (
            f"Echo failed for 0x{val:02X}: expected {sent!r}, got {received!r}"
        )
        print(f"✓ Boundary value 0x{val:02X} echoed correctly")
