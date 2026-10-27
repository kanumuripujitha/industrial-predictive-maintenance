import random
from pathlib import Path

import pandas as pd

from src.config import SEED, OUTPUT_DIR


def main():
    random.seed(SEED)
    output = Path(OUTPUT_DIR)

    failures = pd.read_csv(
        output / "failure_events.csv",
        parse_dates=["timestamp"],
    )
    machines = pd.read_csv(output / "machines.csv")

    technicians = pd.DataFrame([
        {
            "technician_id": f"TECH-{i:03d}",
            "technician_name": f"Technician {i}",
            "specialization": [
                "MECHANICAL", "ELECTRICAL", "INSTRUMENTATION"
            ][(i - 1) % 3],
        }
        for i in range(1, 16)
    ])

    parts = pd.DataFrame([
        {
            "part_id": f"PART-{i:03d}",
            "part_name": [
                "Bearing", "Motor Belt", "Pressure Valve",
                "Cooling Fan", "Vibration Mount",
            ][(i - 1) % 5],
            "unit_cost": round(random.uniform(25, 500), 2),
        }
        for i in range(1, 21)
    ])

    work_orders = []
    for i, failure in enumerate(
        failures.to_dict("records"), start=1
    ):
        created = pd.Timestamp(failure["timestamp"]) - pd.Timedelta(
            hours=random.randint(1, 24)
        )
        completed = pd.Timestamp(failure["timestamp"]) + pd.Timedelta(
            hours=random.randint(2, 48)
        )

        work_orders.append({
            "work_order_id": f"WO-{i:04d}",
            "failure_event_id": failure["failure_event_id"],
            "machine_id": failure["machine_id"],
            "technician_id": f"TECH-{random.randint(1, 15):03d}",
            "part_id": f"PART-{random.randint(1, 20):03d}",
            "created_at": created.isoformat(),
            "completed_at": completed.isoformat(),
            "status": "COMPLETED",
            "maintenance_type": "CORRECTIVE",
        })

    technicians.to_csv(output / "technicians.csv", index=False)
    parts.to_csv(output / "parts.csv", index=False)
    pd.DataFrame(work_orders).to_csv(
        output / "maintenance_work_orders.csv", index=False
    )

    shifts = pd.DataFrame([
        {
            "shift_id": f"SHIFT-{i:03d}",
            "shift_name": name,
            "start_hour": start,
            "end_hour": end,
        }
        for i, (name, start, end) in enumerate([
            ("DAY", 6, 14),
            ("EVENING", 14, 22),
            ("NIGHT", 22, 6),
        ], start=1)
    ])
    shifts.to_csv(output / "operating_shifts.csv", index=False)

    print(f"Technicians: {len(technicians)}")
    print(f"Parts: {len(parts)}")
    print(f"Maintenance work orders: {len(work_orders)}")
    print(f"Operating shifts: {len(shifts)}")
    print("Maintenance datasets generated!")


if __name__ == "__main__":
    main()
