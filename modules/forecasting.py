import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# Import model kandidat baru
from nixtlats import TimeGPT
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, CrostonSBA, AutoTheta, SeasonalNaive
from mlforecast import MLForecast
from mlforecast.target_transforms import Differences
import lightgbm as lgb

# Import profiler dari quality_checker
from .quality_checker import calculate_route_characteristics

# --- KONFIGURASI FORECAST ---
CV_STEPS = 3 # Jumlah langkah validasi silang

def get_base_models(granularity):
    """Menyiapkan instance dari semua model kandidat."""
    freq = 'MS' if granularity == "Bulanan" else 'W-MON'
    season_length = 12 if granularity == "Bulanan" else 52
    
    stat_models = {
        'AutoARIMA': AutoARIMA(),
        'AutoETS': AutoETS(),
        'AutoTheta': AutoTheta(),
        'SeasonalNaive': SeasonalNaive(season_length=season_length)
    }
    
    ml_model = lgb.LGBMRegressor(random_state=42, verbosity=-1)
    mlf = MLForecast(
        models={'LGBM': ml_model},
        freq=freq,
        lags=[1, 2, 3],
        target_transforms=[Differences([1])]
    )
    
    return stat_models, mlf, freq, season_length

def select_champion_model(df_cv: pd.DataFrame) -> pd.DataFrame:
    """Memilih model terbaik untuk setiap rute berdasarkan hasil cross-validation."""
    df_cv['mape'] = np.abs(df_cv['y'] - df_cv.get('y_hat', 0)) / np.abs(df_cv['y'])
    champion_map = df_cv.groupby(['unique_id', 'model'])['mape'].mean().reset_index()
    champions = champion_map.loc[champion_map.groupby('unique_id')['mape'].idxmin()]
    return champions[['unique_id', 'model']].rename(columns={'model': 'champion_model'})

def run_forecasting_pipeline(df_history: pd.DataFrame, df_events: pd.DataFrame, granularity: str, api_key: str, horizon: int) -> (pd.DataFrame, Dict[str, Any], pd.DataFrame):
    """Orkestrasi utama pipeline forecasting, sekarang mengembalikan hasil CV."""
    stat_models, mlf, freq, season_length = get_base_models(granularity)
    is_key_valid = api_key and api_key.startswith("nixtla_")

    df_profiles = calculate_route_characteristics(df_history.copy())
    
    all_forecasts = []
    all_cv_results = [] # List untuk menyimpan semua hasil CV
    metadata = {'total_routes': len(df_profiles), 'model_counts': {}}

    for _, profile in df_profiles.iterrows():
        uid = profile['unique_id']
        df_series = df_history[df_history['unique_id'] == uid][['unique_id', 'ds', 'y']]
        history_col = 'history_months' if granularity == "Bulanan" else 'history_weeks'
        
        model_candidates_names = []
        champion_model_name = None

        if profile['is_intermittent']:
            champion_model_name = 'CrostonSBA'
        elif profile[history_col] < 6:
            champion_model_name = 'AutoETS (Fallback)'
        else:
            if profile['seasonality_strength'] > 0.6:
                model_candidates_names.extend(['AutoETS', 'AutoTheta', 'LGBM'])
            elif profile['trend_strength'] > 0.7:
                model_candidates_names.extend(['AutoARIMA', 'AutoETS', 'AutoTheta'])
            else:
                model_candidates_names.extend(['AutoARIMA', 'AutoETS', 'AutoTheta', 'LGBM'])
            model_candidates_names.append('SeasonalNaive')
            if is_key_valid:
                model_candidates_names.append('TimeGPT')

        try:
            if champion_model_name:
                model_to_run = CrostonSBA() if 'Croston' in champion_model_name else AutoETS()
                sf = StatsForecast(models=[model_to_run], freq=freq, n_jobs=-1)
                sf.fit(df_series)
                forecast = sf.predict(h=horizon)
                forecast.rename(columns={forecast.columns[-1]: 'y_hat'}, inplace=True)
                forecast['champion_model'] = champion_model_name
                all_forecasts.append(forecast)
            else:
                candidate_stat_models = {k: v for k, v in stat_models.items() if k in model_candidates_names}
                
                sf = StatsForecast(models=list(candidate_stat_models.values()), freq=freq, n_jobs=-1)
                cv_sf = sf.cross_validation(df=df_series, h=1, n_windows=CV_STEPS)
                cv_results_this_run = [cv_sf.melt(id_vars=['unique_id', 'ds', 'cutoff', 'y'], var_name='model', value_name='y_hat')]
                
                if 'LGBM' in model_candidates_names:
                    cv_ml = mlf.cross_validation(df=df_series, h=1, n_windows=CV_STEPS)
                    cv_results_this_run.append(cv_ml.melt(id_vars=['unique_id', 'ds', 'cutoff', 'y'], var_name='model', value_name='y_hat'))
                
                if 'TimeGPT' in model_candidates_names:
                    timegpt = TimeGPT(token=api_key)
                    cv_tgpt = timegpt.cross_validation(df=df_series, h=1, n_windows=CV_STEPS, freq=freq)
                    cv_results_this_run.append(cv_tgpt.melt(id_vars=['unique_id', 'ds', 'cutoff', 'y'], var_name='model', value_name='y_hat'))

                df_cv_all_series = pd.concat(cv_results_this_run)
                all_cv_results.append(df_cv_all_series) # Simpan hasil CV
                
                champion = select_champion_model(df_cv_all_series)
                champion_model_name = champion['champion_model'].iloc[0]

                if champion_model_name in stat_models:
                    sf.fit(df_series)
                    forecast = sf.predict(h=horizon)[['ds', champion_model_name]]
                    forecast.rename(columns={champion_model_name: 'y_hat'}, inplace=True)
                elif champion_model_name == 'LGBM':
                    mlf.fit(df_series)
                    forecast = mlf.predict(h=horizon).rename(columns={'LGBM': 'y_hat'})
                else:
                    forecast = timegpt.forecast(df=df_series, h=horizon, freq=freq).rename(columns={'TimeGPT': 'y_hat'})
                
                forecast['unique_id'] = uid
                forecast['champion_model'] = champion_model_name
                all_forecasts.append(forecast)
        
        except Exception as e:
            st.warning(f"Error pada rute {uid}: {e}. Menggunakan AutoETS sebagai fallback.")
            champion_model_name = 'AutoETS (Error Fallback)'
            sf_fallback = StatsForecast(models=[AutoETS()], freq=freq, n_jobs=-1)
            sf_fallback.fit(df_series)
            forecast = sf_fallback.predict(h=horizon)
            forecast.rename(columns={'AutoETS': 'y_hat'}, inplace=True)
            forecast['champion_model'] = champion_model_name
            all_forecasts.append(forecast)

        metadata['model_counts'][champion_model_name] = metadata['model_counts'].get(champion_model_name, 0) + 1

    if not all_forecasts:
        return pd.DataFrame(), {}, pd.DataFrame()
        
    final_forecast_df = pd.concat(all_forecasts).reset_index(drop=True)
    df_cv_final = pd.concat(all_cv_results).reset_index(drop=True) if all_cv_results else pd.DataFrame()

    dim_cols = df_history[['unique_id', 'origin', 'location', 'fleet_type']].drop_duplicates()
    final_with_dims = pd.merge(final_forecast_df, dim_cols, on='unique_id')
    
    full_df = pd.concat([df_history, final_with_dims])
    full_df = full_df.drop_duplicates(subset=['unique_id', 'ds'], keep='last')

    # --- PERUBAHAN RETURN ---
    return full_df, metadata, df_cv_final