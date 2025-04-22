from dataclasses import dataclass, field

import numpy as np

from waveform_generator.waveform import Waveform


@dataclass
class Pulse(Waveform):
    amplitude: float
    dc_bias: float = field(default=0.0, kw_only=True)

    def __post_init__(self):
        super().__init__(duration=self.duration, delay=self.delay)

    def __init__(self, amplitude, duration, delay=0.0, dc_bias=0):
        self.amplitude = amplitude
        self.dc_bias = dc_bias
        super().__init__(duration=duration, delay=delay)


class RectangularPulse(Pulse):
    @property
    def data(self):
        steps_per_min_time = 10
        sample_rate = steps_per_min_time * int(1 / self.duration)  # points/s

        # Create time array
        num_points = int(self.total_duration * sample_rate) + 1
        time_array = np.linspace(0, self.total_duration, num_points)

        # Initialize voltage array with DC bias
        voltage_array = np.ones_like(time_array) * self.dc_bias

        # Set pulse region (delay to delay+duration) to DC bias + amplitude
        pulse_start_idx = int(self.delay * sample_rate)
        pulse_end_idx = int(self.total_duration * sample_rate)
        pulse_end_idx = min(pulse_end_idx, len(voltage_array) - 1)

        voltage_array[pulse_start_idx : pulse_end_idx + 1] = self.dc_bias + self.amplitude

        return {"times": time_array, "voltages": voltage_array}


@dataclass
class TrapezoidalPulse(Pulse):
    pulse_width: float
    rise_time: float = 0.0
    fall_time: float = 0.0
    duration: float = field(init=False)

    def __post_init__(self):
        self.duration = self.rise_time + self.pulse_width + self.fall_time
        super().__post_init__()

    @property
    def data(self):
        time_values = [t for t in [self.delay, self.rise_time, self.pulse_width, self.fall_time] if t != 0]
        min_time = min(time_values)
        steps_per_min_time = 10
        sample_rate = steps_per_min_time * int(1 / min_time)  # points/s

        # Create time array
        num_points = int(self.total_duration * sample_rate) + 1
        time_array = np.linspace(0, self.total_duration, num_points)

        # Initialize voltage array with DC bias
        voltage_array = np.ones_like(time_array) * self.dc_bias

        pulse_start_rise_idx = int(self.delay * sample_rate)
        pulse_end_rise_idx = int((self.delay + self.rise_time) * sample_rate)
        pulse_start_fall_idx = int((self.delay + self.rise_time + self.pulse_width) * sample_rate)
        pulse_end_fall_idx = int((self.delay + self.rise_time + self.pulse_width + self.fall_time) * sample_rate)
        pulse_end_fall_idx = min(pulse_end_fall_idx, len(voltage_array) - 1)

        voltage_array[pulse_start_rise_idx : pulse_end_rise_idx + 1] = np.linspace(
            self.dc_bias,
            self.dc_bias + self.amplitude,
            pulse_end_rise_idx - pulse_start_rise_idx + 1,
        )
        voltage_array[pulse_end_rise_idx : pulse_start_fall_idx + 1] = self.dc_bias + self.amplitude
        voltage_array[pulse_start_fall_idx : pulse_end_fall_idx + 1] = np.linspace(
            self.dc_bias + self.amplitude,
            self.dc_bias,
            pulse_end_fall_idx - pulse_start_fall_idx + 1,
        )

        return {"times": time_array, "voltages": voltage_array}
