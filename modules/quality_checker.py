import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose

def _calculate_strength(series, component):
    """Helper untuk menghitung kekuatan komponen (tren/musiman)."""
    # Rumus: 1 - Var(Residual) / Var(Component + Residual)
    variance_residual = np.var(series.resid)
    variance_component = np.var(series.resid + component)
    return max(0, 1 - variance_residual / variance_component) if variance_component > 0 else 0

def calculate_route_characteristics(df):
    """
    Menghitung profil karakteristik lengkap (termasuk tren & musiman) 
    untuk setiap rute dari data yang sudah diagregat.
    """
    granularity = st.session_state.get('forecast_granularity', 'Bulanan')
    seasonal_period = 12 if granularity == "Bulanan" else 52
    
    all_profiles = []
    
    for uid in df['unique_id'].unique():
        series_df = df[df['unique_id'] == uid].set_index('ds')['y']
        
        # Hitung metrik dasar
        total_demand = series_df.sum()
        history_points = len(series_df)
        mean_demand = series_df.mean()
        std_demand = series_df.std()
        cv_squared = (std_demand / mean_demand) ** 2 if mean_demand > 0 else 0
        is_intermittent = cv_squared > 1.3
        
        # Hitung kekuatan tren & musiman (jika data cukup panjang)
        trend_strength = 0
        seasonality_strength = 0
        if history_points >= 2 * seasonal_period:
            try:
                decomposition = seasonal_decompose(series_df, model='additive', period=seasonal_period)
                trend_strength = _calculate_strength(decomposition, decomposition.trend)
                seasonality_strength = _calculate_strength(decomposition, decomposition.seasonal)
            except Exception:
                # Gagal dekomposisi, biarkan nilai default 0
                pass
        
        profile = {
            'unique_id': uid,
            'total_demand': total_demand,
            'history_points': history_points,
            'cv_squared': cv_squared,
            'is_intermittent': is_intermittent,
            'trend_strength': trend_strength,
            'seasonality_strength': seasonality_strength,
        }
        all_profiles.append(profile)
        
    df_profiles = pd.DataFrame(all_profiles).fillna(0)
    
    # Ganti nama kolom histori agar dinamis
    history_col_name = 'history_months' if granularity == 'Bulanan' else 'history_weeks'
    df_profiles.rename(columns={'history_points': history_col_name}, inplace=True)
    
    return df_profiles


def display_dqc_metrics(df):
    """
    Menampilkan metrik DQC yang sudah diperkaya dengan profil tren & musiman.
    """
    st.info("Metrik di bawah ini adalah 'profil' atau 'DNA' dari setiap rute setelah diagregasi.")
    
    with st.spinner("Menganalisis karakteristik data..."):
        route_chars = calculate_route_characteristics(df.copy())

    total_routes = route_chars['unique_id'].nunique()
    granularity = st.session_state.get('forecast_granularity', 'Bulanan')
    history_col = 'history_months' if granularity == "Bulanan" else 'history_weeks'
    
    # Tampilkan metrik utama
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Rute Unik", value=total_routes)
    with col2:
        avg_cv = route_chars['cv_squared'].mean()
        st.metric(label="Rata-rata Variabilitas (CV²)", value=f"{avg_cv:.2f}")
    with col3:
        avg_trend = route_chars['trend_strength'].mean()
        st.metric(label="Rata-rata Kekuatan Tren", value=f"{avg_trend:.2f}", help="Skala 0-1. Semakin mendekati 1, semakin jelas tren naik/turunnya.")
    with col4:
        avg_season = route_chars['seasonality_strength'].mean()
        st.metric(label="Rata-rata Kekuatan Musiman", value=f"{avg_season:.2f}", help="Skala 0-1. Semakin mendekati 1, semakin kuat pola berulangnya.")
    
    st.markdown("---")
    st.subheader("Segmentasi Karakteristik Rute")
    st.write("Sistem cerdas akan menggunakan profil ini untuk memilih model kandidat yang paling sesuai.")
    
    with st.expander("Lihat Detail Profil per Rute"):
        st.dataframe(
            route_chars[[
                'unique_id', history_col, 'total_demand', 'cv_squared', 'trend_strength', 'seasonality_strength'
            ]].sort_values('total_demand', ascending=False)
        )