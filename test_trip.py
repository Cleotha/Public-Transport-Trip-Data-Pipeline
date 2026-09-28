import pytest
import pandas as pd
from script import clean_trips, handle_errors
@pytest.fixture
def df():
    df = pd.DataFrame({
        "trip_id": [1],
        "passenger_id": [101],
        "driver_id": [201],
        "pickup_location": ["Yaba"],
        "dropoff_location": ["Ikeja"],
        "trip_date": ["2026-09-20"],
        "distance_km": [10],
        "duration_minutes": [30],
        "fare": [2500],
        "payment_status": ["Paid"],
        "trip_status": ["Completed"]
    })
    return df

#testing clean trip
def test_clean_trips_converts_numeric_columns(df):
    result = clean_trips(df)
    assert pd.api.types.is_numeric_dtype(result["trip_id"])
    assert pd.api.types.is_numeric_dtype(result["fare"])
    assert pd.api.types.is_numeric_dtype(result["distance_km"])

def test_clean_trips_formats_locations(df):
    result = clean_trips(df)
    assert result["pickup_location"].iloc[0] == "Yaba"
    assert result["dropoff_location"].iloc[0] == "Ikeja"

#testing handle error
def test_handle_errors_rejects_negative_fare(df):
    df["fare"] = -500
    df = clean_trips(df)
    valid, errors, completed = handle_errors(df)
    assert len(errors) == 1
    assert "Invalid fare" in errors.iloc[0]["error_reason"]

#testing valid trip
def test_valid_trip_is_not_rejected(df):
    valid, errors, completed = handle_errors(df)
    assert len(valid) == 1
    assert len(errors) == 0
    assert len(completed) == 1

#testing completed trip
def test_cancelled_trip_is_not_in_completed(df):
    df["trip_status"] = ["Cancelled"]
    df = clean_trips(df)
    valid, errors, completed = handle_errors(df)
    assert len(valid) == 1
    assert len(errors) == 0
    assert len(completed) == 0

#testing completed trip
def test_completed_trip_is_in_completed(df):
    valid, errors, completed = handle_errors(df)
    assert len(completed) == 1