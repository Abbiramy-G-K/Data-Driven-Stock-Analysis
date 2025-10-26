import pandas as pd
from db import get_engine, get_tables

source_engine = get_engine(database="source")  
result_engine = get_engine(database="result")  
tables = get_tables(database="source") 

monthly_list = []

# Loop through each stock file
for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`",source_engine)
        
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    
    # Sort by date to ensure correct order
    df = df.sort_values(by='date')
    
    # Create a "year-month" column
    df['year_month'] = df['date'].dt.to_period('M')
    
    # Group by each month
    grouped = df.groupby('year_month')
    
    # Calculate monthly return for each month
    for month, group in grouped:
        start_price = group.iloc[0]['close']
        end_price = group.iloc[-1]['close']
        monthly_return = ((end_price - start_price) / start_price) * 100
        
        # Store the results
        monthly_list.append({
            'ticker': table,
            'month': str(month),
            'monthly_return': monthly_return
        })

# Convert list to DataFrame
monthly_df = pd.DataFrame(monthly_list)

# Save for future use
monthly_df.to_sql("monthly_returns",result_engine,if_exists="replace", index=False)

print("✅ Monthly returns calculated!")
print(monthly_df.head())

# Load the monthly returns file
monthly_df = pd.read_sql("SELECT * FROM monthly_returns",result_engine)

# Get all unique months
months = monthly_df['month'].unique()

# Create two lists for gainers and losers
gainers_list = []
losers_list = []

# Loop through each month
for m in months:
    data_m = monthly_df[monthly_df['month'] == m]
    
    # Top 5 gainers
    top5_gainers = data_m.sort_values(by='monthly_return', ascending=False).head(5)
    top5_gainers['rank'] = range(1, 6)
    top5_gainers['type'] = 'Gainer'
    
    # Top 5 losers
    top5_losers = data_m.sort_values(by='monthly_return', ascending=True).head(5)
    top5_losers['rank'] = range(1, 6)
    top5_losers['type'] = 'Loser'
    
    gainers_list.append(top5_gainers)
    losers_list.append(top5_losers)

# Combine results
top_gainers_df = pd.concat(gainers_list)
top_losers_df = pd.concat(losers_list)

# Save them
top_gainers_df.to_sql("top5_gainers_monthwise",result_engine, if_exists="replace", index=False)
top_losers_df.to_sql("top5_losers_monthwise",result_engine, if_exists="replace", index=False)

print("✅ Top 5 gainers and losers saved!")




# import matplotlib.pyplot as plt
# import seaborn as sns

# # Pick a month to visualize
# month_to_plot = '2023-10'

# data_to_plot = pd.concat([
#     top_gainers_df[top_gainers_df['month'] == month_to_plot],
#     top_losers_df[top_losers_df['month'] == month_to_plot]
# ])

# plt.figure(figsize=(10,6))
# sns.barplot(data=data_to_plot, x='ticker', y='monthly_return', hue='type')
# plt.title(f"Top 5 Gainers and Losers - {month_to_plot}")
# plt.xticks(rotation=45)
# plt.ylabel("Monthly Return (%)")
# plt.tight_layout()
# plt.show()

