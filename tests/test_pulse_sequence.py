import pytest

from waveform_generator import PulseSequence, RectangularPulse, TrapezoidalPulse


@pytest.fixture
def pulse_sequence():
    """A sample fixture that can be used by tests"""
    pulse = RectangularPulse(amplitude=2.0, duration=10.0, delay=0)
    pulse_sequence = PulseSequence(pulses=[pulse])

    yield pulse_sequence


def test_addition(pulse_sequence):
    pulse_sequence += RectangularPulse(amplitude=2.0, duration=10.0, delay=0)
    assert len(pulse_sequence.pulses) == 2
