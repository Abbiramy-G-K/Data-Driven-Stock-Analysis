import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from plotly.tools import mpl_to_plotly
import plotly.graph_objects as go
from db import get_engine

st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")
st.title("Stock Analysis Dashboard")

# -------------------------------------------------------------------
# Database Connections
# -------------------------------------------------------------------
result_engine = get_engine(database="result")
source_engine = get_engine(database="source")

@st.cache_data(ttl=300)
def load_table(table_name):

    try:
        df = pd.read_sql_table(table_name, con=result_engine)
        return df
    except Exception:
        try:
            return pd.read_sql(f"SELECT * FROM `{table_name}`", con=result_engine)
        except Exception as e:
            st.error(f"Could not load table `{table_name}`: {e}")
            return pd.DataFrame()

# -------------------------------------------------------------------
# Panel 1: Volatility — Top 10 Most Volatile Stocks
# -------------------------------------------------------------------
st.header("1) Volatility — Top 10 Most Volatile Stocks")
vol_df = load_table("top10_volatile_stocks")

chart_type = st.radio(
    "Select Visualization Type:",
    ("Matplotlib", "Plotly"),
    horizontal=True
)

if chart_type == "Matplotlib":
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.bar(x = vol_df['ticker'], height = vol_df['volatility'], color='skyblue')
    plt.subplots_adjust(left=10, right=11, top=6, bottom=5)
    ax.set_xlabel("Ticker", fontsize = 5, labelpad = 8)
    ax.set_ylabel("Volatility", fontsize = 5, labelpad= 6)
    ax.set_title("Top 10 Volatility Analysis", fontsize=5, pad = 3, fontweight="bold")
    ax.tick_params(axis='x', labelsize=5, length = 2, width = 2)
    ax.tick_params(axis='y', labelsize=5, length = 2, width = 2)
    fig.tight_layout()
    st.pyplot(fig, bbox_inches = 'tight')

else:

    fig_plotly = go.Figure(
        data=[go.Bar(x=vol_df['ticker'], y=vol_df['volatility'], marker_color='lightskyblue')]
    )
    fig_plotly.update_layout(
        title="Top 10 Volatility Analysis",
        xaxis_title="Ticker",
        yaxis_title="Volatility"
    )
    st.plotly_chart(fig_plotly, use_container_width=True)
# -------------------------------------------------------------------
# Panel 2: Cumulative Return Over Time — Top 5 Performers
# -------------------------------------------------------------------
st.header("2) Cumulative Return Over Time — Top 5 Performers")

top5_cum = load_table("top5_cumulative_stocks")
combined_prices = load_table("combined_closing_price")

if top5_cum.empty or combined_prices.empty:
    st.info("Required tables (`top5_cumulative_stocks`, `combined_closing_price`) not found in result DB.")

else:
    top5_tickers = top5_cum["ticker"].tolist()

    present_tickers = [t for t in top5_tickers if t in combined_prices.columns]

    if not present_tickers:
        st.warning("None of the top 5 tickers found in `combined_closing_price`.")
    else:
        viz_option = st.radio(
            "Choose Visualization Type:",
            ("Matplotlib", "Plotly"),
            horizontal=True
        )

        normalized_data = combined_prices[present_tickers].copy()
        normalized_data = normalized_data / normalized_data.iloc[0] 

        if viz_option == "Matplotlib":
            fig, ax = plt.subplots(figsize=(8, 2))  
            for ticker in present_tickers:
                ax.plot(normalized_data.index,normalized_data[ticker], label=ticker)

            ax.set_title("Cumulative Return Over Time — Top 5 Performing Stocks",
                         fontsize=5, fontweight="bold", pad=8)
            ax.set_xlabel("Time (Index progression)", fontsize=5)
            ax.set_ylabel("Closing Price", fontsize=5)
            ax.legend(title="Ticker", loc="upper left", fontsize=5)
            ax.tick_params(axis='x', labelsize=5, length = 2, width = 2)
            ax.tick_params(axis='y', labelsize=5, length = 2, width = 2)

            ax.grid(True, linestyle="--", alpha=0.6)
            fig.tight_layout()

            st.pyplot(fig, use_container_width=True)

        else:
            fig = go.Figure()
            for ticker in present_tickers:
                fig.add_trace(go.Scatter(
                    x=normalized_data.index,
                    y=normalized_data[ticker],
                    mode='lines',
                    name=ticker
                ))

            fig.update_layout(
                title="Cumulative Return Over Time — Top 5 Performing Stocks",
                xaxis_title="Time (Index progression)",
                yaxis_title="Closing Price",
                hovermode="x unified",
                template="plotly_white",
                margin=dict(l=50, r=50, t=80, b=50)
            )

            st.plotly_chart(fig, use_container_width=True)
# -------------------------------------------------------------------
# Panel 3: Sector-wise Performance
# -------------------------------------------------------------------
st.header("3) Sector-wise Performance")
sector_df = load_table("sector_performance")

