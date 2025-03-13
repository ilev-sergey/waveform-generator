import pytest

from waveform_generator import Pulse


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
    pulse = Pulse(amplitude=amplitude, duration=1.0, dc_bias=dc_bias)
    assert pulse.max_voltage == expected_max
