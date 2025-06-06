from dataclasses import dataclass, field, fields

import numpy as np
from matplotlib import pyplot as plt

from waveform_generator.utils import PointType


@dataclass
class Waveform:
    duration: float
    delay: float = field(default=0.0, kw_only=True)

    def __neg__(self):
        kwargs = {f.name: getattr(self, f.name) for f in fields(self) if f.init}
        for name in self._voltage_fields():
            kwargs[name] = -kwargs[name]
        return self.__class__(**kwargs)

    def _voltage_fields(self):
        return []

    @property
    def total_duration(self):
        return self.delay + self.duration

    @property
    def max_voltage(self):
        return np.max(np.abs(self.voltages))

    def plot(self, trigger=False):
        times, voltages = self.data.values()
        plt.plot(times, voltages)
        if trigger:
            plt.step(times, self.trigger, label="Trigger", linestyle="--")
        plt.title("Waveform Plot")
        plt.xlabel("Time, s")
        plt.ylabel("Voltage, V")
        plt.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))

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

    def to_vectors(self):
        raise NotImplementedError(f"to_vectors method is not implemented for {self.__class__.__name__}")

    @property
    def voltages(self):
        return self.data["voltages"]

    @property
    def times(self):
        return self.data["times"]

    @property
    def trigger(self, amplitude=1.0):
        trigger = np.zeros_like(self.voltages)

        slope = np.gradient(self.voltages, self.times)
        flat_threshold = 1e-5
        is_flat = np.abs(slope) < flat_threshold

        trigger[1:] = is_flat[1:] & ~is_flat[:-1]

        return trigger * amplitude
