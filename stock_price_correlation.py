import pandas as pd
from db import get_engine, get_tables

source_engine = get_engine(database="source")  
result_engine = get_engine(database="result")  
tables = get_tables(database="source") 

all_stocks = pd.DataFrame()

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)
    
    
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    
    df = df.sort_values(by='date')
    
    df = df[['date', 'close']]
    
    df.rename(columns={'close': table}, inplace=True)
    
    if all_stocks.empty:
        all_stocks = df
    else:
        all_stocks = pd.merge(all_stocks, df, on='date', how='outer')

all_stocks.set_index('date', inplace=True)

print("Combined data shape:", all_stocks.shape)
print(all_stocks.head())

returns = all_stocks.pct_change()

print("Daily returns calculated")
print(returns.head())

corr_matrix = returns.corr()

print("Correlation matrix calculated")
print(corr_matrix.head())

all_stocks.to_sql("combined_closing_price", result_engine, if_exists="replace", index=False)
returns.to_sql("daily_returns", result_engine, if_exists="replace", index=False)
corr_matrix.to_sql("correlation_matrix", result_engine, if_exists="replace", index=False)

print("combined data, daily returns and correlation matrix saved into db")

