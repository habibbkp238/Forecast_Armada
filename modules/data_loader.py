import streamlit as st
import pandas as pd

# Kolom yang wajib ada di file historis
REQUIRED_HISTORY_COLS = ['date', 'company', 'origin', 'destination', 'region', 'province', 'fleet_type']
# Kolom yang wajib ada di file event
REQUIRED_EVENT_COLS = ['date', 'event', 'uplift']

def process_uploaded_files(history_file, events_file, level, granularity):
    """
    Membaca, memvalidasi, dan memproses file.
    Sekarang menyertakan 'Company' sebagai level agregasi.
    """
    try:
        df_hist = pd.read_csv(history_file) if history_file.name.endswith('.csv') else pd.read_excel(history_file)
        df_hist.columns = [col.lower() for col in df_hist.columns]

        if not all(col in df_hist.columns for col in REQUIRED_HISTORY_COLS):
            missing_cols = [col for col in REQUIRED_HISTORY_COLS if col not in df_hist.columns]
            st.error(f"File historis tidak memiliki kolom wajib: {', '.join(missing_cols)}")
            st.session_state.data_loaded = False
            return

        df_hist['date'] = pd.to_datetime(df_hist['date'])

        # --- Logika Agregasi Dinamis (DITAMBAH COMPANY) ---
        if level == 'Company':
            grouping_cols = ['date', 'company', 'fleet_type']
            location_col = 'company' # 'location' sekarang bisa berarti company
        elif level == 'Region':
            grouping_cols = ['date', 'company', 'origin', 'region', 'fleet_type']
            location_col = 'region'
        elif level == 'Provinsi':
            grouping_cols = ['date', 'company', 'origin', 'province', 'fleet_type']
            location_col = 'province'
        else: # Kota
            grouping_cols = ['date', 'company', 'origin', 'destination', 'fleet_type']
            location_col = 'destination'

        if 'qty' in df_hist.columns:
            df_agg_spatial = df_hist.groupby(grouping_cols)['qty'].sum().reset_index()
            df_agg_spatial.rename(columns={'qty': 'y'}, inplace=True)
        else:
            df_hist['y'] = 1
            df_agg_spatial = df_hist.groupby(grouping_cols)['y'].sum().reset_index()

        df_agg_spatial.rename(columns={location_col: 'location'}, inplace=True)
        
        # Pembuatan unique_id disesuaikan untuk level Company
        if level == 'Company':
            df_agg_spatial['unique_id'] = df_agg_spatial['location'] + '_' + df_agg_spatial['fleet_type']
        else:
            df_agg_spatial['unique_id'] = df_agg_spatial['company'] + '_' + df_agg_spatial['origin'] + '_' + df_agg_spatial['location'] + '_' + df_agg_spatial['fleet_type']
        
        df_agg_spatial.rename(columns={'date': 'ds'}, inplace=True)
        
        # --- Resampling dan Zero Padding (Tidak Berubah) ---
        resample_freq = 'MS' if granularity == "Bulanan" else 'W-MON'
        df_time_indexed = df_agg_spatial.set_index('ds')
        
        df_resampled_list = []
        for uid in df_time_indexed['unique_id'].unique():
            df_series = df_time_indexed[df_time_indexed['unique_id'] == uid]
            df_resampled_series = df_series.resample(resample_freq)['y'].sum().reset_index()
            df_resampled_series['unique_id'] = uid
            df_resampled_list.append(df_resampled_series)

        df_final_resampled = pd.concat(df_resampled_list)

        global_min_date = df_final_resampled['ds'].min()
        global_max_date = df_final_resampled['ds'].max()
        full_date_range = pd.date_range(start=global_min_date, end=global_max_date, freq=resample_freq)
        all_uids = df_final_resampled['unique_id'].unique()
        master_grid = pd.MultiIndex.from_product([all_uids, full_date_range], names=['unique_id', 'ds']).to_frame(index=False)
        df_padded = pd.merge(master_grid, df_final_resampled, on=['unique_id', 'ds'], how='left')
        df_padded['y'] = df_padded['y'].fillna(0)
        
        # Menambahkan kembali kolom dimensi
        if level == 'Company':
            dim_cols = df_agg_spatial[['unique_id', 'location', 'fleet_type']].drop_duplicates()
            dim_cols.rename(columns={'location': 'company'}, inplace=True)
        else:
            dim_cols = df_agg_spatial[['unique_id', 'company', 'origin', 'location', 'fleet_type']].drop_duplicates()

        df_final = pd.merge(df_padded, dim_cols, on='unique_id')

        # --- Simpan Hasil Akhir ---
        st.session_state.df_history_full = df_final
        max_date = df_final['ds'].max()
        st.session_state.cutoff_date = max_date.date()
        st.session_state.df_history = df_final[df_final['ds'] <= max_date].copy()
        
        st.session_state.data_loaded = True
        
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file historis: {e}")
        st.session_state.data_loaded = False
        return
    
    # --- Proses File Event ---
    try:
        if events_file:
            df_events = pd.read_csv(events_file) if events_file.name.endswith('.csv') else pd.read_excel(events_file)
            if not all(col in df_events.columns for col in REQUIRED_EVENT_COLS):
                 missing_cols = [col for col in REQUIRED_EVENT_COLS if col not in df_events.columns]
                 st.error(f"File event tidak memiliki kolom wajib: {', '.join(missing_cols)}")
                 st.session_state.df_events = None
                 return
            df_events['date'] = pd.to_datetime(df_events['date'])
            st.session_state.df_events = df_events
        else:
            st.session_state.df_events = None
    except Exception as e:
        st.error(f"Gagal memproses file event: {e}")
        st.session_state.df_events = None

