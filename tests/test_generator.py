from src.generate_data import generate_master_data


def test_master_data_row_counts():
    data = generate_master_data()
    assert len(data["plants"]) == 3
    assert len(data["production_lines"]) == 12
    assert len(data["machines"]) == 100
    assert len(data["sensors"]) == 500


def test_machine_ids_are_unique():
    data = generate_master_data()
    assert data["machines"]["machine_id"].is_unique


def test_sensor_ids_are_unique():
    data = generate_master_data()
    assert data["sensors"]["sensor_id"].is_unique


def test_each_machine_has_five_sensor_types():
    data = generate_master_data()
    counts = data["sensors"].groupby("machine_id")["sensor_type"].nunique()
    assert len(counts) == 100
    assert (counts == 5).all()
