import pandas as pd
from db import get_engine, get_tables

source_engine = get_engine(database="source")  
result_engine = get_engine(database="result")  
tables = get_tables(database="source") 
results = []

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)

    df['date'] = pd.to_datetime(df['date'],format="%Y-%m-%d_%H-%M-%S")

    df = df.sort_values('date')

    first_price = df['close'].iloc[0]
    last_price  = df['close'].iloc[-1]
    yearly_return = ((last_price - first_price) / first_price) * 100

    results.append({
        'ticker': table,
        'first_close_price': first_price,
        'last_close_price': last_price,
        'yearly_return': yearly_return
    })

returns_df = pd.DataFrame(results)

returns_df.to_sql("yearly_returns", result_engine, if_exists="replace", index=False)
print("✅ Yearly returns saved to DB!")

top10_green = returns_df.sort_values(by='yearly_return', ascending=False).head(10)
top10_loss = returns_df.sort_values(by='yearly_return', ascending=True).head(10)

top10_green.to_sql("top10_green_stocks", result_engine, if_exists="replace", index=False)
top10_loss.to_sql("top10_loss_stocks", result_engine, if_exists="replace", index=False)
print("✅ Top 10 gainers & losers saved to DB!")

green_count = (returns_df['yearly_return'] > 0).sum()
red_count = (returns_df['yearly_return'] < 0).sum()

all_prices = []
all_volumes = []

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)
    all_prices.append(df['close'].mean())
    all_volumes.append(df['volume'].mean())

overall_avg_price = sum(all_prices) / len(all_prices)
overall_avg_volume = sum(all_volumes) / len(all_volumes)

print(f"Overall Average Price: {overall_avg_price:.2f}")
print(f"Overall Average Volume: {overall_avg_volume:.2f}")

market_summary = pd.DataFrame({
    "Metric": ["Green Stocks", "Red Stocks", "Average Price", "Average Volume"],
    "Value": [green_count, red_count, overall_avg_price, overall_avg_volume]
})

market_summary.to_sql("market_summary", result_engine, if_exists="replace", index=False)
print("Market summary saved to DB!")
