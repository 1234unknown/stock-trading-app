import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

st.set_page_config(layout="wide")

st.title("Stock Analysis Application")
st.write("This is the foundation for our DRIP, AI Entry, and Options Spread tools.")

# --- Section to verify API Keys are loaded ---
st.header("API Key Check")

# Get keys from environment variables
twelve_data_key = os.getenv("TWELVE_DATA_API_KEY")
polygon_io_key = os.getenv("POLYGON_IO_API_KEY")
fmp_key = os.getenv("FINANCIAL_MODELING_PREP_API_KEY")

if twelve_data_key:
    st.success(f"Twelve Data API Key Loaded Successfully. Starts with: {twelve_data_key[:4]}")
else:
    st.error("Twelve Data API Key not found.")

if polygon_io_key:
    st.success(f"Polygon.io API Key Loaded Successfully. Starts with: {polygon_io_key[:4]}")
else:
    st.error("Polygon.io API Key not found.")

if fmp_key:
    st.success(f"Financial Modeling Prep API Key Loaded Successfully. Starts with: {fmp_key[:4]}")
else:
    st.error("Financial Modeling Prep API Key not found.")
