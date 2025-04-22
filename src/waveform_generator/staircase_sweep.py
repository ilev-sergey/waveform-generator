from dataclasses import dataclass, field

import numpy as np

from waveform_generator.waveform import Waveform


@dataclass
class StaircaseSweep(Waveform):
    end_voltage: float
    voltage_step: float
    time_step: float
    edge_time: float = 0.0
    dc_bias: float = 0.0
    start_voltage: float = 0.0

    steps: int = field(init=False)
    duration: float = field(init=False)

    def __post_init__(self):
        self.steps = int((self.end_voltage - self.start_voltage) / self.voltage_step)
        self.duration = (self.steps - 1) * (self.time_step + self.edge_time)

    @property
    def data(self):
        times = []
        voltages = []
        current_voltage = self.start_voltage
        t = self.delay

        time_values = [self.delay, self.edge_time, self.time_step]
        time_values = [val for val in time_values if val != 0]
        min_time = min(time_values)
        steps_per_min_time = 10
        for _ in range(self.steps):
            next_voltage = current_voltage + self.voltage_step

            # Rising edge samples
            num_rise_samples = int(np.ceil(self.edge_time / min_time * steps_per_min_time))
            t_rise = np.linspace(t, t + self.edge_time, num_rise_samples)
            v_rise = np.linspace(current_voltage, next_voltage, num_rise_samples)
            times.extend(t_rise)
            voltages.extend(v_rise)

            t += self.edge_time

            # Constant hold samples
            num_hold_samples = int(np.ceil(self.time_step / min_time * steps_per_min_time))
            t_hold = np.linspace(t, t + self.time_step, num_hold_samples)
            v_hold = [next_voltage] * num_hold_samples
            times.extend(t_hold)
            voltages.extend(v_hold)

            t += self.time_step
            current_voltage = next_voltage

        return {"times": np.array(times), "voltages": np.array(voltages)}
