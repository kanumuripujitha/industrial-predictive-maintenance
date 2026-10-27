import pandas as pd


def test_generated_csv_files_exist():
    from pathlib import Path

    output = Path("outputs")
    expected_files = [
        "plants.csv",
        "production_lines.csv",
        "machines.csv",
        "sensors.csv",
        "telemetry_events.csv",
    ]

    for filename in expected_files:
        assert (output / filename).is_file(), f"Missing file: {filename}"


def test_machine_line_references_are_valid():
    from pathlib import Path

    output = Path("outputs")
    lines = pd.read_csv(output / "production_lines.csv")
    machines = pd.read_csv(output / "machines.csv")

    valid_line_ids = set(lines["line_id"])
    assert machines["line_id"].isin(valid_line_ids).all()


def test_sensor_machine_references_are_valid():
    from pathlib import Path

    output = Path("outputs")
    machines = pd.read_csv(output / "machines.csv")
    sensors = pd.read_csv(output / "sensors.csv")

    valid_machine_ids = set(machines["machine_id"])
    assert sensors["machine_id"].isin(valid_machine_ids).all()


def test_telemetry_values_are_within_sensor_limits():
    from pathlib import Path

    output = Path("outputs")
    sensors = pd.read_csv(output / "sensors.csv")
    telemetry = pd.read_csv(output / "telemetry_events.csv")

    checked = telemetry.merge(
        sensors[["sensor_id", "min_value", "max_value"]],
        on="sensor_id",
        how="left",
        validate="many_to_one",
    )

    assert checked["min_value"].notna().all()
    assert checked["value"].ge(checked["min_value"]).all()
    assert checked["value"].le(checked["max_value"]).all()
