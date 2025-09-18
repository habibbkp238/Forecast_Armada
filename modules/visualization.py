import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def display_forecast_plots(forecast_results: dict, show_backtesting: bool):
    """
    Menampilkan plot interaktif untuk hasil forecast.
    Sekarang bisa secara kondisional menampilkan hasil backtesting.
    """
    df_full = forecast_results['data']
    df_cv = forecast_results.get('cv_data') # Ambil data CV
    
    forecast_level = st.session_state.get('forecast_level', 'Lokasi')

    st.markdown("---")
    st.subheader("Pilih Rute untuk Dilihat Detailnya")
    
    # --- Filter Dinamis ---
    col1, col2, col3 = st.columns(3)
    with col1:
        unique_origins = sorted(df_full['origin'].unique())
        selected_origin = st.selectbox("Pilih Origin", options=unique_origins)
    with col2:
        unique_locations = sorted(df_full[df_full['origin'] == selected_origin]['location'].unique())
        selected_location = st.selectbox(f"Pilih Destinasi ({forecast_level})", options=unique_locations)
    with col3:
        if selected_location:
            unique_fleets = sorted(df_full[
                (df_full['origin'] == selected_origin) & 
                (df_full['location'] == selected_location)
            ]['fleet_type'].unique())
            selected_fleet = st.selectbox("Pilih Tipe Armada", options=unique_fleets)
        else:
            selected_fleet = None
        
    # --- Filter Data dan Buat Plot ---
    if selected_origin and selected_location and selected_fleet:
        selected_unique_id = f"{selected_origin}_{selected_location}_{selected_fleet}"
        
        df_plot = df_full[df_full['unique_id'] == selected_unique_id].copy().sort_values('ds')
        
        champion_model = df_plot[df_plot['champion_model'].notna()]['champion_model'].iloc[0]
        
        fig = go.Figure()

        # 1. Trace untuk data historis
        fig.add_trace(go.Scatter(
            x=df_plot['ds'], y=df_plot['y'],
            mode='lines+markers', name='Data Historis (Aktual)',
            line=dict(color='#1f77b4', width=2.5) # Biru
        ))

        # 2. Trace untuk data forecast
        df_forecast_points = df_plot[df_plot['y'].isna()]
        fig.add_trace(go.Scatter(
            x=df_forecast_points['ds'], y=df_forecast_points['y_hat'],
            mode='lines+markers', name=f'Forecast ({champion_model})',
            line=dict(color='#ff7f0e', width=2.5, dash='dash') # Oranye
        ))
        
        # --- BLOK BARU: Tambahkan trace untuk backtesting jika toggle ON ---
        if show_backtesting:
            if df_cv is not None and not df_cv.empty:
                df_cv_plot = df_cv[df_cv['unique_id'] == selected_unique_id]
                
                # Buat palet warna untuk model-model backtest
                models_to_plot = df_cv_plot['model'].unique()
                colors = px.colors.qualitative.Plotly
                
                for i, model in enumerate(models_to_plot):
                    model_cv_data = df_cv_plot[df_cv_plot['model'] == model]
                    fig.add_trace(go.Scatter(
                        x=model_cv_data['ds'],
                        y=model_cv_data['y_hat'],
                        mode='lines',
                        name=f'Backtest: {model}',
                        line=dict(dash='dot', width=1.5, color=colors[i % len(colors)]),
                        legendgroup="backtest",
                        legendgrouptitle_text="Hasil Backtesting"
                    ))

        # Update Layout Plot
        fig.update_layout(
            title=f"Forecast vs. Aktual: {selected_origin} ke {selected_location} ({selected_fleet})",
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Kebutuhan Armada",
            legend_title="Legenda",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")