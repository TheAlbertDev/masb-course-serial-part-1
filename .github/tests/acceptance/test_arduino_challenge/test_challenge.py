import pytest
import time
import math
import threading
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conftest import write_dac, sinus_dac_code, DAC_A0_ADDR

ARTIFACTS_DIR = "../../../../artifacts"

# Voltage references — DAC outputs 0–2.5 V, Nucleo ADC reference is 3.3 V
DAC_VREF = 2.5
ADC_VREF = 3.3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_raw_bytes_timed(ser, duration):
    """Collect all raw bytes received during *duration* seconds.

    Returns a list of dicts:
        {'byte': int, 'ts': float}
    """
    ser.reset_input_buffer()
    entries = []
    start = time.time()
    while time.time() - start < duration:
        available = ser.in_waiting
        if available:
            chunk = ser.read(available)
            ts = time.time() - start
            for b in chunk:
                entries.append({"byte": b, "ts": ts})
        else:
            time.sleep(0.005)
    return entries


def parse_adc_samples(entries):
    """Parse a list of byte entries into 10-bit ADC samples (LSB first, MSB second).

    Returns a list of dicts:
        {'value': int, 'ts': float}
    where ts is the timestamp of the second (MSB) byte.
    """
    samples = []
    i = 0
    while i + 1 < len(entries):
        lsb = entries[i]["byte"]
        msb = entries[i + 1]["byte"]
        value = lsb | (msb << 8)
        ts = entries[i + 1]["ts"]
        samples.append({"value": value, "ts": ts})
        i += 2
    return samples


def dac_to_adc_expected(t, freq=0.1, phase=0.0, amplitude=0.4, offset=0.5):
    """Expected ADC count (0–1023) for a given elapsed time t.

    DAC outputs 0–2.5 V (internal VREF); Nucleo ADC reference is 3.3 V.
    ADC = (Vdac / ADC_VREF) * 1023
    """
    v = offset + amplitude * math.sin(2 * math.pi * freq * t + phase)
    v = max(0.0, min(1.0, v))
    return int(v * (DAC_VREF / ADC_VREF) * 1023)


def pearson_r(x, y):
    """Compute Pearson correlation coefficient between two arrays."""
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    if len(x) < 2:
        return 0.0
    xm = x - x.mean()
    ym = y - y.mean()
    denom = np.sqrt((xm**2).sum() * (ym**2).sum())
    return float(np.dot(xm, ym) / denom) if denom > 0 else 0.0


