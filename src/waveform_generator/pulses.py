from dataclasses import dataclass

import numpy as np
from matplotlib import pyplot as plt

from .utils import PointType


@dataclass
class Waveform:
    max_voltage: float
    duration: float
    delay: float = 0.0

    @property
    def total_duration(self):
        return self.delay + self.duration

    def plot(self):
        times, voltages = self.data.values()
        plt.plot(times, voltages)
        plt.title("Waveform Plot")
        plt.xlabel("Time, s")
        plt.ylabel("Voltage, V")
        plt.show()

    def data(self):
        pass

    def to_string(self, point_type=PointType.DECIMAL_INTEGER, max_dac_value=8191):
        if point_type == PointType.DECIMAL_INTEGER:
            voltages_normed = self.data["voltages"] / self.max_voltage
            voltages_int = np.round(voltages_normed * max_dac_value).astype(int)
            voltages_str = [f"{voltage}" for voltage in voltages_int]
            return ",".join(voltages_str)

        if point_type == PointType.FLOATING_POINT:
            voltages_normed = self.data["voltages"] / self.max_voltage
            voltages_str = [f"{voltage:.2f}" for voltage in voltages_normed]
            return ",".join(voltages_str)

        raise NotImplementedError

    @property
    def voltages(self):
        return self.data["voltages"]

    @property
    def times(self):
        return self.data["times"]


class Pulse(Waveform):
    def _calculate_max_voltage(self):
        return max(abs(self.dc_bias + self.amplitude), abs(self.dc_bias))

    def __init__(self, amplitude, duration, delay=0.0, dc_bias=0):
        self.amplitude = amplitude
        self.dc_bias = dc_bias
        max_voltage = self._calculate_max_voltage()
        super().__init__(max_voltage=max_voltage, duration=duration, delay=delay)


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


class TrapezoidalPulse(Pulse):
    def __init__(self, amplitude, pulse_width, delay=0.0, dc_bias=0, rise_time=0.0, fall_time=0.0):
        super().__init__(
            amplitude=amplitude,
            duration=rise_time + pulse_width + fall_time,
            delay=delay,
            dc_bias=dc_bias,
        )
        self.pulse_width = pulse_width
        self.rise_time = rise_time
        self.fall_time = fall_time

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
