from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

# Credentials
USERNAME = "root"
PASSWORD = "Abbivimi@7"
HOST = "localhost"
PORT = 3306
SOURCE_DB = "stock_analysis"
RESULTS_DB = "stock_results"
SECTOR_DB = "sector_ticker"


# Encode password
PASSWORD = quote_plus(PASSWORD)

# Create a single engine instance
source_engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{SOURCE_DB}")
result_engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{RESULTS_DB}")
sector_engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{SECTOR_DB}")

def fetch_table(table_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, sector_engine)
    return df


def get_engine(database="source"):
    if database == "source":
        return source_engine
    elif database == "result":
        return result_engine
    else:
        raise ValueError("Unknown database. Use 'source' or 'result'.")
def get_tables(database = "source"):
    engine = get_engine(database)
    query = "SHOW TABLES"
    df = pd.read_sql(query, engine)
    table_list = df.iloc[:, 0].tolist() 
    return table_list

def get_all_columns(database = "source"):
    engine = get_engine(database)
    tables = get_tables()  # get all table names
    columns_info = {}

    for table in tables:
        query = f"SHOW COLUMNS FROM `{table}`"
        df = pd.read_sql(query, engine)
        columns_info[table] = df['Field'].tolist()  # list of column names

    return columns_info

