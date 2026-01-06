import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import holidays

# Import custom modules
from utils.data_processor import DataProcessor
from utils.forecaster import FleetForecaster
from utils.visualization import Visualizer
from utils.export import ExportManager

# Page configuration
st.set_page_config(
    page_title="Fleet Forecasting Engine",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for green theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-green: #2E7D32;
        --secondary-green: #66BB6A;
        --dark-green: #1B5E20;
        --light-green: #F1F8F4;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E7D32;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: #2E7D32;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #1B5E20;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F1F8F4;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #E8F5E9;
        border-left: 4px solid #66BB6A;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        border-top: 1px solid #E0E0E0;
        margin-top: 3rem;
    }
    
    .footer a {
        color: #2E7D32;
        text-decoration: none;
        font-weight: bold;
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess {
        background-color: #E8F5E9;
        border-left-color: #2E7D32;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'forecast_results' not in st.session_state:
    st.session_state.forecast_results = None
if 'api_calls_count' not in st.session_state:
    st.session_state.api_calls_count = 0

# Sidebar navigation
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <h2 style='color: #2E7D32;'>🚛 Fleet Forecasting</h2>
    <p style='color: #666; font-size: 0.9rem;'>AI-Powered Fleet Prediction</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home & Setup", "📤 Data Upload & Explorer", "🔮 Forecasting Engine", "📊 Results & Download"],
    label_visibility="collapsed"
)

# API calls counter
if st.session_state.api_calls_count > 0:
    st.sidebar.markdown("---")
    st.sidebar.metric("API Calls Used", st.session_state.api_calls_count)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.8rem; color: #666; padding: 1rem;'>
    <strong>Tips:</strong><br>
    • Hover over ℹ️ icons for help<br>
    • Use sample data to test<br>
    • Date format: dd/mm/yyyy<br>
    • Min 30 days for daily data<br>
    • Min 12 months for monthly
</div>
""", unsafe_allow_html=True)

# Page routing
if page == "🏠 Home & Setup":
    from pages import home
    home.render()
elif page == "📤 Data Upload & Explorer":
    from pages import data_upload
    data_upload.render()
elif page == "🔮 Forecasting Engine":
    from pages import forecasting
    forecasting.render()
elif page == "📊 Results & Download":
    from pages import results
    results.render()

# Footer
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p>Powered by <strong>TimeGPT</strong> | Developed by <strong>Irsandi Habibie</strong></p>
    <p style='font-size: 0.8rem; color: #999; margin-top: 0.5rem;'>
        © 2025 Fleet Forecasting Engine. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)
