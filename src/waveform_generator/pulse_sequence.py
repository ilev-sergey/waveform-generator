import numpy as np

from .pulses import Waveform


class PulseSequence(Waveform):
    def _calculate_max_voltage(self):
        max_voltage = np.max([pulse.max_voltage for pulse in self.pulses])
        return max(abs(self.dc_bias + max_voltage), abs(self.dc_bias))

    def __init__(self, pulses, dc_bias=0, cycles=1, sample_rate=1):
        self.pulses = pulses
        self.dc_bias = dc_bias
        self.cycles = cycles
        self.sample_rate = sample_rate

        max_voltage = self._calculate_max_voltage()
        super().__init__(
            max_voltage=max_voltage,
            delay=pulses[0].delay,
            duration=sum([pulse.duration for pulse in pulses]),
        )

    def __iadd__(self, other):
        self.pulses.append(other)
        return self

    def to_array(self):
        times, voltages = self.pulses[0].to_array()
        for pulse in self.pulses[1:]:
            pulse_times, pulse_voltages = pulse.to_array()
            pulse_times += times[-1]
            times = np.concatenate([times, pulse_times])
            voltages = np.concatenate([voltages, pulse_voltages])

        return times, voltages
