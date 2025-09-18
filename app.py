import streamlit as st
import pandas as pd
from datetime import datetime

# Impor modul-modul
from modules import data_loader, quality_checker, forecasting, visualization, exporter

# --- Konfigurasi Halaman & Inisialisasi State ---
st.set_page_config(
    page_title="Fleet Forecasting Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    # State untuk data
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df_history_full' not in st.session_state:
        st.session_state.df_history_full = None
    if 'df_history' not in st.session_state:
        st.session_state.df_history = None
    if 'df_events' not in st.session_state:
        st.session_state.df_events = None
    if 'cutoff_date' not in st.session_state:
        st.session_state.cutoff_date = None

    # State untuk pengaturan & navigasi
    if 'forecast_horizon' not in st.session_state:
        st.session_state.forecast_horizon = 3
    if 'forecast_granularity' not in st.session_state:
        st.session_state.forecast_granularity = "Bulanan"
    if 'forecast_results' not in st.session_state:
        st.session_state.forecast_results = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "1. Upload Data & Pengaturan"
    if 'forecast_level' not in st.session_state:
        st.session_state.forecast_level = "Kota"

initialize_session_state()


# --- Sidebar ---
with st.sidebar:
    st.title("🚀 Fleet Forecasting Engine")
    st.header("Konfigurasi API (Opsional)")
    timegpt_api_key = st.text_input("Masukkan TimeGPT API Key Anda", type="password")
    is_key_valid = timegpt_api_key and timegpt_api_key.startswith("nixak-")
    if timegpt_api_key and not is_key_valid:
        st.warning("Format API Key tidak valid.")
    elif is_key_valid:
        st.success("API Key siap digunakan!")
    st.markdown("---")
    st.info("Aplikasi ini membantu memproyeksikan kebutuhan armada.")

# --- Tampilan Utama ---
st.title("Dashboard Fleet Forecasting")

tab_names = [
    "1. Upload Data & Pengaturan", 
    "2. Data Quality Check", 
    "3. Event Check & Override",
    "4. Run Forecast & Results",
    "5. Export Forecast"
]

def set_active_tab(tab_name):
    st.session_state.active_tab = tab_name

try:
    active_tab_index = tab_names.index(st.session_state.active_tab)
except ValueError:
    active_tab_index = 0

selected_tab = st.radio(
    "Navigasi Langkah", tab_names, index=active_tab_index, 
    horizontal=True, label_visibility="collapsed"
)
if selected_tab != st.session_state.active_tab:
    set_active_tab(selected_tab)
    st.rerun()

# --- Tab 1: Upload Data & Pengaturan ---
if st.session_state.active_tab == tab_names[0]:
    st.header("Langkah 1: Upload Data & Pengaturan Forecast")
    
    st.subheader("Pengaturan Forecast")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.forecast_level = st.selectbox(
            "Level Agregasi Destinasi",
            ("Kota", "Provinsi", "Region"),
            key="forecast_level_selector"
        )
    with col2:
        st.session_state.forecast_granularity = st.radio(
            "Granularitas Output",
            ("Bulanan", "Mingguan"),
            key="granularity_selector",
            horizontal=True
        )
    with col3:
        unit = "Bulan" if st.session_state.forecast_granularity == "Bulanan" else "Minggu"
        st.session_state.forecast_horizon = st.number_input(
            f"Horizon Forecast ({unit})", 
            min_value=1, 
            max_value=24, 
            value=st.session_state.forecast_horizon,
            key="horizon_selector"
        )

    st.markdown("---")
    st.subheader("Upload File Data")
    data_loader.display_upload_section()
    
    if st.session_state.data_loaded:
        st.markdown("---")
        st.subheader("Pengaturan Data Historis (Cutoff)")
        data_loader.display_cutoff_selector()
        
        st.success("Data berhasil di-load dan difilter! Silakan lanjutkan ke tab berikutnya.")
        st.write("Preview Data (setelah agregasi & cutoff):")
        st.dataframe(st.session_state.df_history.head())

    st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    _, col_next = st.columns([6, 1])
    if col_next.button("Berikutnya →", use_container_width=True):
        set_active_tab(tab_names[1])
        st.rerun()

# --- Tab 2 & 3 ---
elif st.session_state.active_tab == tab_names[1]:
    st.header("Langkah 2: Pemeriksaan Kualitas Data")
    if not st.session_state.data_loaded or st.session_state.df_history is None:
        st.warning("Silakan upload dan proses data terlebih dahulu di Tab 1.")
    else:
        st.info(f"Metrik kualitas data ditampilkan untuk data hingga tanggal **{st.session_state.cutoff_date.strftime('%d %B %Y')}** pada level **{st.session_state.forecast_level}** ({st.session_state.forecast_granularity}).")
        quality_checker.display_dqc_metrics(st.session_state.df_history)

    st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col_prev, _, col_next = st.columns([1, 5, 1])
    if col_prev.button("← Sebelumnya", use_container_width=True):
        set_active_tab(tab_names[0])
        st.rerun()
    if col_next.button("Berikutnya →", use_container_width=True):
        set_active_tab(tab_names[2])
        st.rerun()
elif st.session_state.active_tab == tab_names[2]:
    st.header("Langkah 3: Konfigurasi Event & Uplift")
    if st.session_state.df_events is None or st.session_state.df_events.empty:
        st.info("Tidak ada file event yang di-upload.")
    else:
        st.write("Anda dapat mengubah persentase uplift event secara langsung pada tabel di bawah ini.")
        edited_events = st.data_editor(st.session_state.df_events)
        if not edited_events.equals(st.session_state.df_events):
            st.session_state.df_events = edited_events
            st.success("Perubahan uplift event berhasil disimpan!")
            
    st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col_prev, _, col_next = st.columns([1, 5, 1])
    if col_prev.button("← Sebelumnya", use_container_width=True):
        set_active_tab(tab_names[1])
        st.rerun()
    if col_next.button("Berikutnya →", use_container_width=True):
        set_active_tab(tab_names[3])
        st.rerun()


# --- Tab 4: Run Forecast & Results ---
elif st.session_state.active_tab == tab_names[3]:
    st.header("Langkah 4: Jalankan Forecast dan Visualisasikan Hasil")
    if not st.session_state.data_loaded or st.session_state.df_history is None:
        st.warning("Silakan upload dan proses data terlebih dahulu di Tab 1.")
    else:
        unit = "bulan" if st.session_state.forecast_granularity == "Bulanan" else "minggu"
        st.info(f"Forecast akan dijalankan untuk **{st.session_state.forecast_horizon} {unit}** ke depan, menggunakan data hingga **{st.session_state.cutoff_date.strftime('%d %B %Y')}**.")
        if not is_key_valid:
            st.warning("⚠️ API Key TimeGPT tidak ditemukan. Model TimeGPT akan dilewati.")
        
        run_forecast_button = st.button("🚀 Jalankan Proses Forecast", type="primary", disabled=(not st.session_state.data_loaded))

        if run_forecast_button:
            with st.spinner("Mesin forecast sedang bekerja..."):
                forecast_df, metadata, cv_df = forecasting.run_forecasting_pipeline(
                    df_history=st.session_state.df_history,
                    df_events=st.session_state.df_events,
                    granularity=st.session_state.forecast_granularity,
                    api_key=timegpt_api_key,
                    horizon=st.session_state.forecast_horizon
                )
                st.session_state.forecast_results = { 
                    "data": forecast_df, 
                    "metadata": metadata,
                    "cv_data": cv_df
                }
            st.success("Proses forecast selesai!")

        if st.session_state.forecast_results:
            # --- PERUBAHAN LOKASI TOGGLE ---
            st.subheader("Grafik Hasil Forecast")
            
            show_backtesting = st.toggle(
                "Tampilkan Hasil Backtesting di Grafik", 
                value=False,
                help="Aktifkan untuk menampilkan performa model-model kandidat pada data masa lalu. Ini membantu memvalidasi mengapa model juara terpilih."
            )
            
            visualization.display_forecast_plots(
                forecast_results=st.session_state.forecast_results,
                show_backtesting=show_backtesting
            )
        else:
            st.info("Klik tombol 'Jalankan Proses Forecast' untuk melihat hasilnya.")
    
    # Navigasi
    st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col_prev, _, col_next = st.columns([1, 5, 1])
    if col_prev.button("← Sebelumnya", use_container_width=True):
        set_active_tab(tab_names[2])
        st.rerun()
    if col_next.button("Berikutnya →", use_container_width=True):
        set_active_tab(tab_names[4])
        st.rerun()

# --- Tab 5 ---
elif st.session_state.active_tab == tab_names[4]:
    st.header("Langkah 5: Ekspor Hasil Forecast")
    if st.session_state.forecast_results is None:
        st.warning("Belum ada hasil forecast. Silakan jalankan forecast di Tab 4.")
    else:
        st.write("Klik tombol di bawah untuk mengunduh hasil forecast dalam format Excel.")
        excel_bytes = exporter.create_excel_export(st.session_state.forecast_results)
        st.download_button(
            label="📥 Download Hasil Forecast (.xlsx)",
            data=excel_bytes,
            file_name=f"fleet_forecast_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col_prev, _ = st.columns([1, 6])
    if col_prev.button("← Sebelumnya", use_container_width=True):
        set_active_tab(tab_names[3])
        st.rerun()