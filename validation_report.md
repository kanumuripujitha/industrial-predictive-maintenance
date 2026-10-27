# Validation Report

## Project

Industrial Predictive Maintenance Synthetic Data Generator

## 1. Dataset Summary

| Dataset | Expected / Observed Rows |
|---|---:|
| Plants | 3 |
| Production Lines | 12 |
| Machines | 100 |
| Sensors | 500 |
| Telemetry Events | 1,080,000 |
| Failure Events | 100 |
| Maintenance Work Orders | 100 |
| Technicians | 15 |
| Parts | 20 |
| Operating Shifts | 3 |

## 2. Automated Test Results

The project test suite was executed using `pytest`.

**Result:** 8 tests passed.

Tests cover:
- Master-data row counts
- Unique machine identifiers
- Unique sensor identifiers
- Five sensor types per machine
- Required CSV file existence
- Valid machine-to-production-line references
- Valid sensor-to-machine references
- Telemetry values within configured sensor limits

## 3. Data Integrity

The validation process checks selected record counts, relationships, and telemetry constraints.

Foreign-key and timestamp checks should also be run across the failure events, maintenance work orders, and other generated datasets before final submission.

## 4. Synthetic Data Notice

All data is synthetic and generated for this project. Failure events and machine risk scores must not be interpreted as verified real-world failure records or calibrated failure probabilities.

## 5. Limitations

- The current automated tests cover selected requirements, not every possible data-quality issue.
- Additional validation is needed for all foreign keys, timestamp consistency, duplicate records, and required fields.
- The final output should be regenerated and validated using the documented run sequence before submission.

## 6. Status

The current automated test run completed successfully with 8 passing tests. Full challenge compliance remains subject to additional validation.