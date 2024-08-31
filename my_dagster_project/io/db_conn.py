from sqlalchemy import create_engine

def get_sql_conn():
    """return db connection."""
    #get password from environmnet var
    db_user = "sql12728197"
    db_password = "7fz7Efym5T"
    db_host = "sql12.freesqldatabase.com"
    db_port = 3306
    db_name = "sql12728197"
    
    connection_string = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    #
    engine = create_engine(connection_string)
    try:
        return engine
    except:
        print("Error connecting to SQL Server")