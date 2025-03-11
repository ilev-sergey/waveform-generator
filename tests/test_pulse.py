from waveform_generator import Pulse


def test_max_voltage_positive():
    pulse = Pulse(amplitude=5.0, duration=10.0, dc_bias=2.0)
    assert pulse.max_voltage == 7.0


def test_max_voltage_negative():
    pulse = Pulse(amplitude=-5.0, duration=10.0, dc_bias=-2.0)
    assert pulse.max_voltage == 7.0


def test_max_voltage_different_signs_1():
    pulse = Pulse(amplitude=2.0, duration=10.0, dc_bias=-5.0)
    assert pulse.max_voltage == 5.0


def test_max_voltage_different_signs_2():
    pulse = Pulse(amplitude=6.0, duration=10.0, dc_bias=-5.0)
    assert pulse.max_voltage == 5.0


def test_max_voltage_different_signs_3():
    pulse = Pulse(amplitude=-5.0, duration=10.0, dc_bias=6.0)
    assert pulse.max_voltage == 6.0


def test_max_voltage_different_signs_4():
    pulse = Pulse(amplitude=-5.0, duration=10.0, dc_bias=2.0)
    assert pulse.max_voltage == 3.0
