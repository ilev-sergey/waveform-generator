from dataclasses import dataclass


@dataclass
class Waveform:
    max_voltage: float
    duration: float
    delay: float = 0.0

    def plot(self):
        pass

    def to_array(self):
        pass

    def to_string(self):
        pass


class Pulse(Waveform):
    def _calculate_max_voltage(self):
        return max(abs(self.dc_bias + self.amplitude), abs(self.dc_bias))

    def __init__(self, amplitude, duration, delay=0.0, dc_bias=0):
        self.amplitude = amplitude
        self.dc_bias = dc_bias
        max_voltage = self._calculate_max_voltage()
        super().__init__(max_voltage=max_voltage, duration=duration, delay=delay)


class RectangularPulse(Pulse):
    pass


class TrapezoidalPulse(Pulse):
    pass
