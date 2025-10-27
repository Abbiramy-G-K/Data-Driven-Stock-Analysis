import pandas as pd
from db import fetch_table, get_engine

df = fetch_table("sector_ticker")
result_engine = get_engine(database="result")  


print(df.head())

df['yearly_return'] = df['yearly_return'] / 100


sector_performance = (
    df.groupby("sector")['yearly_return']
      .mean()
      .reset_index()
      .sort_values(by='yearly_return', ascending=False)
)

print(sector_performance)

sector_performance.to_sql("sector_performance",result_engine, if_exists="replace", index=False)
print(" Sector-wise performance saved to sector_performance in DB")

