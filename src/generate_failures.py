import random
from pathlib import Path

import pandas as pd

from src.config import SEED, OUTPUT_DIR


def main():
    random.seed(SEED)
    output = Path(OUTPUT_DIR)

    machines = pd.read_csv(output / "machines.csv")
    sensors = pd.read_csv(output / "sensors.csv")
    telemetry = pd.read_csv(
        output / "telemetry_events.csv",
        parse_dates=["timestamp"],
    )

    sensor_types = ["TEMP", "VIB", "PRESS", "CURRENT", "SPEED"]
    failure_types = {
        "TEMP": "OVERHEATING",
        "VIB": "EXCESSIVE_VIBRATION",
        "PRESS": "PRESSURE_ANOMALY",
        "CURRENT": "ELECTRICAL_OVERLOAD",
        "SPEED": "SPEED_DEGRADATION",
    }

    # Select 150 distinct machines for labelled failure events.
    selected = machines.sample(
        n=min(150, len(machines)),
        random_state=SEED,
    )

    events = []

    for index, machine in enumerate(
        selected.to_dict("records"), start=1
    ):
        machine_sensors = sensors[
            sensors["machine_id"] == machine["machine_id"]
        ]
        sensor_type = sensor_types[(index - 1) % len(sensor_types)]

        sensor = machine_sensors[
            machine_sensors["sensor_type"] == sensor_type
        ].iloc[0]

        readings = telemetry[
            telemetry["sensor_id"] == sensor["sensor_id"]
        ]

        # Avoid the first 24 hours so a prior-reading window exists.
        candidates = readings.iloc[24:]
        chosen = candidates.iloc[
            random.randrange(len(candidates))
        ]

        events.append({
            "failure_event_id": f"FAIL-{index:04d}",
            "machine_id": machine["machine_id"],
            "sensor_id": sensor["sensor_id"],
            "timestamp": chosen["timestamp"],
            "failure_type": failure_types[sensor_type],
            "severity": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "label": 1,
            "ground_truth_source": "SYNTHETIC",
        })

    failures = pd.DataFrame(events)
    failures.to_csv(output / "failure_events.csv", index=False)

    print(f"failure_events: {len(failures)} rows")
    print(f"Unique machines: {failures['machine_id'].nunique()}")
    print("Saved outputs/failure_events.csv")


if __name__ == "__main__":
    main()
