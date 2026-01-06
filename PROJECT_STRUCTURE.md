# 📁 Project Structure

```
fleet_forecasting_app/
│
├── 📄 app.py                          # Main application entry point
│   ├── Streamlit configuration
│   ├── Page routing & navigation
│   ├── Session state management
│   ├── Custom CSS styling (green theme)
│   └── Footer with branding
│
├── 📂 pages/                          # Application pages
│   ├── __init__.py
│   │
│   ├── 📄 home.py                    # Home & Setup page
│   │   ├── Welcome section
│   │   ├── API key configuration
│   │   ├── API validation
│   │   ├── Sample data generation
│   │   └── Getting started guide
│   │
│   ├── 📄 data_upload.py             # Data Upload & Explorer page
│   │   ├── File upload (CSV/Excel)
│   │   ├── Data validation
│   │   ├── Quality report
│   │   ├── Interactive filters
│   │   ├── Visualizations
│   │   └── Preprocessing options
│   │
│   ├── 📄 forecasting.py             # Forecasting Engine page
│   │   ├── Aggregation level selector
│   │   ├── Forecast horizon input
│   │   ├── Holiday configuration
│   │   ├── Model selection
│   │   ├── Configuration summary
│   │   └── Forecast execution
│   │
│   └── 📄 results.py                 # Results & Download page
│       ├── Summary metrics
│       ├── Interactive charts
│       ├── Data table with search
│       ├── Export options (Excel/CSV)
│       └── Forecast insights
│
├── 📂 utils/                          # Utility modules
│   ├── __init__.py
│   │
│   ├── 📄 data_processor.py          # Data processing utilities
│   │   ├── parse_uploaded_data()     # Validate & parse data
│   │   ├── detect_frequency()        # Auto-detect daily/monthly
│   │   ├── validate_data_quality()   # Quality checks
│   │   ├── fill_missing_dates()      # Auto-fill gaps
│   │   ├── aggregate_data()          # Group by dimensions
│   │   ├── prepare_for_timegpt()     # Format for API
│   │   ├── add_holiday_features()    # Indonesian holidays
│   │   └── handle_outliers()         # Cap or remove outliers
│   │
│   ├── 📄 forecaster.py              # Forecasting engine
│   │   ├── __init__()                # Initialize TimeGPT client
│   │   ├── validate_api_key()        # Test API connection
│   │   ├── forecast_timegpt()        # TimeGPT forecasting
│   │   ├── forecast_moving_average() # MA-6 fallback
│   │   ├── prepare_exogenous()       # Holiday features
│   │   ├── run_forecast()            # Main forecast method
│   │   └── merge_with_metadata()     # Add metadata to results
│   │
│   ├── 📄 visualization.py           # Chart generation
│   │   ├── plot_time_series()        # Basic line chart
│   │   ├── plot_historical_vs_forecast() # Comparison chart
│   │   ├── plot_by_dimension()       # Bar charts by category
│   │   ├── plot_distribution()       # Box plot
│   │   ├── plot_top_routes()         # Horizontal bar chart
│   │   └── plot_heatmap()            # Heatmap visualization
│   │
│   └── 📄 export.py                  # Export management
│       ├── export_detailed_excel()   # Multi-sheet Excel
│       ├── export_summary_excel()    # Summary Excel
│       ├── export_detailed_csv()     # Detailed CSV
│       ├── export_summary_csv()      # Summary CSV
│       └── create_metadata_dict()    # Export metadata
│
├── 📂 .streamlit/                     # Streamlit configuration
│   └── 📄 config.toml                # Theme & server settings
│       ├── Green color theme
│       ├── Font settings
│       └── Browser configuration
│
├── 📂 data/                           # Data directory (optional)
│   └── (Sample datasets can be stored here)
│
├── 📄 requirements.txt                # Python dependencies
│   ├── streamlit>=1.28.0
│   ├── pandas>=2.0.0
│   ├── numpy>=1.24.0
│   ├── plotly>=5.14.0
│   ├── openpyxl>=3.1.0
│   ├── holidays>=0.35
│   ├── nixtla>=0.5.0
│   └── python-dateutil>=2.8.2
│
├── 📄 README.md                       # Comprehensive documentation
│   ├── Overview & features
│   ├── Installation guide
│   ├── User guide (all pages)
│   ├── Technical details
│   ├── Troubleshooting
│   └── API reference
│
├── 📄 QUICKSTART.md                   # Quick installation guide
│   ├── Prerequisites
│   ├── Installation methods
│   ├── First time setup
│   └── Troubleshooting
│
├── 📄 start.sh                        # Linux/Mac startup script
│   ├── Virtual environment setup
│   ├── Dependency installation
│   └── App launch
│
└── 📄 start.bat                       # Windows startup script
    ├── Virtual environment setup
    ├── Dependency installation
    └── App launch
```

