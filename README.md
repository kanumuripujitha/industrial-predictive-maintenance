# Industrial Predictive Maintenance Synthetic Data Generator

## Project Overview

This project generates reproducible synthetic industrial predictive-maintenance data for analytics, validation, and machine-risk scoring.

The dataset represents:
- 3 plants
- 12 production lines
- 100 machines
- 500 sensors
- 90 days of hourly telemetry
- 100 synthetic failure events

**Important:** All generated data is synthetic and does not represent measurements from real industrial equipment.

## Features

- Master data generation for plants, production lines, machines, and sensors
- Hourly sensor telemetry generation
- Synthetic failure-event labels
- Maintenance work orders, parts, technicians, and operating shifts
- Machine risk score calculation
- Telemetry anomaly injection around synthetic failure timestamps
- CSV, JSON, and SQL exports
- Automated tests using pytest

## Requirements

- Python 3.10 or compatible
- pandas
- numpy
- pytest

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Generate the Data

Run the scripts from the project root in this order:

```powershell
python -m src.generate_data
python -m src.generate_failures
python -m src.generate_maintenance
python -m src.inject_anomalies
python -m src.calculate_risk
python -m src.validate_data
python -m src.export_data
```

Note: Anomaly injection modifies telemetry values. Run it only after generating the telemetry and failure events. For repeatable runs, regenerate the base telemetry before injecting anomalies.

## Tests

Run automated tests:

```powershell
python -m pytest -v
```

## Output Files

Generated files are stored in `outputs/`.

| File | Description |
|---|---|
| `plants.csv` | Plant master data |
| `production_lines.csv` | Production lines |
| `machines.csv` | Machine master data |
| `sensors.csv` | Sensor metadata and limits |
| `telemetry_events.csv` | Hourly sensor readings |
| `failure_events.csv` | Synthetic failure labels |
| `maintenance_work_orders.csv` | Maintenance work orders |
| `parts.csv` | Spare parts |
| `technicians.csv` | Technician records |
| `operating_shifts.csv` | Shift definitions |
| `machine_risk_scores.csv` | Heuristic machine risk scores |
| `seed_data.sql` | SQL export |
| `*.json` | JSON exports of generated tables |

## Limitations

- Failure labels are synthetic and are not based on real failure records.
- Machine risk scores are heuristic indicators, not calibrated failure probabilities.
- Generated data should be validated before use in any downstream analysis.