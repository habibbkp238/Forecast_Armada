import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def generate_insight_text(profile, champion_model):
    """Membuat teks wawasan dinamis berdasarkan profil rute."""
    insight = f"Model juara untuk rute ini adalah **{champion_model}**."
    
    if "LGBM" in champion_model and profile['seasonality_strength'].iloc[0] > 0.6:
        insight += f" Ini kemungkinan karena rute ini memiliki **pola musiman yang kuat** (skor: {profile['seasonality_strength'].iloc[0]:.2f}) yang berhasil ditangkap oleh model Machine Learning."
    elif ("ETS" in champion_model or "Theta" in champion_model) and profile['trend_strength'].iloc[0] > 0.7:
        insight += f" Model ini kemungkinan terpilih karena kemampuannya menangani **tren yang kuat** (skor: {profile['trend_strength'].iloc[0]:.2f}) pada data."
    elif "ARIMA" in champion_model:
        insight += " Model ini cocok untuk data yang memiliki hubungan kuat dengan nilai-nilai masa lalunya (autokorelasi)."
    elif "Fallback" in champion_model or "Croston" in champion_model:
        insight += " Model ini dipilih karena karakteristik data yang spesifik (misalnya, histori sangat pendek atau permintaan sporadis)."
        
    return insight

def display_forecast_plots(forecast_results: dict, show_backtesting: bool):
    """
    Menampilkan plot interaktif dan wawasan dinamis, dengan filter company.
    """
    df_full = forecast_results['data']
    df_cv = forecast_results.get('cv_data')
    df_profiles = forecast_results.get('profiles_data')
    
    forecast_level = st.session_state.get('forecast_level', 'Lokasi')

    st.markdown("---")
    st.subheader("Pilih Rute untuk Dilihat Detailnya")
    
    # --- Filter Dinamis (DITAMBAH COMPANY) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Filter Company
        unique_companies = sorted(df_full['company'].unique())
        selected_company = st.selectbox("Pilih Company", options=unique_companies)
    
    # Filter selanjutnya akan bergantung pada company yang dipilih
    df_filtered = df_full[df_full['company'] == selected_company]

    with col2:
        unique_origins = sorted(df_filtered['origin'].unique())
        selected_origin = st.selectbox("Pilih Origin", options=unique_origins)
    with col3:
        unique_locations = sorted(df_filtered[df_filtered['origin'] == selected_origin]['location'].unique())
        selected_location = st.selectbox(f"Pilih Destinasi ({forecast_level})", options=unique_locations)
    with col4:
        if selected_location:
            unique_fleets = sorted(df_filtered[
                (df_filtered['origin'] == selected_origin) & 
                (df_filtered['location'] == selected_location)
            ]['fleet_type'].unique())
            selected_fleet = st.selectbox("Pilih Tipe Armada", options=unique_fleets)
        else:
            selected_fleet = None
        
    # --- Filter Data dan Buat Plot ---
    if all([selected_company, selected_origin, selected_location, selected_fleet]):
        selected_unique_id = f"{selected_company}_{selected_origin}_{selected_location}_{selected_fleet}"
        
        df_plot = df_full[df_full['unique_id'] == selected_unique_id].copy().sort_values('ds')
        
        champion_model = df_plot[df_plot['champion_model'].notna()]['champion_model'].iloc[0]
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_plot['ds'], y=df_plot['y'],
            mode='lines+markers', name='Data Historis (Aktual)',
            line=dict(color='#1f77b4', width=2.5)
        ))

        df_forecast_points = df_plot[df_plot['y'].isna()]
        fig.add_trace(go.Scatter(
            x=df_forecast_points['ds'], y=df_forecast_points['y_hat'],
            mode='lines+markers', name=f'Forecast ({champion_model})',
            line=dict(color='#ff7f0e', width=2.5, dash='dash')
        ))
        
        if show_backtesting and df_cv is not None and not df_cv.empty:
            df_cv_plot = df_cv[df_cv['unique_id'] == selected_unique_id]
            models_to_plot = df_cv_plot['model'].unique()
            colors = px.colors.qualitative.Plotly
            
            for i, model in enumerate(models_to_plot):
                model_cv_data = df_cv_plot[df_cv_plot['model'] == model]
                fig.add_trace(go.Scatter(
                    x=model_cv_data['ds'], y=model_cv_data['y_hat'],
                    mode='lines', name=f'Backtest: {model}',
                    line=dict(dash='dot', width=1.5, color=colors[i % len(colors)]),
                    legendgroup="backtest", legendgrouptitle_text="Hasil Backtesting"
                ))

        fig.update_layout(
            title=f"Forecast vs. Aktual: {selected_origin} ke {selected_location} ({selected_fleet})",
            xaxis_title="Tanggal", yaxis_title="Jumlah Kebutuhan Armada",
            legend_title="Legenda", hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        if df_profiles is not None and not df_profiles.empty:
            st.markdown("---")
            st.subheader("💡 Wawasan Otomatis")
            profile_selected = df_profiles[df_profiles['unique_id'] == selected_unique_id]
            if not profile_selected.empty:
                insight_text = generate_insight_text(profile_selected, champion_model)
                st.info(insight_text)

    else:
        st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih.")