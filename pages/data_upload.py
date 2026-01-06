import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.visualization import Visualizer

def render():
    """Render the Data Upload & Explorer page"""
    
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>📤 Data Upload & Explorer</h1>
        <p>Upload your fleet data and explore insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File Upload Section
    st.markdown("### 📁 Upload Your Data")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a file with columns: date, company, origin, destination, province, region, fleet_type, qty"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box' style='margin: 0;'>
            <strong>💡 Format</strong><br>
            Date: dd/mm/yyyy
        </div>
        """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Process uploaded file
        try:
            # Read file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! ({len(df)} rows)")
            
            # Initialize data processor
            processor = DataProcessor()
            
            # Parse and validate data
            with st.spinner("Validating data..."):
                parsed_df, message = processor.parse_uploaded_data(df)
            
            if parsed_df is None:
                st.error(f"❌ Data validation failed: {message}")
                return
            
            st.success("✅ Data validation passed!")
            
            # Store in session state
            st.session_state.data = parsed_df
            
            # Detect frequency
            freq_code, freq_name = processor.detect_frequency(parsed_df)
            
            st.markdown("---")
            
            # Data Quality Report
            st.markdown("### 📊 Data Quality Report")
            
            report = processor.validate_data_quality(parsed_df, freq=freq_code)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>Total Rows</h3>
                    <div class='value'>{report['total_rows']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>Date Range</h3>
                    <div class='value' style='font-size: 1rem;'>{report['date_range']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>Frequency</h3>
                    <div class='value'>{freq_name}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                status_icon = "✅" if report['has_minimum_data'] else "⚠️"
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>Data Points</h3>
                    <div class='value'>{report['actual_points']} {status_icon}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Additional metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Companies", report['unique_companies'])
            
            with col2:
                st.metric("Routes", report['unique_routes'])
            
            with col3:
                st.metric("Fleet Types", report['unique_fleet_types'])
            
            with col4:
                st.metric("Missing Dates", report['missing_dates'])
            
            # Warnings
            if not report['has_minimum_data']:
                st.warning(f"⚠️ Insufficient data: You have {report['actual_points']} data points, but {report['min_points_required']} are recommended for {freq_name.lower()} data.")
            
            if report['missing_dates'] > 0:
                st.info(f"ℹ️ Found {report['missing_dates']} missing dates. These will be auto-filled with zeros during preprocessing.")
            
            if report['zero_qty_percent'] > 20:
                st.warning(f"⚠️ {report['zero_qty_percent']}% of records have zero quantity. This may affect forecast accuracy.")
            
            st.markdown("---")
            
            # Data Preview
            st.markdown("### 👀 Data Preview")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(
                    parsed_df.head(100),
                    use_container_width=True,
                    height=400
                )
            
            with col2:
                st.markdown("**Column Info**")
                st.markdown(f"- **date**: {parsed_df['date'].dtype}")
                st.markdown(f"- **company**: {parsed_df['company'].nunique()} unique")
                st.markdown(f"- **origin**: {parsed_df['origin'].nunique()} unique")
                st.markdown(f"- **destination**: {parsed_df['destination'].nunique()} unique")
                st.markdown(f"- **fleet_type**: {parsed_df['fleet_type'].nunique()} unique")
                st.markdown(f"- **qty**: {parsed_df['qty'].dtype}")
            
            st.markdown("---")
            
            # Interactive Filters
            st.markdown("### 🔍 Data Explorer")
            
            with st.expander("📊 Apply Filters", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    selected_companies = st.multiselect(
                        "Company",
                        options=sorted(parsed_df['company'].unique()),
                        help="Filter by company"
                    )
                
                with col2:
                    selected_origins = st.multiselect(
                        "Origin",
                        options=sorted(parsed_df['origin'].unique()),
                        help="Filter by origin warehouse"
                    )
                
                with col3:
                    selected_fleet_types = st.multiselect(
                        "Fleet Type",
                        options=sorted(parsed_df['fleet_type'].unique()),
                        help="Filter by fleet type"
                    )
                
                # Date range filter
                min_date = parsed_df['date'].min()
                max_date = parsed_df['date'].max()
                
                selected_date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    help="Select date range to analyze"
                )
            
            # Apply filters
            filtered_df = parsed_df.copy()
            
            if selected_companies:
                filtered_df = filtered_df[filtered_df['company'].isin(selected_companies)]
            
            if selected_origins:
                filtered_df = filtered_df[filtered_df['origin'].isin(selected_origins)]
            
            if selected_fleet_types:
                filtered_df = filtered_df[filtered_df['fleet_type'].isin(selected_fleet_types)]
            
            if len(selected_date_range) == 2:
                start_date, end_date = selected_date_range
                filtered_df = filtered_df[
                    (filtered_df['date'] >= pd.Timestamp(start_date)) &
                    (filtered_df['date'] <= pd.Timestamp(end_date))
                ]
            
            st.info(f"📊 Showing {len(filtered_df):,} rows after filtering")
            
            # Visualizations
            if len(filtered_df) > 0:
                st.markdown("### 📈 Visualizations")
                
                # Initialize visualizer
                visualizer = Visualizer()
                
                # Time series plot
                st.markdown("#### Total Fleet Usage Over Time")
                daily_agg = filtered_df.groupby('date')['qty'].sum().reset_index()
                fig = visualizer.plot_time_series(
                    daily_agg,
                    date_col='date',
                    value_col='qty',
                    title='Total Fleet Usage',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Additional charts in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Fleet Usage by Type")
                    fleet_summary = filtered_df.groupby('fleet_type')['qty'].sum().reset_index()
                    fleet_summary = fleet_summary.sort_values('qty', ascending=True)
                    
                    import plotly.graph_objects as go
                    fig = go.Figure(go.Bar(
                        x=fleet_summary['qty'],
                        y=fleet_summary['fleet_type'],
                        orientation='h',
                        marker=dict(color='#66BB6A')
                    ))
                    fig.update_layout(
                        xaxis_title='Total Quantity',
                        yaxis_title='Fleet Type',
                        height=300,
                        plot_bgcolor='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### Fleet Usage by Region")
                    region_summary = filtered_df.groupby('region')['qty'].sum().reset_index()
                    region_summary = region_summary.sort_values('qty', ascending=True)
                    
                    fig = go.Figure(go.Bar(
                        x=region_summary['qty'],
                        y=region_summary['region'],
                        orientation='h',
                        marker=dict(color='#2E7D32')
                    ))
                    fig.update_layout(
                        xaxis_title='Total Quantity',
                        yaxis_title='Region',
                        height=300,
                        plot_bgcolor='white',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Top routes
                st.markdown("#### Top 10 Routes by Volume")
                filtered_df['route'] = filtered_df['origin'] + ' → ' + filtered_df['destination']
                route_summary = filtered_df.groupby('route')['qty'].sum().reset_index()
                route_summary = route_summary.sort_values('qty', ascending=True).tail(10)
                
                fig = go.Figure(go.Bar(
                    x=route_summary['qty'],
                    y=route_summary['route'],
                    orientation='h',
                    marker=dict(color='#1B5E20')
                ))
                fig.update_layout(
                    xaxis_title='Total Quantity',
                    yaxis_title='Route',
                    height=400,
                    plot_bgcolor='white',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Data Preprocessing Options
            st.markdown("### ⚙️ Data Preprocessing")
            
            with st.expander("🔧 Preprocessing Options", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    handle_outliers = st.checkbox(
                        "Handle Outliers",
                        value=False,
                        help="Cap extreme values at 99th percentile"
                    )
                    
                    if handle_outliers:
                        outlier_threshold = st.slider(
                            "Outlier Threshold (percentile)",
                            min_value=90,
                            max_value=99,
                            value=99,
                            help="Values above this percentile will be capped"
                        )
                
                with col2:
                    auto_fill_dates = st.checkbox(
                        "Auto-fill Missing Dates",
                        value=True,
                        help="Automatically fill missing dates with zero qty"
                    )
                
                if st.button("Apply Preprocessing", type="primary"):
                    processed_df = parsed_df.copy()
                    
                    with st.spinner("Processing..."):
                        if handle_outliers:
                            processed_df = processor.handle_outliers(
                                processed_df,
                                method='cap',
                                threshold=outlier_threshold
                            )
                            st.success(f"✅ Outliers capped at {outlier_threshold}th percentile")
                        
                        if auto_fill_dates:
                            # This will be done automatically in forecasting
                            st.success("✅ Missing dates will be filled during forecasting")
                        
                        st.session_state.processed_data = processed_df
                        st.session_state.freq = freq_code
                        st.success("✅ Data preprocessing completed!")
            
            # Next steps
            st.markdown("---")
            st.success("✅ Data is ready! Head to **🔮 Forecasting Engine** to configure and run your forecast.")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please ensure your file is in CSV or Excel format with the correct columns.")
    
    else:
        # Show instructions when no file is uploaded
        st.info("👆 Please upload a CSV or Excel file to begin")
        
        st.markdown("""
        <div class='info-box'>
            <strong>📝 Required Columns:</strong><br>
            <code>date, company, origin, destination, province, region, fleet_type, qty</code><br><br>
            <strong>💡 Tip:</strong> Download the sample dataset from the Home page to see the expected format
        </div>
        """, unsafe_allow_html=True)
