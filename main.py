#!/usr/bin/env python3
"""
synth.py

Monophonic sine synth controlled by two potentiometers via MCP3008:
 - Pot CH0 -> Frequency (100..2000 Hz)
 - Pot CH1 -> Amplitude (0..0.8)
Audio output via sounddevice (PortAudio). Uses a lookup table for efficiency.
"""

import time
import threading
import numpy as np

# Try imports and give a clear error if missing
try:
    import spidev
except Exception as e:
    raise SystemExit("spidev not installed or SPI not enabled. Install + enable SPI. "
                     "On Debian: sudo apt-get install python3-spidev ; enable SPI with sudo raspi-config.") from e

try:
    import sounddevice as sd
except Exception as e:
    raise SystemExit("sounddevice not installed or PortAudio missing. "
                     "Install PortAudio with: sudo apt-get install portaudio19-dev libportaudio2 libportaudiocpp0 ; "
                     "then pip3 install sounddevice") from e


# -------------------- User parameters --------------------
SAMPLE_RATE = 44100           # audio sample rate
BLOCK_SIZE = 512              # audio block size (lower = more responsive, higher = less CPU)
TABLE_SIZE = 4096             # sine table size (bigger -> smoother)
POLL_HZ = 100                 # how often we read the pots (Hz)
FREQ_MIN = 100.0              # min frequency (Hz)
FREQ_MAX = 2000.0             # max frequency (Hz)
AMP_MAX  = 0.8                # maximum amplitude to avoid clipping
ADC_CHANNEL_FREQ = 5          # MCP3008 channel for frequency pot
ADC_CHANNEL_AMP  = 6          # MCP3008 channel for amplitude pot
# ---------------------------------------------------------

# --- Precompute sine table ---
sine_table = np.sin(2.0 * np.pi * np.arange(TABLE_SIZE) / TABLE_SIZE).astype(np.float32)

# --- Globals updated by ADC thread (smoothed) and read by audio callback ---
_smoothed_freq = 440.0
_smoothed_amp  = 0.2
_running = True

# Smoothing parameters (exponential smoothing)
SMOOTH_TAU = 0.02  # seconds - smoothing time constant; smaller -> faster update
_alpha = None      # computed from POLL_HZ

# --- SPI (MCP3008) setup ---
spi = spidev.SpiDev()
try:
    spi.open(0, 0)               # bus 0, device CE0
    spi.max_speed_hz = 1350000
except FileNotFoundError as e:
    raise SystemExit("SPI device not found. Enable SPI (sudo raspi-config -> Interface Options -> SPI) and reboot.") from e


def read_adc(channel: int) -> int:
    """Read ADC channel 0..7 from MCP3008. Returns 0..1023."""
    if not 0 <= channel <= 7:
        return 0
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) | adc[2]


def adc_to_freq(adc_val: int) -> float:
    """Map ADC 0..1023 to frequency FREQ_MIN..FREQ_MAX (log or linear). Linear here."""
    return FREQ_MIN + (adc_val / 1023.0) * (FREQ_MAX - FREQ_MIN)


def adc_to_amp(adc_val: int) -> float:
    """Map ADC 0..1023 to amplitude 0..AMP_MAX"""
    return (adc_val / 1023.0) * AMP_MAX


def adc_poller():
    """Background thread: polls ADC channels at POLL_HZ and updates smoothed globals."""
    global _smoothed_freq, _smoothed_amp, _running, _alpha

    if _alpha is None:
        dt = 1.0 / POLL_HZ
        # alpha for exponential smoothing: alpha = 1 - exp(-dt/tau)
        _alpha = 1.0 - np.exp(-dt / SMOOTH_TAU)

    while _running:
        try:
            raw_f = read_adc(ADC_CHANNEL_FREQ)
            raw_a = read_adc(ADC_CHANNEL_AMP)
        except Exception:
            # SPI transient error: skip this cycle
            time.sleep(1.0 / POLL_HZ)
            continue

        target_f = adc_to_freq(raw_f)
        target_a = adc_to_amp(raw_a)

        # Exponential smoothing (simple low-pass)
        _smoothed_freq += _alpha * (target_f - _smoothed_freq)
        _smoothed_amp  += _alpha * (target_a - _smoothed_amp)

        time.sleep(1.0 / POLL_HZ)


# --- Audio callback: super lightweight, uses lookup table ---
_phase = 0.0  # fractional phase in table indices (float)

def audio_callback(outdata, frames, time_info, status):
    """
    outdata: (frames, channels) float32 numpy array provided by PortAudio.
    Keep this function extremely fast: no blocking, no I/O.
    """
    global _phase, _smoothed_freq, _smoothed_amp

    # Read current parameters (single memory read - fast)
    freq = _smoothed_freq
    amp  = _smoothed_amp

    # Compute step in table indices per output sample
    step = (freq * TABLE_SIZE) / SAMPLE_RATE  # how many table indices to advance per sample

    # Build index array
    # Use float indices and cast to int for table lookup (fast); fractional interpolation would be nicer but slightly heavier.
    idxs = (_phase + step * np.arange(frames)).astype(np.int64) % TABLE_SIZE
    samples = sine_table[idxs] * amp

    # Write into outdata (mono -> shape (-1,1))
    outdata[:] = samples.reshape(-1, 1)

    # advance phase
    _phase = (_phase + step * frames) % TABLE_SIZE


def main():
    global _running

    print("Starting ADC poller thread...")
    poller = threading.Thread(target=adc_poller, daemon=True)
    poller.start()

    print("Opening audio stream (sample_rate={}, blocksize={})...".format(SAMPLE_RATE, BLOCK_SIZE))
    try:
        with sd.OutputStream(channels=1,
                             samplerate=SAMPLE_RATE,
                             blocksize=BLOCK_SIZE,
                             dtype='float32',
                             callback=audio_callback):
            print("Synth running. Pots: CH0=freq, CH1=amp. Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(0.2)  # main thread idle
            except KeyboardInterrupt:
                print("\nStopping...")
    except Exception as e:
        print("Error opening audio stream or during playback:", e)
    finally:
        _running = False
        time.sleep(0.1)
        try:
            spi.close()
        except Exception:
            pass
        print("Exited cleanly.")


if __name__ == "__main__":
    main()