def display_upload_section():
    """Menampilkan bagian untuk upload file data."""
    with st.expander("Lihat Panduan Format Data"):
        st.markdown("""
        ### **Panduan Format Data Historis**
        **Kolom Wajib:** `date`, `company`, `origin`, `destination`, `province`, `region`, `fleet_type`
        **Kolom Opsional:** `qty`
        ---
        ### **Panduan Format Data Event**
        **Penting:** Mencakup event masa lalu dan masa depan.
        **Kolom Wajib:** `date`, `event`, `uplift`
        """)

    history_file = st.file_uploader("Unggah file data historis Anda (CSV atau Excel)", type=['csv', 'xlsx'])
    events_file = st.file_uploader("Unggah file event/hari libur Anda (Opsional)", type=['csv', 'xlsx'])
    
    forecast_level = st.session_state.get('forecast_level', 'Kota')
    granularity = st.session_state.get('forecast_granularity', 'Bulanan')

    if st.button("Proses Data", type="primary"):
        if history_file:
            with st.spinner(f"Memvalidasi dan mengagregasi data ke level {forecast_level} ({granularity})..."):
                process_uploaded_files(history_file, events_file, forecast_level, granularity)
        else:
            st.warning("Mohon unggah file data historis terlebih dahulu.")


def display_cutoff_selector():
    """Menampilkan date input untuk cutoff dan memfilter DataFrame utama."""
    if st.session_state.df_history_full is not None:
        df_full = st.session_state.df_history_full
        min_date = df_full['ds'].min().date()
        max_date = df_full['ds'].max().date()

        selected_cutoff = st.date_input(
            label="Gunakan data historis hingga tanggal:",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key="cutoff_date_widget",
            help="Pilih tanggal terakhir dari data historis yang akan digunakan untuk analisis dan forecast."
        )

        if selected_cutoff != st.session_state.cutoff_date:
            st.session_state.cutoff_date = selected_cutoff
            st.session_state.df_history = df_full[df_full['ds'] <= pd.to_datetime(selected_cutoff)].copy()
            st.rerun()