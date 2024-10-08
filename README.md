# my_dagster_project

This dataset includes information on movies released during the summer months, typically regarded as the peak season for blockbuster films.

**Why this dataset:- Easy to relate and play around, instead of picking F1 or Cricket data set.**

**Input**

`summer_movies.csv` ==> It has column information about movies released with columns like, name, release date, runtime, avg rating, votes, release date, timestamp. Here unique id is tconst

**Note:** Release date, timestamp these both columns are manually generated

`summer_movie_genres.csv` ==> It has imformation about the genres of the corresponding movies, with columns, tconst and genres.

**Output**

We want to get movie and there genres by joining these data set together.

## Getting started

### Python Virtual environment

Create a virtual environment to install the specified version of libraries.

```bash
python -m venv myenv

source myenv/bin/activate
```
### pyarrow

```bash
pip install pyarrow
```

### Dagster, version 1.7.7

```bash
pip install dagster dagster-webserver
```

```bash
pip install -e ".[dev]"
```

Then, start the Dagster UI web server:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project.

### SQL Server Setup

1. Go to this site, and login [freesqldatabase](https://www.freesqldatabase.com/)
2. Take help from this [video](https://youtu.be/TMGHOW8Hzvw?si=FMUGmkbhbglSOd5d) and get your db credentials.
3. Provide DB credentials in `.env` file.

**Credentials are already available, clone repo and run dagster. Auto expired after 7 days**

## Sneak peek

<img src="./data/flow.png" alt="Alt text">

## Flow

**Using IOManager for reading and writing the data to warehouse_location and transectional table.**

Why:- I/O managers in Dagster are used to handle the storage and retrieval of asset and op outputs, allowing you to separate business logic from I/O operations.

### Extraction, (group_name="extract")

1. Extract data from souce, in this case its data folder and load into a central location like AWS S3. In my case its `warehouse_location/result`
2. Keep in raw fomat as it was in source, if there is a variance you would know where is the issue.
3. Store with efficient data file format (e.g., Parquet with run length encoding)

### Staging, (group_name="stg")

1. Read from `warehouse_location` and write data to transaction table.

```bash
summer_movies.csv ==> summer_movies
summer_movie_genres.csv ==> summer_movie_genres
```

2. Cleaning: Remove duplicate records, Handle missing values (e.g., impute missing ages, fill missing purchase history with zero),
   and Correct any inconsistencies in data (e.g., standardize date formats).

```bash
df['runtime_minutes'] = df['runtime_minutes'].fillna(df['runtime_minutes'].mean())
df['year'] = df['year'].fillna(9999)
df['timestamp'] = df['timestamp'].apply(parse_date)
```

3. summer_movies table is partitioned on `release_day` daily instead of hourly. With START_DATE = '2024-01-01'
   and END_DATE = '2024-01-12'
   **Why:- with a partition is created a metadata will also be maintained corresponding to it. When there are too many partitions, it can lead to overhead metadata and Small File Problem. this would not be ideal for distributed prosessing large dataset.**

```bash
Consider 10 years of data
hourly partition:- 24*365*10 = 87600
Daily partition:- 365*10 = 3650

** You can keep 3 yr to 4 yr data in standard layer and push other to glacier to efficient storage and processing.
```

Better approach would be partition on `type/date` (e.g. hollywood/date)

### Transformation, (group_name="transformation")

Merge data from `summer_movies` and `summer_movie_genres`, and store into processed folder of warehouse location in paquet format.

**Why:- This would be master data that would be used by data science, downstream data team and populate warehouse.**

### Loading, (group_name="load")

Read master data and load into warehouse table, in my case its transectional table.

### Job

Bundled all components of the data flow into a job. This is helpful for managing and setting up schedules.

### Schedules

Setup the schedule to run every monday

## Testing

### Assert Test

When reading incremental data you would want to make sure high quality data is flowing into the pipeline. I have used `check_specs`, to make sure after doing operation
data quality is correct. And severity not all data quality check needs to alert stakeholders.

```bash
yield AssetCheckResult(
        passed=bool(df["tconst"].notnull().all()),
        severity=AssetCheckSeverity.WARN,
        description="key notnull",
        metadata = {
            "num_rows": len(df),
            "num_empty": len(df["tconst"].notnull())
        }
    )
```

**Data quality checks implemented**

1. Count
2. Joining key not null

### Unit Test

Tests are in the `my_dagster_project_tests/test_assets` file and you can run tests using `pytest`. This is used when there is a new implementation and want to test that
locally:

```bash
pytest my_dagster_project_tests
```
