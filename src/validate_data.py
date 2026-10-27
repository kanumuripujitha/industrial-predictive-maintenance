
from pathlib import Path
import pandas as pd

from src.config import (
    NUM_PLANTS,
    NUM_LINES,
    NUM_MACHINES,
    NUM_SENSORS,
)

OUTPUT_DIR = Path("outputs")


def main():
    all_valid = True

    # 1. Check expected row counts
    expected_counts = {
        "plants": NUM_PLANTS,
        "production_lines": NUM_LINES,
        "machines": NUM_MACHINES,
        "sensors": NUM_SENSORS,
    }

    data = {}

    for name, expected in expected_counts.items():
        path = OUTPUT_DIR / f"{name}.csv"

        if not path.exists():
            print(f"FAIL: {name}.csv missing")
            all_valid = False
            continue

        df = pd.read_csv(path)
        data[name] = df

        if len(df) == expected:
            print(f"PASS: {name}: {len(df)} rows")
        else:
            print(f"FAIL: {name}: expected {expected}, found {len(df)}")
            all_valid = False

        if "id" in df.columns and df["id"].duplicated().any():
            print(f"FAIL: Duplicate IDs in {name}")
            all_valid = False

    # 2. Check production lines -> plants
    if "production_lines" in data and "plants" in data:
        lines = data["production_lines"]
        plants = data["plants"]

        if {"plant_id", "id"}.issubset(lines.columns) and "id" in plants.columns:
            invalid = ~lines["plant_id"].isin(plants["id"])
            if invalid.any():
                print(f"FAIL: {invalid.sum()} lines have invalid plant IDs")
                all_valid = False
            else:
                print("PASS: Production lines reference valid plants")

    # 3. Check machines -> production lines
    if "machines" in data and "production_lines" in data:
        machines = data["machines"]
        lines = data["production_lines"]

        if {"production_line_id", "id"}.issubset(machines.columns) and "id" in lines.columns:
            invalid = ~machines["production_line_id"].isin(lines["id"])
            if invalid.any():
                print(f"FAIL: {invalid.sum()} machines have invalid line IDs")
                all_valid = False
            else:
                print("PASS: Machines reference valid production lines")

    # 4. Check sensors -> machines
    if "sensors" in data and "machines" in data:
        sensors = data["sensors"]
        machines = data["machines"]

        if {"machine_id", "id"}.issubset(sensors.columns) and "id" in machines.columns:
            invalid = ~sensors["machine_id"].isin(machines["id"])
            if invalid.any():
                print(f"FAIL: {invalid.sum()} sensors have invalid machine IDs")
                all_valid = False
            else:
                print("PASS: Sensors reference valid machines")

    # 5. Check telemetry -> sensors
    telemetry_path = OUTPUT_DIR / "telemetry_events.csv"

    if not telemetry_path.exists():
        print("FAIL: telemetry_events.csv missing")
        all_valid = False
    else:
        telemetry = pd.read_csv(telemetry_path)
        print(f"INFO: telemetry_events: {len(telemetry)} rows")

        if telemetry.empty:
            print("FAIL: Telemetry file is empty")
            all_valid = False
        elif "sensor_id" in telemetry.columns and "id" in data.get("sensors", pd.DataFrame()).columns:
            valid_sensor_ids = set(data["sensors"]["id"])
            invalid = ~telemetry["sensor_id"].isin(valid_sensor_ids)

            if invalid.any():
                print(f"FAIL: {invalid.sum()} telemetry rows have invalid sensor IDs")
                all_valid = False
            else:
                print("PASS: Telemetry references valid sensors")

    if all_valid:
        print("\nValidation completed: ALL CHECKS PASSED")
    else:
        print("\nValidation completed: SOME CHECKS FAILED")


if __name__ == "__main__":
    main()