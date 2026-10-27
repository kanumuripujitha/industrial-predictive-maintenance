
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("outputs")


def main():
    telemetry_path = OUTPUT_DIR / "telemetry_events.csv"
    sensors_path = OUTPUT_DIR / "sensors.csv"

    if not telemetry_path.exists() or not sensors_path.exists():
        print("ERROR: Required CSV files are missing.")
        print("First run: python -m src.generate_data")
        return

    # Read sensor metadata
    sensors = pd.read_csv(sensors_path)

    # Read telemetry data
    telemetry = pd.read_csv(telemetry_path)

    # Identify the sensor type for each telemetry reading
    data = telemetry.merge(
        sensors[["sensor_id", "sensor_type"]],
       on="sensor_id",
        how="left",
    )

    if data["sensor_type"].isna().any():
        print("ERROR: Some telemetry rows have unknown sensor IDs.")
        return

    
    # Calculate average readings for each machine and sensor type
    readings = data.groupby(
        ["machine_id", "sensor_type"]
    )["value"].mean().unstack()

    # Create the risk DataFrame BEFORE adding risk columns
    risk = pd.DataFrame(index=readings.index)

    # Temperature risk
    if "TEMP" in readings.columns:
        risk["temperature_risk"] = (
            (readings["TEMP"] - 60) / 40
        ).clip(0, 1)
    else:
        risk["temperature_risk"] = float("nan")

    # Vibration risk
    if "VIB" in readings.columns:
        risk["vibration_risk"] = (
            readings["VIB"] / 10
        ).clip(0, 1)
    else:
        risk["vibration_risk"] = float("nan")

    # Pressure risk
    if "PRESS" in readings.columns:
        risk["pressure_risk"] = (
            (readings["PRESS"] - 100) / 100
        ).abs().clip(0, 1)
    else:
        risk["pressure_risk"] = float("nan")

  
    # Calculate score using only available sensor types
    risk_columns = [
        "temperature_risk",
        "vibration_risk",
        "pressure_risk",
    ]

    weights = pd.Series({
        "temperature_risk": 0.4,
        "vibration_risk": 0.4,
        "pressure_risk": 0.2,
    })

    available_risks = risk[risk_columns]
    valid_weights = available_risks.notna().mul(weights)

    weighted_sum = (
        available_risks.fillna(0).mul(weights)
    ).sum(axis=1)

    total_weight = valid_weights.sum(axis=1)

    risk["risk_score"] = (
        weighted_sum.div(total_weight).mul(100)
    ).round(2)

    risk["risk_level"] = pd.cut(
        risk["risk_score"],
        bins=[-1, 30, 60, 100],
        labels=["LOW", "MEDIUM", "HIGH"],
    )

    risk = risk.reset_index()
    risk = risk.sort_values("risk_score", ascending=False)

    output_path = OUTPUT_DIR / "machine_risk_scores.csv"
    risk.to_csv(output_path, index=False)


    print(f"Machines scored: {len(risk)}")
    print(f"Risk report saved to: {output_path}")
    print("\nTop 10 machines by risk:")
    print(risk.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