---

## 🔄 Data Flow

```
User Upload (CSV/Excel)
        ↓
📄 data_upload.py
        ↓
utils/data_processor.py
    • Parse dates (dd/mm/yyyy)
    • Validate columns
    • Detect frequency
    • Quality report
        ↓
Session State Storage
        ↓
📄 forecasting.py
        ↓
utils/data_processor.py
    • Aggregate data
    • Fill missing dates
    • Add holiday features
    • Format for TimeGPT
        ↓
utils/forecaster.py
    • Call TimeGPT API
    • Or use MA-6 fallback
    • Process results
        ↓
Session State Storage
        ↓
📄 results.py
        ↓
utils/visualization.py + utils/export.py
    • Generate charts
    • Create exports
    • Display results
        ↓
User Downloads (Excel/CSV)
```

---

## 🎯 Key Components

### 1. Data Processing Pipeline
**File**: `utils/data_processor.py`
- Handles all data validation and transformation
- Auto-detects frequency (daily/monthly)
- Fills missing dates automatically
- Supports flexible aggregation
- Adds Indonesian holiday features

### 2. Forecasting Engine
**File**: `utils/forecaster.py`
- Integrates with TimeGPT API
- Implements MA-6 fallback
- Manages API quota gracefully
- Processes exogenous variables
- Batch forecasting (all series in one call)

### 3. Visualization System
**File**: `utils/visualization.py`
- Professional Plotly charts
- Consistent green theme
- Interactive features (zoom, pan, filter)
- Multiple chart types

### 4. Export Manager
**File**: `utils/export.py`
- Multi-sheet Excel generation
- Professional formatting
- Detailed and summary options
- Metadata inclusion

---

## 🔐 Session State Variables

```python
st.session_state.api_key              # Nixtla API key
st.session_state.data                 # Raw uploaded data
st.session_state.processed_data       # Preprocessed data
st.session_state.forecast_results     # Forecast results
st.session_state.forecast_metadata    # Forecast configuration
st.session_state.api_calls_count      # API usage counter
st.session_state.freq                 # Data frequency (D/MS)
```

---

## 🎨 Theming

### Color Palette
- **Primary Green**: #2E7D32
- **Secondary Green**: #66BB6A
- **Dark Green**: #1B5E20
- **Light Green**: #F1F8F4

### Custom Components
- Metric cards with green borders
- Info boxes with green highlights
- Buttons with hover effects
- Professional charts with green scales

---

## 📦 Dependencies

### Core
- **streamlit**: Web application framework
- **pandas**: Data manipulation
- **numpy**: Numerical operations

### Forecasting
- **nixtla**: TimeGPT API client

### Visualization
- **plotly**: Interactive charts

### Data Processing
- **holidays**: Holiday calendars
- **openpyxl**: Excel file generation
- **python-dateutil**: Date parsing

---

## 🚀 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy from repository

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

---

**Powered by TimeGPT | Developed by Irsandi Habibie**
