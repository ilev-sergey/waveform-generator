import pytest

from waveform_generator import TrapezoidalPulse


@pytest.mark.parametrize(
    "amplitude, dc_bias, expected_max",
    [
        (5.0, 2.0, 7.0),
        (-5.0, -2.0, 7.0),
        (2.0, -5.0, 5.0),
        (6.0, -5.0, 5.0),
        (-5.0, 6.0, 6.0),
        (-5.0, 2.0, 3.0),
    ],
)
def test_max_voltage(amplitude, dc_bias, expected_max):
    pulse = TrapezoidalPulse(amplitude=amplitude, dc_bias=dc_bias, pulse_width=1, rise_time=0.1, fall_time=0.1)
    assert pulse.max_voltage == expected_max
