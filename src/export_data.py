import re
from pathlib import Path

import pandas as pd

from src.config import OUTPUT_DIR


def safe_name(name):
    name = re.sub(r"\W+", "_", name).strip("_").lower()
    if not name or name[0].isdigit():
        name = f"table_{name}"
    return name


def sql_value(value):
    if pd.isna(value):
        return "NULL"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def main():
    output = Path(OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)

    # Exclude backup copies and previously generated outputs.
    excluded = {
        "telemetry_events_backup.csv",
    }
    csv_files = sorted(
        path for path in output.glob("*.csv")
        if path.name not in excluded
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No eligible CSV files found in {output.resolve()}"
        )

    sql_path = output / "seed_data.sql"

    with sql_path.open("w", encoding="utf-8") as sql:
        sql.write("-- Synthetic industrial maintenance seed data\n\n")

        for csv_path in csv_files:
            df = pd.read_csv(csv_path)
            table = safe_name(csv_path.stem)

            json_path = output / f"{csv_path.stem}.json"
            df.to_json(
                json_path,
                orient="records",
                indent=2,
                date_format="iso",
            )

            columns = [safe_name(col) for col in df.columns]
            sql.write(f"CREATE TABLE IF NOT EXISTS {table} (\n")

            definitions = []
            for col, dtype in zip(columns, df.dtypes):
                if pd.api.types.is_integer_dtype(dtype):
                    sql_type = "INTEGER"
                elif pd.api.types.is_numeric_dtype(dtype):
                    sql_type = "REAL"
                else:
                    sql_type = "TEXT"
                definitions.append(f"    {col} {sql_type}")

            sql.write(",\n".join(definitions) + "\n);\n")

            column_sql = ", ".join(columns)
            for start in range(0, len(df), 1000):
                chunk = df.iloc[start:start + 1000]
                for row in chunk.itertuples(index=False, name=None):
                    values = ", ".join(sql_value(value) for value in row)
                    sql.write(
                        f"INSERT INTO {table} ({column_sql}) "
                        f"VALUES ({values});\n"
                    )

            sql.write("\n")
            print(
                f"Exported {csv_path.name} -> "
                f"{json_path.name} + SQL"
            )

    print(f"SQL export completed: {sql_path}")


if __name__ == "__main__":
    main()
