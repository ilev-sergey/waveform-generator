import numpy as np

from waveform_generator.waveform import Waveform


class PulseSequence(Waveform):
    def __init__(self, pulses, dc_bias=0, cycles=1, sample_rate=1):
        self.pulses = pulses
        self.dc_bias = dc_bias
        self.cycles = cycles
        self.sample_rate = sample_rate

        super().__init__(
            delay=pulses[0].delay,
            duration=sum([pulse.delay + pulse.duration for pulse in pulses]) - pulses[0].delay,
        )

    def __iadd__(self, other):
        self.pulses.append(other)
        return self

    def __neg__(self):
        return self.__class__(
            pulses=[-pulse for pulse in self.pulses],
            dc_bias=-self.dc_bias,
            cycles=self.cycles,
            sample_rate=self.sample_rate,
        )

    @property
    def data(self):
        times, voltages = self.pulses[0].data.values()
        for pulse in self.pulses[1:]:
            pulse_times, pulse_voltages = pulse.data.values()
            pulse_times += times[-1]
            times = np.concatenate([times, pulse_times])
            voltages = np.concatenate([voltages, pulse_voltages])

        return {"times": times, "voltages": voltages}
