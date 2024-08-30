# my_dagster_project

This dataset includes information on movies released during the summer months, typically regarded as the peak season for blockbuster films. The data has been sourced from IMDb, featuring key details such as movie titles, release dates, genres, directors, cast, and IMDb ratings. It's an excellent resource for analyzing trends in summer movie releases, exploring the correlation between release timing and box office performance, or studying the impact of genre on audience reception. This dataset is ideal for data enthusiasts, researchers, and movie buffs interested in exploring the dynamics of summer cinema.

## Getting started

### Dagster

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

FYI: Creds are already available, clone and run dagster using

```bash
dagster dev
```

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `setup.py`.

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