if not sector_df.empty:
    viz_option = st.radio(
        "Choose Visualization Type:",
        ("Matplotlib", "Plotly"),
        horizontal=True,
        key="sector_viz_option"
    )

    if viz_option == "Matplotlib":
        fig, ax = plt.subplots(figsize=(8, 2))
        ax.bar(sector_df["sector"], sector_df["yearly_return"], color="orange")
        ax.set_title("Average Yearly Return by Sector", fontsize=5, fontweight="bold", pad=8)
        ax.set_xlabel("Sector", fontsize=5)
        ax.set_ylabel("Average Yearly Return", fontsize=5)
        ax.tick_params(axis='x', labelsize=5, length = 2, width = 2)
        ax.tick_params(axis='y', labelsize=5, length = 2, width = 2)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout()

        st.pyplot(fig, use_container_width=True)

    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sector_df["sector"],
            y=sector_df["yearly_return"],
            marker_color="orange",
            text=[f"{v:.2%}" for v in sector_df["yearly_return"]],
            textposition="auto"
        ))

        fig.update_layout(
            title="Average Yearly Return by Sector",
            xaxis_title="Sector",
            yaxis_title="Average Yearly Return",
            template="plotly_white",
            margin=dict(l=50, r=50, t=80, b=100)
        )

        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("`sector_performance` table not found or could not be computed.")
# -------------------------------------------------------------------
# Panel 4: Stock Price Correlation (Heatmap)
# -------------------------------------------------------------------
import seaborn as sns

st.header("4) Stock Price Correlation Heatmap")

correlation_matrix = load_table("correlation_matrix")

if correlation_matrix.empty:
    st.warning("`correlation_matrix` table not found in the result database.")
else:
    st.markdown("""
    **Objective:**  
    This visualization shows the correlation between the stock prices of different companies.  
    A darker color indicates a stronger positive correlation, while lighter or blue tones indicate weaker or negative correlation.
    """)

    viz_option = st.radio(
        "Choose Visualization Type:",
        ("Matplotlib (Seaborn)", "Plotly"),
        horizontal=True,
        key="corr_viz_option"
    )

    if viz_option == "Matplotlib (Seaborn)":
        fig, ax = plt.subplots(figsize=(8, 2))
        sns.heatmap(
            correlation_matrix,
            annot=False,
            cmap="coolwarm",
            cbar=True,
            ax=ax
        )
        ax.set_title("Stock Price Correlation Heatmap", fontsize=5, fontweight="bold", pad=8)
        ax.tick_params(axis='x', labelsize=5, length = 2, width = 2)
        ax.tick_params(axis='y', labelsize=5, length = 2, width = 2)

        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

    else:
        fig = go.Figure(
            data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale="RdBu",
                zmin=-1, zmax=1,
                colorbar=dict(title="Correlation Coefficient")
            )
        )

        fig.update_layout(
            title="Stock Price Correlation Heatmap",
            xaxis_title="Stocks",
            yaxis_title="Stocks",
            template="plotly_white",
            margin=dict(l=80, r=80, t=80, b=80),
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------
# Panel 5: Top 5 Gainers and Losers (Month-wise)
# -------------------------------------------------------------------
st.header("4) Monthly Top 5 Gainers and Losers")

gainers_df = load_table("top5_gainers_monthwise")
losers_df = load_table("top5_losers_monthwise")

if not gainers_df.empty and not losers_df.empty:
    months = sorted(gainers_df['month'].unique())
    selected_month = st.selectbox("Select Month:", months)

    combined = pd.concat([
        gainers_df[gainers_df['month'] == selected_month],
        losers_df[losers_df['month'] == selected_month]
    ])

    chart_type4 = st.radio("Select visualization type:", ["Matplotlib", "Plotly"], horizontal=True, key="gainers_losers_type")

    if chart_type4 == "Matplotlib":
        fig, ax = plt.subplots(figsize=(8, 2))
        sns.barplot(data=combined, x="ticker", y="monthly_return", hue="type", ax=ax)
        ax.set_title(f"Top 5 Gainers and Losers — {selected_month}", fontsize = 5, fontweight = "bold", pad = 8)
        ax.set_xlabel("Ticker", fontsize = 5)
        ax.set_ylabel("Monthly Return (%)", fontsize = 5)
        ax.tick_params(axis='x', labelsize=5, length = 2, width = 2)
        ax.tick_params(axis='y', labelsize=5, length = 2, width = 2)
        fig.tight_layout()
        st.pyplot(fig)
    else:
        fig_plotly = go.Figure()
        for typ, color in zip(["Gainer", "Loser"], ["green", "red"]):
            data_subset = combined[combined["type"] == typ]
            fig_plotly.add_trace(go.Bar(x=data_subset["ticker"],
                                        y=data_subset["monthly_return"],
                                        name=typ,
                                        marker_color=color))
        fig_plotly.update_layout(title=f"Top 5 Gainers and Losers — {selected_month}",
                                 xaxis_title="Ticker", yaxis_title="Monthly Return (%)",
                                 barmode="group")
        st.plotly_chart(fig_plotly, use_container_width=True)
else:
    st.warning("Required tables for monthly gainers/losers not found.")