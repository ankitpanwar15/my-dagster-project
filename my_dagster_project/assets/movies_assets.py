import pandas as pd
from dagster import asset, AssetCheckResult, multi_asset_check, Definitions, AssetCheckSpec, AssetCheckSeverity, Output, asset_check, HourlyPartitionsDefinition, MetadataValue, AssetMaterialization, AssetExecutionContext
from sqlalchemy import create_engine
from datetime import datetime
from ..partitions import Daily_partition
from ..io import db_conn

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

@asset(
    check_specs=[AssetCheckSpec(name="check_count", asset="extract_movie_genres")],
    group_name="extract", 
    compute_kind="pandas", 
    io_manager_key="file_io"
    )
def extract_movie_genres() -> pd.DataFrame:
    # Read the CSV file using Pandas
    df = pd.read_csv("./data/summer_movie_genres.csv")
    
    # Log some metadata
    metadata = {
        "row_count": len(df),
        "preview": MetadataValue.md(df.head().to_markdown())
    }
    
    # Return the DataFrame as an output
    yield Output(df, metadata=metadata)
    
    # count check
    yield AssetCheckResult(
        passed=bool(df.shape[0] == 1585),
        severity=AssetCheckSeverity.WARN,
        description="Count check",
    )
    
@asset(
    check_specs=[AssetCheckSpec(name="check_count", asset="extract_movie")],
    group_name="extract", 
    compute_kind="pandas", 
    io_manager_key="file_io"
    )
def extract_movie() -> pd.DataFrame:
    # Read the CSV file using Pandas
    df = pd.read_csv("./data/summer_movies.csv")
    
    print(df['timestamp'].unique())
    
    # Log some metadata
    metadata = {
        "row_count": len(df),
        "preview": MetadataValue.md(df.head().to_markdown())
    }
    # Return the DataFrame as an output
    yield Output(df, metadata=metadata)
    
    # Count check
    yield AssetCheckResult(
        passed=bool(df.shape[0] == 905),
        severity=AssetCheckSeverity.WARN,
        description="Count check",
    )

@asset(
    check_specs=[AssetCheckSpec(name="key_notnull", asset="summer_movie_genres")],
    group_name="stg",
    compute_kind="pandas", 
    io_manager_key="db_io"
    )
def summer_movie_genres(context, extract_movie_genres: pd.DataFrame) -> pd.DataFrame:
    """Transform and Stage Data into Postgres."""
    try:
        context.log.info(extract_movie_genres.head())
        df = extract_movie_genres
        
        metadata = {
            "row_count": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
        yield Output(df, metadata=metadata)
        
        yield AssetCheckResult(
            passed=bool(df["tconst"].notnull().all()),
            severity=AssetCheckSeverity.WARN,
            description="key notnull",
            metadata = {
                "num_rows": len(df),
                "num_empty": len(df["tconst"].notnull())
            }
        )
    except Exception as e:
        context.log.info(str(e))

@asset(
    check_specs=[AssetCheckSpec(name="key_notnull", asset="summer_movies")],
    group_name="stg", 
    compute_kind="pandas", 
    io_manager_key="db_io",
    partitions_def=Daily_partition
    )
def summer_movies(context, extract_movie: pd.DataFrame) -> pd.DataFrame:
    """Transform and Stage Data into Postgres."""
    try:
        context.log.info(extract_movie.head())
        df = extract_movie
        
        metadata = {
            "row_count": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
        
        df['runtime_minutes'] = df['runtime_minutes'].fillna(df['runtime_minutes'].mean())
        df['year'] = df['year'].fillna(9999)
        # df['timestamp'] = df['timestamp'].apply(parse_date)
        
        yield Output(df, metadata=metadata)
        
        yield AssetCheckResult(
            passed=bool(df["tconst"].notnull().all()),
            severity=AssetCheckSeverity.WARN,
            description="key notnull",
            metadata = {
                "num_rows": len(df),
                "num_empty": len(df["tconst"].notnull())
            }
        )
    except Exception as e:
        context.log.info(str(e))

@asset (
    check_specs=[AssetCheckSpec(name="check_count", asset="transform_movie_data")],
    group_name="transformation", 
    compute_kind="pandas",
    deps = ["summer_movie_genres", "summer_movies"], 
    io_manager_key="file_io"
    )
def transform_movie_data(context: AssetExecutionContext) -> pd.DataFrame:
    
    with db_conn.get_sql_conn().connect() as connection:
        summer_movie_genres_data = pd.read_sql("SELECT * FROM summer_movie_genres", connection)
        
        summer_movies_data = pd.read_sql("SELECT * FROM summer_movies", connection)
    
    # Perform the join operation
    joined_data = pd.merge(summer_movie_genres_data, summer_movies_data, on="tconst")
    
    # Log some metadata about the joined data
    metadata = {
            "row_count": len(joined_data),
            "preview": MetadataValue.md(joined_data.head().to_markdown())
    }
        
    yield Output(joined_data, metadata=metadata)
    
    yield AssetCheckResult(
        passed=bool(joined_data.shape[0] == 1585),
        severity=AssetCheckSeverity.WARN,
        description="Count check",
    )

@asset(
    check_specs=[AssetCheckSpec(name="check_count", asset="joined_movie_genres")],
    group_name="load", 
    compute_kind="pandas", 
    io_manager_key="db_io"
    )
def joined_movie_genres(context, transform_movie_data: pd.DataFrame) -> pd.DataFrame:
    """Transform and Stage Data into Postgres."""
    try:
        context.log.info(transform_movie_data.head())
        df = transform_movie_data
        
        metadata = {
            "row_count": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
        
        yield Output(df, metadata=metadata)
        
        yield AssetCheckResult(
            passed=bool(df.shape[0] == 1585),
            severity=AssetCheckSeverity.WARN,
            description="Count check",
        )
    except Exception as e:
        context.log.info(str(e))
        