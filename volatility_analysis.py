import pandas as pd
from db import get_engine, get_tables

source_engine = get_engine(database="source")  
result_engine = get_engine(database="result")  
tables = get_tables(database="source") 


volatility_list = []

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)    
    
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    df = df.sort_values(by='date')
    
    df['daily_return'] = df['close'].pct_change()
    
    volatility = df['daily_return'].std()
    
    volatility_list.append({
        'ticker': table,
        'volatility': volatility
    })

volatility_df = pd.DataFrame(volatility_list)
volatility_df.to_sql("volatility_analysis", result_engine, if_exists="replace", index=False)

top10_volatile = volatility_df.sort_values(by='volatility', ascending=False).head(10)
print(top10_volatile)

top10_volatile.to_sql("top10_volatile_stocks",result_engine,if_exists="replace", index=False)
print("✅ Volatility data saved!")

