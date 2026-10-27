from pathlib import Path

import numpy as np
import pandas as pd

from src.config import OUTPUT_DIR, SEED


def main():
    output = Path(OUTPUT_DIR)
    telemetry_path = output / "telemetry_events.csv"
    failures_path = output / "failure_events.csv"
    sensors_path = output / "sensors.csv"

    telemetry = pd.read_csv(telemetry_path)
    telemetry["timestamp"] = pd.to_datetime(
        telemetry["timestamp"], utc=True
    )
    failures = pd.read_csv(
        failures_path, parse_dates=["timestamp"]
    )
    sensors = pd.read_csv(sensors_path)

    sensor_types = sensors.set_index("sensor_id")["sensor_type"].to_dict()
    limits = sensors.set_index("sensor_id")[["min_value", "max_value"]]
    directions = {
        "OVERHEATING": 1,
        "EXCESSIVE_VIBRATION": 1,
        "PRESSURE_ANOMALY": 1,
        "ELECTRICAL_OVERLOAD": 1,
        "SPEED_DEGRADATION": -1,
    }

    modified = 0

    for failure in failures.to_dict("records"):
        sensor_id = failure["sensor_id"]
        failure_time = pd.to_datetime(failure["timestamp"], utc=True)
        direction = directions[failure["failure_type"]]

        mask = (
            telemetry["sensor_id"].eq(sensor_id)
            & telemetry["timestamp"].lt(failure_time)
            & telemetry["timestamp"].ge(
                failure_time - pd.Timedelta(hours=6)
            )
        )
        indices = telemetry.index[mask]
        if len(indices) == 0:
            continue

        values = telemetry.loc[indices, "value"].to_numpy(dtype=float)
        low = float(limits.loc[sensor_id, "min_value"])
        high = float(limits.loc[sensor_id, "max_value"])
        span = high - low

        # Gradual deterioration over six hourly readings.
        trend = np.linspace(0.03, 0.25, len(indices)) * span
        if direction > 0:
            changed = values + trend
        else:
            changed = values - trend

        telemetry.loc[indices, "value"] = np.round(
            np.clip(changed, low, high), 2
        )
        modified += len(indices)

    telemetry.to_csv(telemetry_path, index=False)
    print(f"Telemetry readings modified: {modified}")
    print("Direction-specific anomaly injection completed.")
    print("Synthetic data only; not measured industrial data.")


if __name__ == "__main__":
    main()
