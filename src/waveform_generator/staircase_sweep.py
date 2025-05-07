from dataclasses import dataclass, field

import numpy as np

from waveform_generator.waveform import Waveform


@dataclass
class StaircaseSweep(Waveform):
    end_voltage: float
    time_step: float
    steps: int = None
    start_voltage: float = 0.0
    edge_time: float = 0.0
    voltage_step: float = None
    dc_bias: float = 0.0

    duration: float = field(init=False)

    def __post_init__(self):
        self._validate_steps()

        if self.voltage_step is None:
            self.voltage_step = self._calculate_voltage_step_from_steps()

        elif self.steps is None:
            steps_calculated = (self.end_voltage - self.start_voltage) / self.voltage_step
            if not np.isclose(steps_calculated, round(steps_calculated), rtol=1e-3):
                raise ValueError(
                    f"The difference between end_voltage and start_voltage ({self.end_voltage - self.start_voltage}) "
                    f"is not divisible by voltage_step ({self.voltage_step}). This is not supported as it can lead to unexpected waveform. "
                    f"Consider using steps instead."
                )
            self.steps = int((self.end_voltage - self.start_voltage) / self.voltage_step)

        self.duration = (self.steps - 1) * (self.time_step + self.edge_time)

    def _validate_steps(self):
        if self.voltage_step is None and self.steps is None:
            raise ValueError("One of 'voltage_step' or 'steps' must be provided")

        if self.voltage_step is not None and self.steps is not None:
            calculated_step = self._calculate_voltage_step_from_steps()
            if not np.isclose(abs(self.voltage_step), abs(calculated_step), rtol=1e-3):
                raise ValueError(
                    f"Both 'voltage_step' and 'steps' are provided, but they are inconsistent, use only one of them.\n"
                    f"Calculated voltage step: {calculated_step:.3f}, provided voltage step: {self.voltage_step}"
                )

    def _calculate_voltage_step_from_steps(self):
        return (self.end_voltage - self.start_voltage) / (self.steps)

    def _voltage_fields(self):
        return super()._voltage_fields() + [
            "start_voltage",
            "end_voltage",
            "voltage_step",
            "dc_bias",
        ]

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

        return {"times": np.array(times), "voltages": np.array(voltages) + self.dc_bias}
