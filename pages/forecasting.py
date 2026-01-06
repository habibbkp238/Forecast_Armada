import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.forecaster import FleetForecaster

def render():
    """Render the Forecasting Engine page"""
    
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>🔮 Forecasting Engine</h1>
        <p>Configure and run your fleet forecast</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if data is uploaded
    if st.session_state.data is None:
        st.warning("⚠️ No data uploaded yet. Please go to **📤 Data Upload & Explorer** page first.")
        return
    
    # Check if API key is configured
    if not st.session_state.api_key:
        st.warning("⚠️ API key not configured. TimeGPT forecasting will not be available. You can still use Moving Average (MA-6).")
    
    # Initialize processor
    processor = DataProcessor()
    df = st.session_state.data.copy()
    
    # Get frequency from session or detect
    if 'freq' in st.session_state:
        freq_code = st.session_state.freq
    else:
        freq_code, _ = processor.detect_frequency(df)
    
    freq_name = 'Daily' if freq_code == 'D' else 'Monthly'
    
    st.markdown("---")
    
    # Configuration Section
    st.markdown("### ⚙️ Forecast Configuration")
    
    # Aggregation Level
    st.markdown("#### 1️⃣ Aggregation Level")
    st.markdown("Choose how to group your data for forecasting")
    
    aggregation_options = [
        'Most Granular',
        'By Company',
        'By Route',
        'By Fleet Type',
        'By Region',
        'By Province',
        'By Company & Route',
        'By Company & Fleet Type',
        'By Route & Fleet Type'
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        aggregation_level = st.selectbox(
            "Select Aggregation Level",
            options=aggregation_options,
            index=0,
            help="Most Granular: company + origin + destination + fleet_type. Choose higher-level aggregations for broader forecasts."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ℹ️ View Impact"):
            st.info(f"**{aggregation_level}** will create separate forecasts for each unique combination at this level.")
    
    # Preview aggregation impact
    agg_df, agg_cols = processor.aggregate_data(df, aggregation_level)
    series_summary = processor.get_series_summary(agg_df, agg_cols)
    
    st.markdown(f"""
    <div class='info-box'>
        <strong>📊 Series Summary:</strong><br>
        • Total series to forecast: <strong>{series_summary['total_series']}</strong><br>
        • Average data points per series: <strong>{series_summary['avg_data_points']:.0f}</strong><br>
        • Total quantity in dataset: <strong>{series_summary['total_qty']:,.0f}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if series_summary['total_series'] > 50:
        st.warning(f"⚠️ You're forecasting {series_summary['total_series']} series. This may take a few minutes and consume API quota if using TimeGPT.")
    
    st.markdown("---")
    
    # Forecast Horizon
    st.markdown("#### 2️⃣ Forecast Horizon")
    st.markdown("How many periods ahead to forecast")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        max_horizon = 365 if freq_code == 'D' else 36
        horizon = st.number_input(
            f"Number of {freq_name.lower()} periods",
            min_value=1,
            max_value=max_horizon,
            value=30 if freq_code == 'D' else 3,
            help=f"Forecast horizon: 1 to {max_horizon} periods"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Forecast Range", f"{horizon} {freq_name.lower()}")
    
    st.markdown("---")
    
    # Holiday Configuration
    st.markdown("#### 3️⃣ Holiday Features")
    st.markdown("Include Indonesian public holidays to improve accuracy")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        include_holidays = st.checkbox(
            "Include Indonesian Holidays",
            value=True,
            help="Recommended: Holidays can significantly impact fleet usage patterns"
        )
    
    with col2:
        if include_holidays:
            st.success("✅ Holidays enabled")
        else:
            st.info("ℹ️ Holidays disabled")
    
    if include_holidays:
        st.markdown("""
        <div class='info-box'>
            <strong>🎄 Holiday Integration:</strong><br>
            • Indonesian public holidays will be automatically detected<br>
            • Binary features will be created (is_holiday, is_weekend)<br>
            • Helps model understand seasonal patterns
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Model Selection
    st.markdown("#### 4️⃣ Model Selection")
    st.markdown("Choose the forecasting model")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.api_key:
            model_options = {
                'TimeGPT-1-long-horizon (Recommended)': 'timegpt-1-long-horizon',
                'TimeGPT-1': 'timegpt-1',
                'Moving Average (MA-6)': 'ma6'
            }
            
            selected_model_name = st.selectbox(
                "Select Model",
                options=list(model_options.keys()),
                index=0,
                help="TimeGPT-1-long-horizon recommended for datasets with 3+ years"
            )
            
            selected_model = model_options[selected_model_name]
            use_timegpt = selected_model != 'ma6'
        else:
            st.warning("API key not configured - only Moving Average available")
            selected_model = 'ma6'
            selected_model_name = 'Moving Average (MA-6)'
            use_timegpt = False
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if use_timegpt:
            st.success("🤖 AI Model")
        else:
            st.info("📊 Statistical Model")
    
    # Model info
    with st.expander("ℹ️ Model Information"):
        if use_timegpt:
            st.markdown("""
            **TimeGPT-1-long-horizon:**
            - Foundation model trained on 100B+ data points
            - Handles long-term patterns and seasonality
            - Best for 3+ years of historical data
            - Automatically incorporates exogenous features
            - Zero-shot forecasting (no training needed)
            
            **TimeGPT-1:**
            - Standard TimeGPT model
            - Faster inference
            - Good for shorter time series
            """)
        else:
            st.markdown("""
            **Moving Average (MA-6):**
            - Simple statistical method
            - Uses average of last 6 periods
            - Fast and reliable
            - No API required
            - Works as fallback when API quota exceeded
            """)
    
    st.markdown("---")
    
    # Summary
    st.markdown("### 📋 Configuration Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Aggregation</h3>
            <div class='value' style='font-size: 1rem;'>{aggregation_level}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Horizon</h3>
            <div class='value'>{horizon}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Model</h3>
            <div class='value' style='font-size: 0.9rem;'>{selected_model_name.split()[0]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Series</h3>
            <div class='value'>{series_summary['total_series']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Run Forecast Button
    st.markdown("### 🚀 Run Forecast")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        run_button = st.button(
            "▶️ Run Forecast",
            type="primary",
            use_container_width=True
        )
    
    if run_button:
        # Validate
        if series_summary['total_series'] == 0:
            st.error("❌ No data available for selected aggregation level")
            return
        
        # Prepare data
        with st.spinner("Preparing data..."):
            # Aggregate data
            agg_df, agg_cols = processor.aggregate_data(df, aggregation_level)
            
            # Fill missing dates
            filled_df = processor.fill_missing_dates(agg_df, freq=freq_code, aggregation_cols=agg_cols)
            
            # Add holiday features if enabled
            if include_holidays:
                filled_df = processor.add_holiday_features(filled_df, freq=freq_code)
            
            # Prepare for TimeGPT format
            timegpt_df = processor.prepare_for_timegpt(filled_df, agg_cols)
            print("Columns after prepare_for_timegpt:", timegpt_df.columns.tolist())
            print("Sample data:")
            print(timegpt_df.head())
            print("Unique IDs:", timegpt_df.index.nunique())
        
        # Run forecast
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress, message):
            progress_bar.progress(progress)
            status_text.text(message)
        
        # Initialize forecaster
        forecaster = FleetForecaster(api_key=st.session_state.api_key)
        
        # Run forecast
        forecast_result, model_used, message = forecaster.run_forecast(
            df=timegpt_df,
            horizon=horizon,
            freq=freq_code,
            model=selected_model,
            use_timegpt=use_timegpt,
            include_holidays=include_holidays,
            progress_callback=update_progress
        )
        
        if forecast_result is not None:
            # Merge with metadata
            final_forecast = forecaster.merge_forecast_with_metadata(
                forecast_result,
                filled_df,
                agg_cols
            )
            
            # Store in session state
            st.session_state.forecast_results = final_forecast
            st.session_state.forecast_metadata = {
                'model_used': model_used,
                'aggregation_level': aggregation_level,
                'aggregation_cols': agg_cols,
                'horizon': horizon,
                'freq': freq_name,
                'include_holidays': include_holidays,
                'n_series': series_summary['total_series']
            }
            
            progress_bar.progress(1.0)
            status_text.empty()
            
            st.success(f"✅ Forecast completed successfully using {model_used}!")
            st.balloons()
            
            # Show preview
            st.markdown("### 👀 Forecast Preview")
            st.dataframe(final_forecast.head(20), use_container_width=True)
            
            st.markdown("---")
            st.info("📊 Go to **Results & Download** page to view charts and export your forecast!")
        
        else:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Forecast failed: {message}")
            
            if "API" in message:
                st.info("💡 Try using Moving Average (MA-6) as a fallback, or check your API key configuration.")
