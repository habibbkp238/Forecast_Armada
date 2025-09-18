import pandas as pd
import io
from datetime import datetime
import streamlit as st

def create_excel_export(forecast_results: dict) -> bytes:
    """
    Membuat file Excel dari hasil forecast untuk diunduh.
    Kolom output sekarang dinamis berdasarkan level forecast.
    """
    output = io.BytesIO()

    # Ambil level forecast dari session state untuk membuat output dinamis
    forecast_level = st.session_state.get('forecast_level', 'Lokasi')
    forecast_granularity = st.session_state.get('forecast_granularity', 'Bulanan')

    # Menggunakan ExcelWriter untuk menulis ke beberapa sheet
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        # --- Sheet 1: Metadata ---
        metadata = forecast_results['metadata']
        run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Buat DataFrame dari metadata
        meta_data_list = [
            ("Forecast Run Time", run_time),
            ("Forecast Level", forecast_level),
            ("Forecast Granularity", forecast_granularity),
            ("Total Unique Series Forecasted", metadata.get('total_routes', 'N/A')),
        ]
        
        # Tambahkan hitungan model jika ada
        if 'model_counts' in metadata:
            for model, count in metadata['model_counts'].items():
                meta_data_list.append((f"Count of Model: {model}", count))
            
        df_meta = pd.DataFrame(meta_data_list, columns=["Metric", "Value"])
        
        df_meta.to_excel(writer, sheet_name="Metadata", index=False)

        # --- Sheet 2: Forecast Results ---
        df_full = forecast_results['data']
        
        # Ambil hanya baris forecast (di mana data historis 'y' adalah NaN)
        df_export = df_full[df_full['y'].isna()].copy()
        
        # Pilih dan urutkan kolom yang relevan untuk ekspor
        cols_to_export = [
            'ds', 
            'origin', 
            'location', # Gunakan kolom 'location' yang sudah distandarisasi
            'fleet_type', 
            'y_hat', 
            'champion_model'
        ]
        # Pastikan semua kolom ada sebelum memilih
        cols_to_export = [col for col in cols_to_export if col in df_export.columns]
        df_export = df_export[cols_to_export]
        
        # Ganti nama kolom agar lebih ramah pengguna dan dinamis
        df_export.rename(columns={
            'ds': 'Tanggal Forecast',
            'location': f'Destinasi ({forecast_level})',
            'y_hat': 'Nilai Forecast (Pembulatan)',
            'champion_model': 'Model yang Digunakan'
        }, inplace=True)
        
        # Bulatkan hasil forecast jika kolomnya ada
        if 'Nilai Forecast (Pembulatan)' in df_export.columns:
            df_export['Nilai Forecast (Pembulatan)'] = df_export['Nilai Forecast (Pembulatan)'].round().astype(int)
        
        df_export.to_excel(writer, sheet_name="Forecast Results", index=False)

    # Ambil data bytes dari buffer di memori
    excel_data = output.getvalue()
    return excel_data