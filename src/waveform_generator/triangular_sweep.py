from dataclasses import dataclass, field

import numpy as np

from waveform_generator.staircase_sweep import StaircaseSweep
from waveform_generator.waveform import Waveform


@dataclass
class TriangularSweep(Waveform):
    end_voltage: float
    time_step: float
    steps: int = None
    start_voltage: float = 0.0
    edge_time: float = 0.0
    voltage_step: float = None
    dc_bias: float = 0.0

    duration: float = field(init=False)

    def __post_init__(self):
        if self.steps is not None and self.steps % 2 != 0:
            raise ValueError(f"'steps' must be even for TriangularSweep, got {self.steps}")

        half_steps = self.steps // 2 if self.steps is not None else None

        self.up_sweep = StaircaseSweep(
            start_voltage=self.start_voltage,
            end_voltage=self.end_voltage,
            time_step=self.time_step,
            steps=half_steps,
            edge_time=self.edge_time,
            voltage_step=self.voltage_step,
            dc_bias=self.dc_bias,
            delay=self.delay,
        )
        self.down_sweep = StaircaseSweep(
            start_voltage=self.end_voltage,
            end_voltage=self.start_voltage,
            time_step=self.time_step,
            steps=self.up_sweep.steps,
            edge_time=self.edge_time,
            voltage_step=-self.up_sweep.voltage_step,
            dc_bias=self.dc_bias,
        )

        self.steps = 2 * self.up_sweep.steps
        self.voltage_step = self.up_sweep.voltage_step
        self.duration = self.up_sweep.duration + self.down_sweep.duration

    def _voltage_fields(self):
        return super()._voltage_fields() + [
            "start_voltage",
            "end_voltage",
            "voltage_step",
            "dc_bias",
        ]

    @property
    def data(self):
        up_times, up_voltages = self.up_sweep.data.values()
        down_times, down_voltages = self.down_sweep.data.values()

        down_times = down_times + up_times[-1]

        times = np.concatenate([up_times, down_times])
        voltages = np.concatenate([up_voltages, down_voltages])

        return {"times": times, "voltages": voltages}

    def to_vectors(self):
        up_times, up_voltages = self.up_sweep.to_vectors()
        down_times, down_voltages = self.down_sweep.to_vectors()

        times = np.concatenate([up_times, down_times])
        voltages = np.concatenate([up_voltages, down_voltages])

        return times, voltages
