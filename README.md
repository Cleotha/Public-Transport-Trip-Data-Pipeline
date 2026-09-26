# Public Transport Trip Data Pipeline

A Python data pipeline that cleans, validates, and processes public transport trip data before loading completed trips into PostgreSQL.

## Overview

This project takes raw transport trip data from a CSV file and runs it through a simple ETL workflow:

**Extract → Clean → Validate → Handle Errors → Analyze → Load**

The pipeline is designed to identify invalid records, save them separately with clear error reasons, exclude cancelled trips from the completed-trip dataset, and load valid completed trips into PostgreSQL.

## Features

- Reads transport trip data from a CSV file.
- Cleans text fields by removing extra whitespace and standardizing capitalization.
- Converts numeric fields to appropriate numeric types.
- Converts trip dates to datetime values.
- Removes duplicate `trip_id` records.
- Validates required fields.
- Checks that distance, duration, and fare are greater than zero.
- Validates trip and payment statuses.
- Separates invalid records from valid records.
- Adds an `error_reason` column to rejected records.
- Saves rejected records to an `errors/` folder.
- Filters the valid dataset to include only completed trips.
- Loads completed trips into PostgreSQL using SQLAlchemy.

## Technologies Used

- **Python**
- **Pandas** — data cleaning and validation
- **CSV** — raw data input
- **SQLAlchemy** — database connection and loading
- **PostgreSQL** — data storage
- **python-dotenv** — loading database credentials from environment variables

## Input Data

The pipeline expects transport trip data containing fields such as:

- `trip_id`
- `passenger_id`
- `driver_id`
- `pickup_location`
- `dropoff_location`
- `trip_date`
- `distance_km`
- `duration_minutes`
- `fare`
- `payment_status`
- `trip_status`

### Expected status values

**Trip status**
- `Completed`
- `Cancelled`
- `Pending`

**Payment status**
- `Paid`
- `Pending`
- `Failed`

## Data Quality Checks

The pipeline checks for:

1. Missing trip IDs
2. Missing passenger IDs
3. Missing driver IDs
4. Missing pickup locations
5. Missing dropoff locations
6. Invalid dates
7. Invalid or non-positive distance
8. Invalid or non-positive duration
9. Invalid or non-positive fare
10. Invalid trip status
11. Invalid payment status
12. Duplicate trip IDs

Invalid records are rejected and saved with an `error_reason` column explaining why each record failed validation.

## Pipeline Flow

```text
transport_trips.csv
        ↓
     Extract
        ↓
      Clean
        ↓
     Validate
        ↓
 ┌──────┴───────┐
 ↓              ↓
Valid         Invalid
Records       Records
 ↓              ↓
Completed     errors/
 Trips        error_trip.csv
 ↓
PostgreSQL
```

## Project Structure

A typical project structure is:

```text
Public Transport Trip Data Pipeline/
│
├── script.py
├── transport_trips.csv
├── errors/
│   └── error_trip.csv
├── .env
├── .gitignore
└── README.md
```

> Note: The current Python script reads `transport_trips.csv` from the project directory. The initial project requirements mention a `data/raw/` folder, so the file path can be updated later if the project is reorganized around that structure.

## PostgreSQL Configuration

Database credentials are loaded from a `.env` file.

Example:

```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=your_database
```

**Do not commit your `.env` file to GitHub.**

Add it to `.gitignore`:

```gitignore
.env
__pycache__/
errors/
```

If you want to keep the generated error file in GitHub for demonstration purposes, remove `errors/` from `.gitignore`.

## How to Run

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd "Public Transport Trip Data Pipeline"
```

### 2. Install dependencies

```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv
```

### 3. Configure your environment

Create a `.env` file and add your PostgreSQL credentials:

```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=your_database
```

### 4. Add the input CSV

Place `transport_trips.csv` in the project directory.

### 5. Run the pipeline

```bash
python script.py
```

A successful run ends with:

```text
🎉 Pipeline complete!
```

The completed trips are loaded into a PostgreSQL table named:

```text
transport
```

Rejected records are saved as:

```text
errors/error_trip.csv
```

## Example Error Reasons

Rejected records may contain reasons such as:

```text
Missing driver ID
Invalid date
Invalid distance
Invalid fare
Invalid trip status
```

A record can contain multiple reasons, for example:

```text
Missing driver ID, Invalid distance, Invalid payment status
```

## Learning Goals

This project demonstrates practical data engineering concepts including:

- Data extraction
- Data cleaning
- Data validation
- Error handling
- Data quality checks
- ETL pipeline design
- Working with Pandas
- Loading data into PostgreSQL
- Environment variables and database credentials
- Separating valid and invalid data

## Future Improvements

Possible improvements include:

- Read daily files automatically from a `data/raw/` directory.
- Use relative paths instead of hard-coded local file paths.
- Add logging instead of relying only on `print()` statements.
- Add automated tests with `pytest`.
- Create summary reports for completed trips.
- Add pipeline configuration through environment variables.
- Add a proper database schema and constraints.
- Schedule the pipeline to run automatically.

## Author

**Chidiebere Marydoris**

Built as a hands-on data engineering project to practice data cleaning, validation, ETL workflows, and PostgreSQL loading.
