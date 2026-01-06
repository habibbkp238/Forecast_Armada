import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def render():
    """Render the Home & Setup page"""
    
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>🚛 Fleet Forecasting Engine</h1>
        <p>AI-Powered Fleet Usage Prediction with TimeGPT</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 👋 Welcome!")
        st.markdown("""
        This application helps you forecast fleet usage across different types, routes, and regions using 
        state-of-the-art AI models from TimeGPT.
        
        **Key Features:**
        - 🎯 Accurate forecasting with TimeGPT-1-long-horizon
        - 📊 Flexible aggregation levels (granular to high-level)
        - 🎄 Indonesian holiday integration
        - 📈 Interactive visualizations
        - 📥 Export to Excel/CSV
        - 🔄 Automatic fallback to Moving Average (MA-6)
        """)
    
    with col2:
        st.markdown("### 📋 Quick Stats")
        st.markdown("""
        <div class='metric-card'>
            <h3>Data Format</h3>
            <div class='value'>dd/mm/yyyy</div>
        </div>
        <div class='metric-card'>
            <h3>Min Data Points</h3>
            <div class='value'>30 days</div>
        </div>
        <div class='metric-card'>
            <h3>API Calls</h3>
            <div class='value'>1 per run</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Key Setup
    st.markdown("### 🔑 API Configuration")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key_input = st.text_input(
            "Enter your Nixtla API Key",
            type="password",
            value=st.session_state.api_key if st.session_state.api_key else "",
            help="Get your free API key from https://dashboard.nixtla.io"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        validate_button = st.button("✓ Validate", type="primary")
    
    if validate_button and api_key_input:
        with st.spinner("Validating API key..."):
            from utils.forecaster import FleetForecaster
            
            forecaster = FleetForecaster(api_key=api_key_input)
            is_valid, message = forecaster.validate_api_key()
            
            if is_valid:
                st.session_state.api_key = api_key_input
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                st.session_state.api_key = None
    
    elif not api_key_input and validate_button:
        st.warning("Please enter an API key")
    
    # Show API key status
    if st.session_state.api_key:
        st.success("✅ API Key configured and ready!")
    else:
        st.info("ℹ️ Please enter and validate your API key to use TimeGPT forecasting")
    
    st.markdown("""
    <div class='info-box'>
        <strong>💡 Don't have an API key?</strong><br>
        Get your free API key at <a href='https://dashboard.nixtla.io' target='_blank'>dashboard.nixtla.io</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sample Dataset Section
    st.markdown("### 📦 Sample Dataset")
    st.markdown("""
    Download a sample dataset to test the app or use as a template for your own data.
    """)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📥 Download Sample", type="secondary"):
            sample_data = generate_sample_data()
            csv = sample_data.to_csv(index=False)
            
            st.download_button(
                label="💾 Save Sample Data",
                data=csv,
                file_name=f"fleet_sample_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        with st.expander("ℹ️ Sample Data Structure"):
            st.markdown("""
            **Required Columns:**
            - `date` - Format: dd/mm/yyyy (e.g., 31/12/2024)
            - `company` - Company name
            - `origin` - Warehouse origin name
            - `destination` - City destination name
            - `province` - Province of destination
            - `region` - Region of destination
            - `fleet_type` - Type of fleet (categorical)
            - `qty` - Number of fleets used (integer)
            """)
    
    st.markdown("---")
    
    # Getting Started Guide
    st.markdown("### 🚀 Getting Started")
    
    with st.expander("📖 Step-by-Step Guide", expanded=False):
        st.markdown("""
        **Step 1: Setup API Key (Current Page)**
        - Enter your Nixtla API key above
        - Click "Validate" to test the connection
        
        **Step 2: Upload Data**
        - Go to "📤 Data Upload & Explorer" page
        - Upload your CSV or Excel file
        - Ensure dates are in dd/mm/yyyy format
        - Review data quality report
        
        **Step 3: Configure Forecast**
        - Go to "🔮 Forecasting Engine" page
        - Select aggregation level
        - Set forecast horizon
        - Enable holiday features (recommended)
        - Choose model (TimeGPT recommended)
        
        **Step 4: Review Results**
        - Go to "📊 Results & Download" page
        - View interactive charts
        - Download detailed or summary reports
        - Export as Excel or CSV
        """)
    
    # System Requirements
    with st.expander("⚙️ Data Requirements"):
        st.markdown("""
        **Minimum Data Requirements:**
        - Daily data: At least 30 consecutive days
        - Monthly data: At least 12 months
        - No gaps in critical series (auto-filled if missing)
        
        **Recommended:**
        - 1-3 years of historical data for best results
        - Consistent data quality across all series
        - Include major holidays in the date range
        
        **File Format:**
        - CSV or Excel (.xlsx, .xls)
        - UTF-8 encoding recommended
        - Maximum file size: 200 MB
        """)
    
    # Tips and Best Practices
    with st.expander("💡 Tips & Best Practices"):
        st.markdown("""
        **For Best Forecast Accuracy:**
        1. Use TimeGPT-1-long-horizon for datasets with 3+ years
        2. Enable Indonesian holiday features
        3. Ensure data is clean and complete
        4. Choose appropriate aggregation level
        
        **Performance Optimization:**
        - Filter data before forecasting if you have many series
        - Use batch forecasting (app does this automatically)
        - Consider aggregating to reduce series count
        
        **API Usage:**
        - Free tier has request limits
        - One API call processes all series simultaneously
        - App automatically falls back to MA-6 if quota exceeded
        """)
    
    st.markdown("---")
    
    # Footer Info
    st.info("👉 Ready to start? Head to the **📤 Data Upload & Explorer** page to upload your data!")

def generate_sample_data():
    """Generate sample fleet data"""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Parameters
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    companies = ['PT ABC Logistics', 'PT XYZ Transport']
    origins = ['Jakarta', 'Surabaya', 'Bandung']
    destinations = ['Bandung', 'Semarang', 'Yogyakarta', 'Solo', 'Malang']
    fleet_types = ['Truck', 'Van', 'Container']
    
    # Province and region mapping
    location_mapping = {
        'Bandung': {'province': 'West Java', 'region': 'West'},
        'Semarang': {'province': 'Central Java', 'region': 'Central'},
        'Yogyakarta': {'province': 'DI Yogyakarta', 'region': 'Central'},
        'Solo': {'province': 'Central Java', 'region': 'Central'},
        'Malang': {'province': 'East Java', 'region': 'East'}
    }
    
    # Generate data
    data = []
    
    for company in companies:
        for origin in origins:
            for destination in destinations:
                if origin != destination:  # Avoid same origin-destination
                    for fleet_type in fleet_types:
                        # Generate time series with trend and seasonality
                        base_qty = np.random.randint(3, 10)
                        trend = np.linspace(0, 2, len(date_range))
                        seasonality = 2 * np.sin(2 * np.pi * np.arange(len(date_range)) / 365)
                        noise = np.random.normal(0, 1, len(date_range))
                        
                        qty_series = base_qty + trend + seasonality + noise
                        qty_series = np.maximum(qty_series, 0).astype(int)
                        
                        for date, qty in zip(date_range, qty_series):
                            data.append({
                                'date': date.strftime('%d/%m/%Y'),
                                'company': company,
                                'origin': origin,
                                'destination': destination,
                                'province': location_mapping[destination]['province'],
                                'region': location_mapping[destination]['region'],
                                'fleet_type': fleet_type,
                                'qty': qty
                            })
    
    df = pd.DataFrame(data)
    
    # Sample to reduce size (keep 30%)
    df = df.sample(frac=0.3, random_state=42).sort_values('date').reset_index(drop=True)
    
    return df
