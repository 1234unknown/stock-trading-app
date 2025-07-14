import streamlit as st
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="Stock Analysis Application",
    layout="wide"
)

# --- API Key and Base URL ---
FMP_API_KEY = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# --- Helper Function to Fetch Stock Data ---
def get_stock_data(ticker):
    """Fetches current price and dividend yield from Financial Modeling Prep."""
    try:
        # Fetch quote for current price
        quote_url = f"{FMP_BASE_URL}/quote/{ticker}?apikey={FMP_API_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json()
        if not quote_data:
            return None, None
        current_price = quote_data[0].get('price')

        # Fetch company profile for dividend yield
        profile_url = f"{FMP_BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_response = requests.get(profile_url)
        profile_data = profile_response.json()
        if not profile_data:
            return current_price, 0.0

        # FMP gives last annual dividend, so we calculate yield
        last_div = profile_data[0].get('lastDiv', 0)
        dividend_yield = (last_div / current_price) * 100 if current_price > 0 else 0

        return current_price, dividend_yield
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None, None

# --- DRIP Calculator Logic ---
def run_drip_calculation(initial_investment, monthly_contribution, investment_period, dividend_yield_pct, stock_growth_pct, tax_rate_pct, current_price):
    # Convert percentages to decimals
    annual_dividend_rate = dividend_yield_pct / 100
    annual_stock_growth_rate = stock_growth_pct / 100
    tax_rate = tax_rate_pct / 100

    # Initial values
    total_shares = initial_investment / current_price
    total_invested = initial_investment
    total_dividends_earned = 0
    portfolio_value = initial_investment

    # Data for chart
    projection_data = {'Year': [], 'Portfolio Value': [], 'Total Contributions': []}

    for year in range(1, int(investment_period) + 1):
        # Add contributions for the year
        yearly_contribution = monthly_contribution * 12
        total_invested += yearly_contribution
        total_shares += yearly_contribution / portfolio_value * total_shares if portfolio_value > 0 else 0

        # Calculate and reinvest dividends
        dividends_this_year = total_shares * (portfolio_value / total_shares * annual_dividend_rate if total_shares > 0 else 0)
        net_dividends = dividends_this_year * (1 - tax_rate)
        total_dividends_earned += net_dividends
        reinvested_shares = net_dividends / (portfolio_value / total_shares if total_shares > 0 else 1)
        total_shares += reinvested_shares

        # Apply stock price growth [cite: 30]
        portfolio_value = total_shares * (portfolio_value / total_shares if total_shares > 0 else 1) * (1 + annual_stock_growth_rate)

        # Store data for chart [cite: 31, 35]
        projection_data['Year'].append(year)
        projection_data['Portfolio Value'].append(round(portfolio_value, 2))
        projection_data['Total Contributions'].append(round(total_invested, 2))

    return {
        "final_value": portfolio_value,
        "total_contributions": total_invested,
        "total_dividends": total_dividends_earned,
        "projection_df": pd.DataFrame(projection_data)
    }


# --- Streamlit User Interface ---
st.title("DRIP (Dividend Reinvestment Plan) Calculator")
st.write("Project the long-term growth of your investments by simulating dividend reinvestment.")

# --- User Inputs --- [cite: 11]
col1, col2 = st.columns(2)

with col1:
    st.header("Inputs")
    ticker = st.text_input("Stock Ticker Symbol", "AAPL").upper()
    initial_investment = st.number_input("Initial Investment Amount ($)", min_value=0.0, value=10000.0, step=1000.0)
    monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=100.0, step=50.0)
    investment_period = st.slider("Investment Period (Years)", 1, 50, 10)

with col2:
    st.header("Assumptions")
    # Fetch data when ticker is entered
    current_price, fetched_yield = get_stock_data(ticker) if ticker else (None, None)

    if current_price:
        st.success(f"Successfully fetched data for {ticker}. Current Price: ${current_price:,.2f}")

    # Allow user to edit fetched data [cite: 16]
    dividend_yield = st.number_input("Expected Annual Dividend Yield (%)", min_value=0.0, value=float(fetched_yield) if fetched_yield else 1.5, step=0.1, format="%.2f")
    stock_growth = st.number_input("Expected Annual Stock Price Growth (%)", min_value=0.0, value=8.0, step=0.5)
    tax_rate = st.slider("Dividend Tax Rate (%)", 0, 50, 15)


# --- Calculate and Display Results ---
if st.button("Calculate Projection", type="primary"):
    if current_price and isinstance(current_price, (int, float)):
        with st.spinner("Calculating..."):
            results = run_drip_calculation(
                initial_investment,
                monthly_contribution,
                investment_period,
                dividend_yield,
                stock_growth,
                tax_rate,
                current_price
            )

            st.header("Projection Results")

            # Display summary metrics [cite: 32]
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Final Portfolio Value", f"${results['final_value']:,.2f}")
            metric_col2.metric("Total Contributions", f"${results['total_contributions']:,.2f}")
            metric_col3.metric("Total Dividend Earnings (Net)", f"${results['total_dividends']:,.2f}")

            # Display projection chart [cite: 34]
            st.subheader("Portfolio Growth Over Time")
            chart_df = results['projection_df'].set_index('Year')
            st.line_chart(chart_df)

    else:
        st.error("Could not fetch stock data. Please check the ticker symbol and try again.")
