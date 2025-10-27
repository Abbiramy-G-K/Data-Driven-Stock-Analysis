import pandas as pd
from db import get_engine, get_tables

source_engine = get_engine(database="source")  
result_engine = get_engine(database="result")  
tables = get_tables(database="source") 

monthly_list = []

for table in tables:
    df = pd.read_sql(f"SELECT * FROM `{table}`",source_engine)
        
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d_%H-%M-%S")
    
    df = df.sort_values(by='date')
    
    df['year_month'] = df['date'].dt.to_period('M')
    
    grouped = df.groupby('year_month')
    
    for month, group in grouped:
        start_price = group.iloc[0]['close']
        end_price = group.iloc[-1]['close']
        monthly_return = ((end_price - start_price) / start_price) * 100
        
        monthly_list.append({
            'ticker': table,
            'month': str(month),
            'monthly_return': monthly_return
        })

monthly_df = pd.DataFrame(monthly_list)

monthly_df.to_sql("monthly_returns",result_engine,if_exists="replace", index=False)

print("✅ Monthly returns calculated!")
print(monthly_df.head())

monthly_df = pd.read_sql("SELECT * FROM monthly_returns",result_engine)

months = monthly_df['month'].unique()

gainers_list = []
losers_list = []

for m in months:
    data_m = monthly_df[monthly_df['month'] == m]
    
    top5_gainers = data_m.sort_values(by='monthly_return', ascending=False).head(5)
    top5_gainers['rank'] = range(1, 6)
    top5_gainers['type'] = 'Gainer'
    
    top5_losers = data_m.sort_values(by='monthly_return', ascending=True).head(5)
    top5_losers['rank'] = range(1, 6)
    top5_losers['type'] = 'Loser'
    
    gainers_list.append(top5_gainers)
    losers_list.append(top5_losers)

top_gainers_df = pd.concat(gainers_list)
top_losers_df = pd.concat(losers_list)

top_gainers_df.to_sql("top5_gainers_monthwise",result_engine, if_exists="replace", index=False)
top_losers_df.to_sql("top5_losers_monthwise",result_engine, if_exists="replace", index=False)

print("✅ Top 5 gainers and losers saved!")




