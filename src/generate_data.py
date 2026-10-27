import random
from pathlib import Path
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from src.config import (
    SEED,
    NUM_PLANTS,
    NUM_LINES,
    NUM_MACHINES,
    NUM_SENSORS,
    DAYS,
    OUTPUT_DIR,
)


def generate_master_data():
    random.seed(SEED)

    plants = [
        {
            "plant_id": f"PLT-{i:03d}",
            "plant_name": f"Plant {i}",
            "status": "ACTIVE",
        }
        for i in range(1, NUM_PLANTS + 1)
    ]

    lines = []
    for i in range(1, NUM_LINES + 1):
        plant_no = ((i - 1) % NUM_PLANTS) + 1
        lines.append({
            "line_id": f"LINE-{i:03d}",
            "plant_id": f"PLT-{plant_no:03d}",
            "line_name": f"Production Line {i}",
        })

    machines = []
    machine_types = ["Motor", "Pump", "Conveyor", "Compressor"]

    for i in range(1, NUM_MACHINES + 1):
        line_no = ((i - 1) % NUM_LINES) + 1
        machines.append({
            "machine_id": f"MCH-{i:03d}",
            "line_id": f"LINE-{line_no:03d}",
            "machine_type": random.choice(machine_types),
            "status": "ACTIVE",
        })

    sensor_types = [
        ("TEMP", "C", 0, 120),
        ("VIB", "mm/s", 0, 25),
        ("PRESS", "bar", 0, 20),
        ("CURRENT", "A", 0, 100),
        ("SPEED", "rpm", 0, 5000),
    ]

    sensors = []
    for machine_no in range(1, NUM_MACHINES + 1):
        for sensor_type, unit, low, high in sensor_types:
            sensor_no = len(sensors) + 1
            sensors.append({
                "sensor_id": f"SNS-{sensor_no:04d}",
                "machine_id": f"MCH-{machine_no:03d}",
                "sensor_type": sensor_type,
                "unit": unit,
                "min_value": low,
                "max_value": high,
            })

    if len(sensors) != NUM_SENSORS:
        raise ValueError(
            f"Expected {NUM_SENSORS} sensors, generated {len(sensors)}. "
            "Check NUM_SENSORS = NUM_MACHINES * 5."
        )

    return {
        "plants": pd.DataFrame(plants),
        "production_lines": pd.DataFrame(lines),
        "machines": pd.DataFrame(machines),
        "sensors": pd.DataFrame(sensors),
    }


def generate_telemetry(sensors):
    rng = np.random.default_rng(SEED)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    readings = []

    for sensor in sensors.to_dict("records"):
        kind = sensor["sensor_type"]

        for hour in range(DAYS * 24):
            timestamp = start + timedelta(hours=hour)

            if kind == "TEMP":
                value = rng.normal(65, 5)
            elif kind == "VIB":
                value = rng.normal(4, 1)
            elif kind == "PRESS":
                value = rng.normal(8, 1)
            elif kind == "CURRENT":
                value = rng.normal(30, 5)
            else:
                value = rng.normal(1500, 100)

            value = float(np.clip(
                value,
                sensor["min_value"],
                sensor["max_value"],
            ))

            readings.append({
                "telemetry_id": (
                    f"TEL-{sensor['sensor_id']}-"
                    f"{timestamp.strftime('%Y%m%d%H')}"
                ),
                "sensor_id": sensor["sensor_id"],
                "machine_id": sensor["machine_id"],
                "timestamp": timestamp.isoformat(),
                "value": round(value, 2),
                "unit": sensor["unit"],
            })

    return pd.DataFrame(readings)


def main():
    output = Path(OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)

    data = generate_master_data()

    for name, df in data.items():
        df.to_csv(output / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} rows")

    telemetry = generate_telemetry(data["sensors"])
    telemetry.to_csv(output / "telemetry_events.csv", index=False)

    print(f"telemetry_events: {len(telemetry)} rows")
    print("Data generation completed!")


if __name__ == "__main__":
    main()
