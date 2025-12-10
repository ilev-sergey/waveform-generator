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

    def __mul__(self, other):
        kwargs = {f.name: getattr(self, f.name) for f in fields(self) if f.init}
        for name in self._voltage_fields():
            kwargs[name] = kwargs[name] * other
        return self.__class__(**kwargs)

    def __rmul__(self, other):
        return self.__mul__(other)

    def _voltage_fields(self):
        return []

    @property
    def total_duration(self):
        return self.delay + self.duration

    @property
    def max_voltage(self):
        return np.max(np.abs(self.voltages))

    def plot(self, trigger=False, ax=None):
        if ax is None:
            ax = plt.gca()
        times, voltages = self.data.values()
        ax.plot(times, voltages)
        if trigger:
            ax.step(times, self.trigger, label="Trigger", linestyle="--")
        ax.set_title("Waveform Plot")
        ax.set_xlabel("Time, s")
        ax.set_ylabel("Voltage, V")
        ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))

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
