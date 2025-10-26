import pandas as pd
from db import get_engine, get_tables

# -------------------------
# 0. Connect to DB
# -------------------------
source_engine = get_engine(database="source")  # raw stock data
result_engine = get_engine(database="result")  # processed results
tables = get_tables(database="source") 

# Start with an empty DataFrame
all_stocks = pd.DataFrame()

# Loop through each CSV
for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`", source_engine)
    
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    
    # Sort by date (important so pct_change works correctly)
    df = df.sort_values(by='date')
    
    # Keep only date and close columns
    df = df[['date', 'close']]
    
    # Rename close column to the ticker name
    df.rename(columns={'close': table}, inplace=True)
    
    # Merge into the main DataFrame
    if all_stocks.empty:
        all_stocks = df
    else:
        all_stocks = pd.merge(all_stocks, df, on='date', how='outer')

# Set date as the index
all_stocks.set_index('date', inplace=True)

print("Combined data shape:", all_stocks.shape)
print(all_stocks.head())

# Calculate daily percentage changes
returns = all_stocks.pct_change()

print("Daily returns calculated")
print(returns.head())

# Compute correlation between all stocks
corr_matrix = returns.corr()

print("Correlation matrix calculated")
print(corr_matrix.head())

all_stocks.to_sql("combined_closing_price", result_engine, if_exists="replace", index=False)
returns.to_sql("daily_returns", result_engine, if_exists="replace", index=False)
corr_matrix.to_sql("correlation_matrix", result_engine, if_exists="replace", index=False)

print("combined data, daily returns and correlation matrix saved into db")

# import seaborn as sns
# import matplotlib.pyplot as plt

# plt.figure(figsize=(14,10))
# sns.heatmap(corr_matrix, cmap='coolwarm', annot=False)
# plt.title("Stock Price Correlation Heatmap")
# plt.tight_layout()
# plt.show()
