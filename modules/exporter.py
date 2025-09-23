import streamlit as st
import pandas as pd
from datetime import datetime
import io

def create_excel_export(forecast_results: dict) -> bytes:
    """
    Membuat file Excel dari hasil forecast untuk diunduh.
    Kolom output sekarang menyertakan company.
    """
    output = io.BytesIO()

    # Ambil pengaturan dari session state untuk metadata
    forecast_level = st.session_state.get('forecast_level', 'Lokasi')
    forecast_granularity = st.session_state.get('forecast_granularity', 'Bulanan')
    forecast_horizon = st.session_state.get('forecast_horizon', 3)

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # --- Sheet 1: Metadata ---
        metadata = forecast_results['metadata']
        run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        meta_data_list = [
            ("Forecast Run Time", run_time),
            ("Forecast Level", forecast_level),
            ("Forecast Granularity", forecast_granularity),
            ("Forecast Horizon", f"{forecast_horizon} {forecast_granularity.replace('an', '')}"),
            ("Total Unique Series Forecasted", metadata.get('total_routes', 'N/A')),
        ]
        
        if 'model_counts' in metadata:
            for model, count in metadata['model_counts'].items():
                meta_data_list.append((f"Count of Model: {model}", count))
            
        df_meta = pd.DataFrame(meta_data_list, columns=["Metric", "Value"])
        df_meta.to_excel(writer, sheet_name="Metadata", index=False)

        # --- Sheet 2: Forecast Results ---
        df_full = forecast_results['data']
        df_export = df_full[df_full['y'].isna()].copy()
        
        # Sertakan 'company' dalam daftar kolom untuk diekspor
        cols_to_export = [
            'ds', 
            'company',
            'origin', 
            'location',
            'fleet_type', 
            'y_hat', 
            'champion_model'
        ]
        cols_to_export = [col for col in cols_to_export if col in df_export.columns]
        df_export = df_export[cols_to_export]
        
        df_export.rename(columns={
            'ds': 'Tanggal Forecast',
            'location': f'Destinasi ({forecast_level})',
            'y_hat': 'Nilai Forecast (Pembulatan)',
            'champion_model': 'Model yang Digunakan'
        }, inplace=True)
        
        if 'Nilai Forecast (Pembulatan)' in df_export.columns:
            df_export['Nilai Forecast (Pembulatan)'] = df_export['Nilai Forecast (Pembulatan)'].round().astype(int)
        
        df_export.to_excel(writer, sheet_name="Forecast Results", index=False)

    excel_data = output.getvalue()
    return excel_data