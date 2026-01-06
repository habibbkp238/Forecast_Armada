import streamlit as st
import pandas as pd
from utils.visualization import Visualizer
from utils.export import ExportManager
from datetime import datetime

def render():
    """Render the Results & Download page"""
    
    # Header
    st.markdown("""
    <div class='main-header'>
        <h1>📊 Results & Download</h1>
        <p>View forecast results and export data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if forecast results exist
    if st.session_state.forecast_results is None:
        st.warning("⚠️ No forecast results available. Please run a forecast first from the **🔮 Forecasting Engine** page.")
        return
    
    # Get data
    forecast_df = st.session_state.forecast_results
    metadata = st.session_state.forecast_metadata
    historical_df = st.session_state.data
    
    st.markdown("---")
    
    # Summary Cards
    st.markdown("### 📈 Forecast Summary")
    
    # Calculate metrics
    total_forecast = forecast_df['forecast_qty'].sum()
    avg_daily_forecast = forecast_df['forecast_qty'].mean()
    n_series = metadata['n_series']
    
    # Parse dates for range
    forecast_df_temp = forecast_df.copy()
    forecast_df_temp['date_parsed'] = pd.to_datetime(forecast_df_temp['date'], format='%d/%m/%Y')
    start_date = forecast_df_temp['date_parsed'].min().strftime('%d/%m/%Y')
    end_date = forecast_df_temp['date_parsed'].max().strftime('%d/%m/%Y')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Total Forecast</h3>
            <div class='value'>{total_forecast:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Forecast Period</h3>
            <div class='value' style='font-size: 1rem;'>{start_date}<br>to<br>{end_date}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Series Forecasted</h3>
            <div class='value'>{n_series}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Model Used</h3>
            <div class='value' style='font-size: 1rem;'>{metadata['model_used']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizations
    st.markdown("### 📊 Forecast Visualizations")
    
    # Initialize visualizer
    visualizer = Visualizer()
    
    # Main chart: Historical vs Forecast
    st.markdown("#### Historical Data vs Forecast")
    
    # Prepare historical data for comparison
    historical_df_viz = historical_df.copy()
    historical_df_viz['date'] = historical_df_viz['date'].dt.strftime('%d/%m/%Y')

    # Debug: check data
    print("Historical df shape:", historical_df_viz.shape)
    print("Historical df columns:", historical_df_viz.columns.tolist())
    print("Forecast df shape:", forecast_df.shape)
    print("Forecast df columns:", forecast_df.columns.tolist())

    # Call plot
    fig_main = visualizer.plot_historical_vs_forecast(
        historical_df_viz,
        forecast_df,
        aggregation='total',
        height=500
    )

    print("fig_main type:", type(fig_main))

    st.plotly_chart(fig_main, use_container_width=True)
    
    st.markdown("---")
    
    # Additional visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Forecast by Fleet Type")
        if 'fleet_type' in forecast_df.columns and forecast_df['fleet_type'].nunique() > 1:
            fig_fleet = visualizer.plot_by_dimension(
                forecast_df,
                dimension='fleet_type',
                top_n=10,
                height=400
            )
            st.plotly_chart(fig_fleet, use_container_width=True)
        else:
            st.info("Single fleet type - no comparison available")
    
    with col2:
        st.markdown("#### Forecast by Region")
        if 'region' in forecast_df.columns and forecast_df['region'].nunique() > 1:
            fig_region = visualizer.plot_by_dimension(
                forecast_df,
                dimension='region',
                top_n=10,
                height=400
            )
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("Single region - no comparison available")
    
    # Top Routes
    if 'origin' in forecast_df.columns and 'destination' in forecast_df.columns:
        if forecast_df['origin'].nunique() > 1 or forecast_df['destination'].nunique() > 1:
            st.markdown("#### Top 10 Routes by Forecast Volume")
            fig_routes = visualizer.plot_top_routes(forecast_df, top_n=10, height=450)
            st.plotly_chart(fig_routes, use_container_width=True)
    
    # Distribution
    st.markdown("#### Forecast Distribution")
    fig_dist = visualizer.plot_forecast_distribution(forecast_df, height=350)
    st.plotly_chart(fig_dist, use_container_width=True)
    
    st.markdown("---")
    
    # Data Table
    st.markdown("### 📋 Forecast Data Table")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Add search/filter
        search_term = st.text_input("🔍 Search in data", placeholder="Search by company, origin, destination...")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        show_all = st.checkbox("Show all rows", value=False)
    
    # Filter data if search term provided
    display_df = forecast_df.copy()
    if search_term:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
    
    # Display table
    if show_all:
        st.dataframe(display_df, use_container_width=True, height=600)
    else:
        st.dataframe(display_df.head(100), use_container_width=True, height=400)
        if len(display_df) > 100:
            st.info(f"Showing first 100 of {len(display_df)} rows. Check 'Show all rows' to see more.")
    
    st.markdown("---")
    
    # Export Section
    st.markdown("### 💾 Export Forecast")
    
    # Initialize export manager
    exporter = ExportManager()
    
    # Create metadata for export
    export_metadata = exporter.create_metadata_dict(
        forecast_df,
        model_used=metadata['model_used'],
        aggregation_level=metadata['aggregation_level'],
        horizon=metadata['horizon'],
        freq='D' if metadata['freq'] == 'Daily' else 'MS',
        include_holidays=metadata['include_holidays']
    )
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Detailed Export")
        st.markdown("Includes all dimensions and series")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Excel detailed
            excel_detailed = exporter.export_detailed_excel(
                forecast_df,
                historical_df_viz,
                export_metadata
            )
            
            st.download_button(
                label="📥 Download Detailed (Excel)",
                data=excel_detailed,
                file_name=f"fleet_forecast_detailed_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_b:
            # CSV detailed
            csv_detailed = exporter.export_detailed_csv(forecast_df)
            
            st.download_button(
                label="📥 Download Detailed (CSV)",
                data=csv_detailed,
                file_name=f"fleet_forecast_detailed_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with st.expander("ℹ️ What's included in Detailed Export?"):
            st.markdown("""
            **Excel Format (Multiple Sheets):**
            - Detailed Forecast: All dimensions and forecasts
            - Summary by Date: Daily/Monthly totals
            - Summary by Fleet Type: Aggregated by fleet type
            - Summary by Region: Aggregated by region
            - Summary by Route: Aggregated by route
            - Metadata: Forecast configuration details
            
            **CSV Format:**
            - Single file with all detailed forecasts
            - Columns: date, company, origin, destination, province, region, fleet_type, forecast_qty
            """)
    
    with col2:
        st.markdown("#### 📊 Summary Export")
        st.markdown("Aggregated totals by date")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Excel summary
            excel_summary = exporter.export_summary_excel(
                forecast_df,
                export_metadata
            )
            
            st.download_button(
                label="📥 Download Summary (Excel)",
                data=excel_summary,
                file_name=f"fleet_forecast_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_b:
            # CSV summary
            csv_summary = exporter.export_summary_csv(forecast_df)
            
            st.download_button(
                label="📥 Download Summary (CSV)",
                data=csv_summary,
                file_name=f"fleet_forecast_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with st.expander("ℹ️ What's included in Summary Export?"):
            st.markdown("""
            **Excel Format:**
            - Summary: Total forecast by date
            - By Fleet Type: Pivot table showing forecast by date and fleet type
            - Metadata: Forecast configuration details
            
            **CSV Format:**
            - Simple two-column format: date, total_forecast
            - Perfect for quick imports and analysis
            """)
    
    st.markdown("---")
    
    # Forecast Insights
    st.markdown("### 💡 Forecast Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Peak day
        daily_total = forecast_df.groupby('date')['forecast_qty'].sum()
        peak_day = daily_total.idxmax()
        peak_value = daily_total.max()
        
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Peak Day</h3>
            <div class='value' style='font-size: 1.2rem;'>{peak_day}</div>
            <p style='margin: 0.5rem 0 0 0; color: #666;'>{peak_value:.0f} fleets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Lowest day
        low_day = daily_total.idxmin()
        low_value = daily_total.min()
        
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Lowest Day</h3>
            <div class='value' style='font-size: 1.2rem;'>{low_day}</div>
            <p style='margin: 0.5rem 0 0 0; color: #666;'>{low_value:.0f} fleets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Most active fleet type
        if 'fleet_type' in forecast_df.columns:
            fleet_total = forecast_df.groupby('fleet_type')['forecast_qty'].sum()
            top_fleet = fleet_total.idxmax()
            top_fleet_value = fleet_total.max()
            
            st.markdown(f"""
            <div class='metric-card'>
                <h3>Top Fleet Type</h3>
                <div class='value' style='font-size: 1.2rem;'>{top_fleet}</div>
                <p style='margin: 0.5rem 0 0 0; color: #666;'>{top_fleet_value:.0f} total</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Run New Forecast", use_container_width=True):
            st.switch_page("pages/forecasting.py")
    
    with col2:
        if st.button("📤 Upload New Data", use_container_width=True):
            st.session_state.data = None
            st.session_state.forecast_results = None
            st.switch_page("pages/data_upload.py")
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("pages/home.py")
