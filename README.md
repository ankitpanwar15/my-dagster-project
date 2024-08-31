# my_dagster_project

This dataset includes information on movies released during the summer months, typically regarded as the peak season for blockbuster films.
\*\*Why pick:- Easy to relate and play around, instead of picking F1 or Cricket data set.

summer_movies.csv ==> It has column information about movies released with columns like, name, release date, runtime, avg rating, votes, release date, timestamp. Here unique id is tconst

\*\* release date, timestamp these both columns are manually generated

summer_movie_genres.csv ==> It has imformation about the genres of the corresponding movies, with columns, tconst and genres.

We want to get movie and there genres by joining these data set together.

## Getting started

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

FYI: Creds are already available, clone repo and run dagster.

## Flow

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

3. summer_movies table is partitioned on `release_day` daily instead of hourly.
   \*\*why:- with a partition is created a metadata will also be maintained corresponding to it. When there are too many partitions, it can lead to overhead metadata and Small File Problem. this would not be ideal for distributed prosessing large dataset.

```bash
Consider 10 years of data
hourly partition:- 24*365*10 = 87600
Daily partition:- 365*10 = 3650

** You can keet 3 year to 4 year data in standard layer and push other to glacier to efficient storage and processing.
```

\*\*Using IOManager for reading and writing the data to warehouse_location and transectional table.

Better approach would be partition on `type/date` (e.g. hollywood/date)

### Transformation, (group_name="transformation")

Merge data from `summer_movies` and `summer_movie_genres`, and store into processed folder of warehouse location in paquet format.

\*\* Why:- This would be master data that would be used by data science, downstream data team and populate warehouse.

### Loading, (group_name="load")

Read master data and load into warehouse table, in my case its transectional table.

### Unit testing

Tests are in the `my_dagster_project_tests` directory and you can run tests using `pytest`:

```bash
pytest my_dagster_project_tests
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/concepts/partitions-schedules-sensors/schedules) or [Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) for your jobs, the [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Deploy on Dagster Cloud

The easiest way to deploy your Dagster project is to use Dagster Cloud.

Check out the [Dagster Cloud Documentation](https://docs.dagster.cloud) to learn more.
