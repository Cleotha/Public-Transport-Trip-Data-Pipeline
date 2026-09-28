#Read daily trip CSV files from a data/raw/ folder.
#Validate that all required columns exist.
#Remove duplicate trip IDs.
#Check that distance, duration, and fare are positive.
#Convert dates and numeric fields into the correct types.
#Separate invalid records into an errors/ folder with an error_reason column.
#Reject cancelled trips from completed-trip reports.
import csv
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_csv(filename):
    with open(filename, 'r') as f:
        return list(csv.DictReader(f))

def clean_trips(df):
    df['pickup_location'] = df['pickup_location'].str.strip().str.title()
    df['dropoff_location'] = df['dropoff_location'].str.strip().str.title()
    df['payment_status'] = df['payment_status'].str.strip().str.title()
    df['trip_status'] = df['trip_status'].str.strip().str.title()
    df['trip_id'] = pd.to_numeric(df['trip_id'], errors = 'coerce')
    df['passenger_id'] = pd.to_numeric(df['passenger_id'], errors = 'coerce')
    df['driver_id'] = pd.to_numeric(df['driver_id'], errors = 'coerce')
    df['distance_km'] = pd.to_numeric(df['distance_km'], errors = 'coerce')
    df['fare'] = pd.to_numeric(df['fare'], errors = 'coerce')
    df['duration_minutes'] = pd.to_numeric(df['duration_minutes'], errors = 'coerce')
    df.replace('', pd.NA,inplace = True)
    df['trip_date'] = pd.to_datetime(df['trip_date'], errors = 'coerce', format = 'mixed')
    return df

def handle_errors(df):
    # Clean status columns
    df = df.drop_duplicates(subset='trip_id')
    trip_status = df['trip_status'].fillna('').str.strip().str.lower()
    payment_status = df['payment_status'].fillna('').str.strip().str.lower()

    # Check required fields
    missing_trip_id = df['trip_id'].isna()
    missing_passenger = df['passenger_id'].isna()
    missing_driver = df['driver_id'].isna()
    missing_pickup = df['pickup_location'].fillna('').str.strip().eq('')
    missing_dropoff = df['dropoff_location'].fillna('').str.strip().eq('')

    # Check numeric columns
    invalid_distance = df['distance_km'].isna() | df['distance_km'].le(0)
    invalid_duration = df['duration_minutes'].isna() | df['duration_minutes'].le(0)
    invalid_fare = df['fare'].isna() | df['fare'].le(0)
    invalid_date = df['trip_date'].isna()

    # Check statuses
    invalid_trip_status = ~trip_status.isin(
        ['completed', 'cancelled', 'pending']
    )

    invalid_payment_status = ~payment_status.isin(
        ['paid', 'pending', 'failed']
    )

    # Create error
    has_error = (
        missing_trip_id |
        missing_passenger |
        missing_driver |
        missing_pickup |
        missing_dropoff |
        invalid_date |
        invalid_distance |
        invalid_duration |
        invalid_fare |
        invalid_trip_status |
        invalid_payment_status
    )

    # Add error reasons
    errors = df[has_error].copy()

    def get_error_reason(row):
        reasons = []

        if pd.isna(row['trip_id']):
            reasons.append("Missing trip ID")

        if pd.isna(row['passenger_id']):
            reasons.append("Missing passenger ID")

        if pd.isna(row['driver_id']) or str(row['driver_id']).strip() == '':
            reasons.append("Missing driver ID")

        if pd.isna(row['pickup_location']) or str(row['pickup_location']).strip() == '':
            reasons.append("Missing pickup location")

        if pd.isna(row['dropoff_location']) or str(row['dropoff_location']).strip() == '':
            reasons.append("Missing dropoff location")

        if pd.isna(row['trip_date']):
            reasons.append("Invalid date")

        if pd.isna(row['distance_km']) or row['distance_km'] <= 0:
            reasons.append("Invalid distance")

        if pd.isna(row['duration_minutes']) or row['duration_minutes'] <= 0:
            reasons.append("Invalid duration")

        if pd.isna(row['fare']) or row['fare'] <= 0:
            reasons.append("Invalid fare")

        if str(row['trip_status']).strip().lower() not in [
            'completed', 'cancelled', 'pending'
        ]:
            reasons.append("Invalid trip status")

        if str(row['payment_status']).strip().lower() not in [
            'paid', 'pending', 'failed'
        ]:
            reasons.append("Invalid payment status")

        return ", ".join(reasons)

    errors['error_reason'] = errors.apply(get_error_reason, axis=1)

    # Valid records
    valid = df[~has_error].copy()

    valid_trip = valid
    error_trip = errors
    completed_trip = valid_trip[valid_trip['trip_status'].str.lower() == 'completed']
    return valid_trip, error_trip, completed_trip

import os
def save_errors(errors, filename):
    os.makedirs('errors', exist_ok=True)
    errors.to_csv(f'errors/{filename}', index=False)
    logging.info("Saved %s rejected records/ %s", len(errors), filename)


from sqlalchemy import create_engine
from dotenv import load_dotenv
def load_to_postgres(completed_trip):
    load_dotenv()
    try:
        logging.info("Connecting to postgreSQL")
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        )    
        completed_trip.to_sql('transport', engine, if_exists='replace', index=False)
        logging.info("Loaded %s completed trips into the postgre.", len(completed_trip))
    except Exception:
        logging.exception("Failed to connect to postgreSQL.")

def run_pipeline():
    logging.info("Beginning data pipeline.")
    logging.info("Extracting data")
    raw_transport_trips = read_csv('/Users/Marydoris/Cleotha/Public Transport Trip Data Pipeline/transport_trips.csv')
    
    logging.info("Cleaning data")
    transport_trips = clean_trips(pd.DataFrame(raw_transport_trips))

    logging.info("Handling errors in data")
    valid_trip, error_trip, completed_trip = handle_errors(transport_trips)
    logging.info("Valid trip: %s", len(valid_trip))
    logging.warning("Error record: %s", len(error_trip))
    logging.info("Complete record: %s", len(completed_trip))

    logging.info("Saving error data")
    save_errors(error_trip, 'error_trip.csv')

    logging.info('Analyzing data')

    logging.info("Loading the data")
    load_to_postgres(completed_trip)

    logging.info("Pipeline completed successfully!")
if __name__ == "__main__":
    run_pipeline()