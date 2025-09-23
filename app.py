import streamlit as st
import pandas as pd
from datetime import datetime

# Impor modul-modul
from modules import data_loader, quality_checker, forecasting, visualization, exporter

# --- FUNGSI UNTUK MEMUAT CSS KUSTOM ---
def load_custom_css():
    st.markdown("""
        <style>
            /* Palet Warna */
            .main { background-color: #F9F5F0; }
            h1, h2, h3 { color: #344F1F; }
            div[role="radiogroup"] > label {
                padding: 5px 15px; border-radius: 20px; border: 1px solid #D1C7B8;
                background-color: #FFFFFF; color: #344F1F; margin-right: 10px; transition: all 0.3s;
            }
            div[role="radiogroup"] > label:has(input:checked) {
                background-color: #F4991A; color: #F9F5F0; border: 1px solid #344F1F;
            }
            .stButton>button {
                border-radius: 20px; border: 2px solid #F4991A; background-color: #F4991A;
                color: white; font-weight: bold; transition: all 0.3s;
            }
            .stButton>button:hover { background-color: #FFFFFF; color: #F4991A; }
            div[data-testid="stMetric"] {
                background-color: #F4991A; border: 1px solid #E0D8C8; border-radius: 10px;
                padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            div[data-testid="stSidebarUserContent"] { background-color: #F2EAD3; }
        </style>
    """, unsafe_allow_html=True)

# --- FUNGSI BARU UNTUK FOOTER ---
def display_footer():
    year = datetime.now().year
    st.markdown(f"""
        <style>
            .footer {{
                position: relative; left: 0; bottom: 0; width: 100%;
                background-color: #344F1F; color: #F2EAD3; text-align: center;
                padding: 10px; border-radius: 10px; margin-top: 2rem;
            }}
            .footer a {{ color: #F4991A; text-decoration: none; }}
            .footer a:hover {{ text-decoration: underline; }}
        </style>
        <div class="footer">
            <p>&copy; {year} - Fleet Forecasting Engine | by Irsandi Habibie | https://www.linkedin.com/in/habibie238/ <br>
            <a href="irsandi.nur@bkpprima.co.id" target="_blank">Hubungi Pengembang</a></p>
        </div>
    """, unsafe_allow_html=True)

# --- Konfigurasi Halaman & Inisialisasi State ---
st.set_page_config(
    page_title="Fleet Forecasting Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Panggil fungsi CSS setelah set_page_config
load_custom_css()

def initialize_session_state():
    # ... (Isi fungsi ini tidak berubah) ...
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

# --- Header Profesional ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("asset/logistics.png", width=100)
with col2:
    st.title("Fleet Forecasting Engine")
    st.markdown("##### Rencanakan Kebutuhan Armada")
st.markdown("---")

# --- Tampilan Utama ---
tab_names = [
    "1. Upload Data & Pengaturan", 
    "2. Data Quality Check", 
    "3. Event Check & Override",
    "4. Run Forecast & Results",
    "5. Ringkasan & Ekspor"
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
            "Pilih Level Agregasi",
            ("Company", "Region", "Provinsi", "Kota"),
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

# --- Sisa Tab (Tidak ada perubahan) ---
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
                forecast_df, metadata, cv_df, profiles_df = forecasting.run_forecasting_pipeline(
                    df_history=st.session_state.df_history,
                    df_events=st.session_state.df_events,
                    granularity=st.session_state.forecast_granularity,
                    api_key=timegpt_api_key,
                    horizon=st.session_state.forecast_horizon
                )
                st.session_state.forecast_results = { 
                    "data": forecast_df, 
                    "metadata": metadata,
                    "cv_data": cv_df,
                    "profiles_data": profiles_df
                }
            st.success("Proses forecast selesai!")

        if st.session_state.forecast_results:
            st.subheader("Grafik Hasil Forecast")
            
            show_backtesting = st.toggle(
                "Tampilkan Hasil Backtesting di Grafik", 
                value=False,
                help="Aktifkan untuk menampilkan performa model-model kandidat pada data masa lalu."
            )
            
            visualization.display_forecast_plots(
                forecast_results=st.session_state.forecast_results,
                show_backtesting=show_backtesting
            )
        else:
            st.info("Klik tombol 'Jalankan Proses Forecast' untuk melihat hasilnya.")
    
    st.markdown('<hr style="margin-top: 2rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    col_prev, _, col_next = st.columns([1, 5, 1])
    if col_prev.button("← Sebelumnya", use_container_width=True):
        set_active_tab(tab_names[2])
        st.rerun()
    if col_next.button("Berikutnya →", use_container_width=True):
        set_active_tab(tab_names[4])
        st.rerun()
elif st.session_state.active_tab == tab_names[4]:
    st.header("Langkah 5: Ringkasan & Ekspor")
    if st.session_state.forecast_results is None:
        st.warning("Belum ada hasil forecast. Silakan jalankan forecast di Tab 4.")
    else:
        st.subheader("Ringkasan Kunci Hasil Forecast")
        
        results_data = st.session_state.forecast_results['data']
        all_companies = sorted(results_data['company'].unique())
        selected_company = st.selectbox("Tampilkan Ringkasan untuk Company:", options=all_companies)
        
        filtered_results_data = results_data[results_data['company'] == selected_company]
        
        forecast_data = filtered_results_data[filtered_results_data['y'].isna()].copy()
        total_forecasted_demand = forecast_data['y_hat'].sum()
        
        champion_models = st.session_state.forecast_results['metadata'].get('model_counts', {})
        most_used_model = max(champion_models, key=champion_models.get) if champion_models else "N/A"
        unit = "Bulan" if st.session_state.forecast_granularity == "Bulanan" else "Minggu"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"Total Prediksi Armada ({st.session_state.forecast_horizon} {unit} ke depan)",
                value=f"{int(total_forecasted_demand):,}"
            )
        with col2:
            st.metric(
                label="Model Juara Paling Sering Digunakan",
                value=most_used_model
            )
        with col3:
            st.metric(
                label="Total Series yang Di-forecast",
                value=len(filtered_results_data['unique_id'].unique())
            )
        
        st.markdown("---")
        st.subheader("Ekspor Hasil Lengkap")
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

# --- PANGGIL FUNGSI FOOTER DI BAGIAN PALING AKHIR ---

display_footer()
