import pandas as pd
from db import get_engine, get_tables

source_engine = get_engine(database="source") 
result_engine = get_engine(database="result") 
tables = get_tables(database="source") 

cumulative_list = []

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)    
    
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    df = df.sort_values(by='date')
    
    df['daily_return'] = df['close'].pct_change()

    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1

    cumulative = df['cumulative_return'].iloc[-1]

    cumulative_list.append({
        'ticker': table,
        'cumulative': cumulative
    })

cumulative_df = pd.DataFrame(cumulative_list)
cumulative_df.to_sql("cumulative_analysis", result_engine, if_exists="replace", index=False)

top5_cumulative = cumulative_df.sort_values(by='cumulative', ascending=False).head(5)
print(top5_cumulative)

top5_cumulative.to_sql("top5_cumulative_stocks", result_engine, if_exists="replace", index=False)
print("cumulative data saved!")