def save_comparison_chart(ts, received, t0_offset, filename):
    """Save a two-panel comparison chart (received ADC vs expected sinus)."""
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    expected = [dac_to_adc_expected(t + t0_offset) for t in ts]

    if ts:
        t_plot = np.linspace(0, max(ts), 500)
        exp_curve = [dac_to_adc_expected(t + t0_offset) for t in t_plot]
    else:
        t_plot, exp_curve = [], []

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    axes[0].plot(t_plot, exp_curve, "b-", linewidth=1.5, alpha=0.7,
                 label="Expected (generated sinus)")
    axes[0].scatter(ts, received, c="orange", s=20, zorder=5,
                    label="Received ADC (serial raw)")
    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("ADC counts (0–1023)")
    axes[0].set_title("Serial Challenge: Generated Sinus vs Received ADC")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    residual = [r - e for r, e in zip(received, expected)]
    axes[1].plot(ts, residual, "g-", linewidth=0.8)
    axes[1].axhspan(-50, 50, color="grey", alpha=0.2, label="±50 ADC count band")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Residual (ADC counts)")
    axes[1].set_title("Residual (Received − Expected)")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(ARTIFACTS_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved chart: {path}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_output_initially(setup_hardware):
    """No bytes must appear on serial before any command is sent."""
    _, ser = setup_hardware
    entries = collect_raw_bytes_timed(ser, 2.0)
    assert len(entries) == 0, (
        f"Expected no output initially, but received {len(entries)} bytes"
    )
    print("✓ No output received before sending any command")


def test_status_ok_on_start_command(setup_hardware):
    """Sending 0x01 must return status 0x00 (no error)."""
    _, ser = setup_hardware

    ser.write(bytes([0x01]))
    response = ser.read(1)

    assert response == bytes([0x00]), (
        f"Expected 0x00 status for 0x01 command, got {response!r}"
    )
    print("✓ Start command (0x01) returned 0x00 (no error)")


def test_adc_starts_after_start_command(setup_hardware):
    """After sending 0x01, ADC samples (2-byte raw) must appear on serial."""
    _, ser = setup_hardware

    ser.write(bytes([0x01]))
    ser.read(1)  # consume status byte 0x00

    # Collect for 5 s — expect at least 3 samples (6 bytes) at ~1 s interval
    entries = collect_raw_bytes_timed(ser, 5.0)

    assert len(entries) >= 6, (
        f"Expected ≥6 bytes (≥3 ADC samples) after start command, got {len(entries)}"
    )
    print(f"✓ Received {len(entries)} bytes ({len(entries) // 2} ADC samples) after 0x01 command")


def test_sampling_rate_approx_1s(setup_hardware):
    """ADC sampling rate must be approximately 1 s (±200 ms tolerance)."""
    _, ser = setup_hardware

    ser.write(bytes([0x01]))
    ser.read(1)  # consume status byte 0x00

    # Collect for 8 s to gather enough samples for interval analysis
    entries = collect_raw_bytes_timed(ser, 8.0)
    samples = parse_adc_samples(entries)

    assert len(samples) >= 4, (
        f"Too few ADC samples ({len(samples)}) to compute sampling interval"
    )

    intervals = [samples[i]["ts"] - samples[i - 1]["ts"] for i in range(1, len(samples))]
    median_interval = float(np.median(intervals))
    print(f"Sampling interval: median={median_interval * 1000:.1f} ms "
          f"(from {len(intervals)} intervals)")

    assert 0.80 <= median_interval <= 1.20, (
        f"Sampling interval {median_interval * 1000:.1f} ms is outside 800–1200 ms range"
    )
    print("✓ Sampling rate is approximately 1 s")


def test_adc_values_in_range(setup_hardware):
    """All received ADC values must be within the 10-bit range (0–1023)."""
    _, ser = setup_hardware

    ser.write(bytes([0x01]))
    ser.read(1)  # consume status byte 0x00

    entries = collect_raw_bytes_timed(ser, 4.0)
    samples = parse_adc_samples(entries)

    assert len(samples) >= 2, (
        f"Too few ADC samples ({len(samples)}) for range validation"
    )

    for s in samples:
        assert 0 <= s["value"] <= 1023, (
            f"ADC value {s['value']} is outside valid 10-bit range (0–1023)"
        )
    print(f"✓ All {len(samples)} ADC values are within 0–1023 range")


def test_invalid_command_returns_error(setup_hardware):
    """Sending an unknown command must return 0x01 (error)."""
    _, ser = setup_hardware

    ser.write(bytes([0x03]))
    response = ser.read(1)

    assert response == bytes([0x01]), (
        f"Expected 0x01 error for unknown command 0x03, got {response!r}"
    )
    print("✓ Unknown command 0x03 returned 0x01 (error)")


def test_adc_stops_after_stop_command(setup_hardware):
    """Sending 0x02 must stop ADC output and return 0x00 (no error)."""
    _, ser = setup_hardware

    # Start ADC conversion
    ser.write(bytes([0x01]))
    assert ser.read(1) == bytes([0x00]), "Start command did not return 0x00"

    # Wait to confirm ADC is running
    time.sleep(2.0)

    # Stop ADC conversion
    ser.write(bytes([0x02]))
    status = ser.read(1)
    assert status == bytes([0x00]), (
        f"Expected 0x00 status for stop command (0x02), got {status!r}"
    )

    # Flush any residual bytes still in transit
    time.sleep(0.5)
    ser.reset_input_buffer()

    # Collect for 2 s — should receive no further bytes
    entries = collect_raw_bytes_timed(ser, 2.0)
    assert len(entries) == 0, (
        f"Expected no output after stop command, but received {len(entries)} bytes"
    )
    print("✓ ADC output stopped after 0x02 command")


def test_adc_tracks_sinus_signal(setup_hardware):
    """ADC must track a 0.1 Hz sinus generated on DAC A0 after 0x01 command."""
    bus, ser = setup_hardware

    stop_flag = threading.Event()
    t0 = time.time()

    def dac_loop():
        while not stop_flag.is_set():
            code = sinus_dac_code(time.time() - t0)
            write_dac(bus, DAC_A0_ADDR, code)

    # Start DAC thread before enabling ADC so A0 already carries the sinus signal
    thread = threading.Thread(target=dac_loop, daemon=True)
    thread.start()
    time.sleep(0.05)  # let at least one I2C write complete before enabling ADC

    ser.write(bytes([0x01]))
    ser.read(1)  # consume status byte 0x00

    # Collect for 15 s — at 0.1 Hz sinus, this covers 1.5 full cycles
    collection_start = time.time()
    entries = collect_raw_bytes_timed(ser, 15.0)

    stop_flag.set()
    thread.join(timeout=1.0)

    samples = parse_adc_samples(entries)
    assert len(samples) >= 8, (
        f"Too few ADC samples ({len(samples)}) for correlation analysis"
    )

    # Timestamps relative to collection_start; sinus time = ts + (collection_start - t0)
    offset = collection_start - t0
    ts = [s["ts"] for s in samples]
    received = [s["value"] for s in samples]
    expected = [dac_to_adc_expected(t + offset) for t in ts]

    r = pearson_r(received, expected)
    print(f"ADC Pearson R = {r:.3f} ({len(samples)} samples)")

    save_comparison_chart(ts, received, offset, "serial_challenge_comparison.png")

    assert r > 0.85, (
        f"ADC does not track sinus signal (Pearson R = {r:.3f}, need > 0.85)"
    )
    print("✓ ADC correctly tracks generated sinus signal")
