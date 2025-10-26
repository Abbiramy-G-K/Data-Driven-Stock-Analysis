import pandas as pd
from db import get_engine, get_tables

# -------------------------
# 0. Connect to DB
# -------------------------
source_engine = get_engine(database="source")  # raw stock data
result_engine = get_engine(database="result")  # processed results
tables = get_tables(database="source") 


volatility_list = []

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)    
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    # df = df.dropna(subset=['date'])
    df = df.sort_values(by='date')
    
    # Calculate daily returns
    df['daily_return'] = df['close'].pct_change()
    
    # Calculate volatility (standard deviation of daily returns)
    volatility = df['daily_return'].std()
    
    # Store result
    volatility_list.append({
        'ticker': table,
        'volatility': volatility
    })

# Create a DataFrame of volatility for all stocks
volatility_df = pd.DataFrame(volatility_list)
volatility_df.to_sql("volatility_analysis", result_engine, if_exists="replace", index=False)

top10_volatile = volatility_df.sort_values(by='volatility', ascending=False).head(10)
print(top10_volatile)

top10_volatile.to_sql("top10_volatile_stocks",result_engine,if_exists="replace", index=False)
print("✅ Volatility data saved!")

