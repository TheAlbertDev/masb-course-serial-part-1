import pytest
import time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_bytes(ser, timeout=1.0):
    """Drain all available bytes from ser within timeout seconds."""
    data = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        available = ser.in_waiting
        if available:
            data += ser.read(available)
        else:
            time.sleep(0.01)
    return data


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_output_initially(setup_hardware):
    """No serial output must appear on either port before any data is sent."""
    ser_usart2, ser_usart1 = setup_hardware

    data_usart2 = collect_bytes(ser_usart2, timeout=1.0)
    data_usart1 = collect_bytes(ser_usart1, timeout=1.0)

    assert len(data_usart2) == 0, (
        f"Expected no output on USART2 initially, but received: {data_usart2!r}"
    )
    assert len(data_usart1) == 0, (
        f"Expected no output on USART1 initially, but received: {data_usart1!r}"
    )
    print("No spurious output on either port before data is sent")


def test_byte_forwarded_usart2_to_usart1(setup_hardware):
    """A byte sent via USART2 (USB) must appear on USART1 (GPIO)."""
    ser_usart2, ser_usart1 = setup_hardware

    sent = bytes([0x41])  # 'A'
    ser_usart2.write(sent)

    received = ser_usart1.read(1)
    assert received == sent, (
        f"Expected {sent!r} on USART1 after sending via USART2, got {received!r}"
    )
    print(f"Byte {sent!r} correctly forwarded from USART2 to USART1")


def test_byte_forwarded_usart1_to_usart2(setup_hardware):
    """A byte sent via USART1 (GPIO) must appear on USART2 (USB)."""
    ser_usart2, ser_usart1 = setup_hardware

    sent = bytes([0x42])  # 'B'
    ser_usart1.write(sent)

    received = ser_usart2.read(1)
    assert received == sent, (
        f"Expected {sent!r} on USART2 after sending via USART1, got {received!r}"
    )
    print(f"Byte {sent!r} correctly forwarded from USART1 to USART2")


def test_multibyte_string_usart2_to_usart1(setup_hardware):
    """A multi-byte string sent via USART2 must appear byte-for-byte on USART1."""
    ser_usart2, ser_usart1 = setup_hardware

    sent = b"Hello from USART2\r\n"
    for byte in sent:
        ser_usart2.write(bytes([byte]))
        time.sleep(0.003)

    received = ser_usart1.read(len(sent))
    assert received == sent, (
        f"Expected {sent!r} on USART1, got {received!r}"
    )
    print("Multi-byte string correctly forwarded from USART2 to USART1")


def test_multibyte_string_usart1_to_usart2(setup_hardware):
    """A multi-byte string sent via USART1 must appear byte-for-byte on USART2."""
    ser_usart2, ser_usart1 = setup_hardware

    sent = b"Hello from USART1\r\n"
    for byte in sent:
        ser_usart1.write(bytes([byte]))
        time.sleep(0.003)

    received = ser_usart2.read(len(sent))
    assert received == sent, (
        f"Expected {sent!r} on USART2, got {received!r}"
    )
    print("Multi-byte string correctly forwarded from USART1 to USART2")


def test_no_echo_on_sender(setup_hardware):
    """Bytes sent via USART2 must not echo back on USART2 itself."""
    ser_usart2, ser_usart1 = setup_hardware

    ser_usart2.write(bytes([0x58]))  # 'X'
    ser_usart1.read(1)  # consume the forwarded byte on USART1

    # Check that nothing was echoed back on USART2
    echo = collect_bytes(ser_usart2, timeout=0.5)
    assert len(echo) == 0, (
        f"USART2 unexpectedly echoed {echo!r} back to sender"
    )
    print("No echo observed on USART2 (the sending port)")
