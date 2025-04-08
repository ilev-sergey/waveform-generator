from dataclasses import dataclass

import numpy as np
from matplotlib import pyplot as plt


@dataclass
class Waveform:
    max_voltage: float
    duration: float
    delay: float = 0.0

    def plot(self):
        times, voltages = self.to_array()
        plt.plot(times, voltages)
        plt.title("Waveform Plot")
        plt.xlabel("Time, s")
        plt.ylabel("Voltage, V")
        plt.show()

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
        steps_per_min_time = 10
        sample_rate = steps_per_min_time * int(1 / self.duration)  # points/s

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

        voltage_array[pulse_start_idx : pulse_end_idx + 1] = self.dc_bias + self.amplitude

        return (time_array, voltage_array)


class TrapezoidalPulse(Pulse):
    def __init__(self, amplitude, duration, delay=0.0, dc_bias=0, rise_time=0.0, fall_time=0.0):
        super().__init__(amplitude, duration, delay, dc_bias)
        self.rise_time = rise_time
        self.fall_time = fall_time

    def to_array(self):
        time_values = [t for t in [self.delay, self.rise_time, self.duration, self.fall_time] if t != 0]
        min_time = min(time_values)
        steps_per_min_time = 10
        sample_rate = steps_per_min_time * int(1 / min_time)  # points/s

        total_time = self.delay + self.rise_time + self.duration + self.fall_time

        # Create time array
        num_points = int(total_time * sample_rate) + 1
        time_array = np.linspace(0, total_time, num_points)

        # Initialize voltage array with DC bias
        voltage_array = np.ones_like(time_array) * self.dc_bias

        pulse_start_rise_idx = int(self.delay * sample_rate)
        pulse_end_rise_idx = int((self.delay + self.rise_time) * sample_rate)
        pulse_start_fall_idx = int((self.delay + self.rise_time + self.duration) * sample_rate)
        pulse_end_fall_idx = int((self.delay + self.rise_time + self.duration + self.fall_time) * sample_rate)
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

        return (time_array, voltage_array)
