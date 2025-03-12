from dataclasses import dataclass

import numpy as np


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
    def to_array(self):
        sample_rate = 1000  # points/s

        total_time = self.delay + self.duration

        # Create time array
        num_points = int(total_time * sample_rate) + 1
        time_array = np.linspace(0, total_time, num_points)

        # Initialize voltage array with DC bias
        voltage_array = np.ones_like(time_array) * self.dc_bias

        # Set pulse region (delay to delay+duration) to DC bias + amplitude
        pulse_start_idx = int(self.delay * sample_rate)
        pulse_end_idx = int((self.delay + self.duration) * sample_rate)
        pulse_end_idx = min(pulse_end_idx, len(voltage_array) - 1)

        voltage_array[pulse_start_idx : pulse_end_idx + 1] = (
            self.dc_bias + self.amplitude
        )

        values = (time_array, voltage_array)
        return values


class TrapezoidalPulse(Pulse):
    pass
