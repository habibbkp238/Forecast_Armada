# 🚛 Fleet Forecasting Engine

AI-Powered Fleet Usage Prediction with TimeGPT

---

## 📋 Overview

The **Fleet Forecasting Engine** is a professional Streamlit application designed to forecast fleet usage across different types, routes, and regions using state-of-the-art AI models from Nixtla's TimeGPT.

### Key Features

- 🎯 **Accurate Forecasting**: Powered by TimeGPT-1-long-horizon for superior accuracy
- 📊 **Flexible Aggregation**: Forecast at granular or aggregated levels
- 🎄 **Holiday Integration**: Automatically includes Indonesian public holidays
- 📈 **Interactive Visualizations**: Professional charts with Plotly
- 📥 **Export Options**: Download as Excel or CSV (detailed or summary)
- 🔄 **Automatic Fallback**: MA-6 fallback when API quota exceeded
- 🎨 **Professional UI**: Clean green-themed interface

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the repository
cd fleet_forecasting_app

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### 3. Get API Key

1. Go to [https://dashboard.nixtla.io](https://dashboard.nixtla.io)
2. Sign up for a free account
3. Copy your API key
4. Enter it in the app's Home page

---

## 📊 Data Requirements

### Required Columns

Your dataset must include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `date` | Date in dd/mm/yyyy format | 31/12/2024 |
| `company` | Company name | PT ABC Logistics |
| `origin` | Warehouse origin | Jakarta |
| `destination` | City destination | Bandung |
| `province` | Province of destination | West Java |
| `region` | Region of destination | West |
| `fleet_type` | Type of fleet | Truck |
| `qty` | Number of fleets used | 5 |

### Data Format

- **Date Format**: dd/mm/yyyy (e.g., 31/12/2024)
- **File Format**: CSV or Excel (.xlsx, .xls)
- **Encoding**: UTF-8 recommended
- **Minimum Data**: 30 days for daily data, 12 months for monthly data

### Sample Data

Download sample data from the Home page to see the expected format.

---

## 📖 User Guide

### Page 1: 🏠 Home & Setup

**Purpose**: Configure API key and get started

**Steps**:
1. Enter your Nixtla API key
2. Click "Validate" to test connection
3. Download sample dataset (optional)
4. Read the getting started guide

**Tips**:
- Free tier API has request limits
- One API call processes all series simultaneously
- Automatic fallback to MA-6 if quota exceeded

---

### Page 2: 📤 Data Upload & Explorer

**Purpose**: Upload and validate your data

**Steps**:
1. Upload CSV or Excel file
2. Review data quality report
3. Check for missing dates or outliers
4. Explore visualizations
5. Apply preprocessing if needed

**Features**:
- Automatic data validation
- Frequency detection (daily/monthly)
- Interactive filters
- Time series visualizations
- Data quality metrics

**Tips**:
- Ensure dates are in dd/mm/yyyy format
- Missing dates will be auto-filled
- Review data quality report carefully

---

### Page 3: 🔮 Forecasting Engine

**Purpose**: Configure and run forecast

**Configuration Options**:

#### 1. Aggregation Level
Choose how to group your data:
- **Most Granular**: company + origin + destination + fleet_type
- **By Company**: Aggregate all routes and fleet types per company
- **By Route**: Aggregate by origin-destination pairs
- **By Fleet Type**: Aggregate by fleet type
- **By Region**: Aggregate by geographic region
- And more combinations...

#### 2. Forecast Horizon
- Daily data: 1 to 365 periods
- Monthly data: 1 to 36 periods
- Recommended: 30 days or 3 months

#### 3. Holiday Features
- **Enabled (Recommended)**: Includes Indonesian public holidays
- Adds binary features: is_holiday, is_weekend
- Helps model understand seasonal patterns

#### 4. Model Selection
- **TimeGPT-1-long-horizon** (Recommended): Best for 3+ years data
- **TimeGPT-1**: Standard model, faster inference
- **Moving Average (MA-6)**: Statistical fallback, no API required

**Steps**:
1. Select aggregation level
2. Set forecast horizon
3. Enable holiday features (recommended)
4. Choose model
5. Review configuration summary
6. Click "Run Forecast"

**Tips**:
- Higher aggregation = fewer series = faster
- TimeGPT-1-long-horizon recommended for your 3-year dataset
- Watch series count to manage API usage

---

### Page 4: 📊 Results & Download

**Purpose**: View and export forecast results

**Features**:
- Summary metrics (total forecast, peak days, etc.)
- Interactive visualizations
- Forecast data table with search
- Export options (Excel/CSV, detailed/summary)
- Forecast insights

**Visualizations**:
- Historical vs Forecast comparison
- Forecast by Fleet Type
- Forecast by Region
- Top 10 Routes
- Forecast Distribution

**Export Options**:

#### Detailed Export
**Excel**: Multiple sheets with:
- Detailed forecasts (all dimensions)
- Summary by date
- Summary by fleet type
- Summary by region
- Summary by route
- Metadata

**CSV**: Single file with all detailed forecasts

#### Summary Export
**Excel**: Two sheets:
- Summary by date
- Pivot by fleet type

**CSV**: Simple two-column format (date, total_forecast)

**Tips**:
- Use detailed export for deep analysis
- Use summary export for quick reporting
- Charts can be zoomed and filtered interactively

---

## 🎨 Customization

### Color Scheme

The app uses a professional green theme:
- Primary: #2E7D32
- Secondary: #66BB6A
- Accent: #1B5E20
- Light: #F1F8F4

### Modifying Colors

Edit the CSS in `app.py` to change colors:

```python
:root {
    --primary-green: #2E7D32;
    --secondary-green: #66BB6A;
    --dark-green: #1B5E20;
    --light-green: #F1F8F4;
}
```

---

## ⚙️ Technical Details

### Architecture

```
fleet_forecasting_app/
├── app.py                 # Main application file
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── pages/                # Page modules
│   ├── home.py           # Home & Setup
│   ├── data_upload.py    # Data Upload & Explorer
│   ├── forecasting.py    # Forecasting Engine
│   └── results.py        # Results & Download
├── utils/                # Utility modules
│   ├── data_processor.py # Data processing & validation
│   ├── forecaster.py     # Forecasting engine
│   ├── visualization.py  # Chart generation
│   └── export.py         # Export management
└── data/                 # Sample data (optional)
```

### Key Technologies

- **Streamlit**: Web application framework
- **TimeGPT**: Foundation model for forecasting
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **OpenPyXL**: Excel file generation
- **Holidays**: Holiday calendar for Indonesia

### Data Processing Pipeline

1. **Upload** → Validate columns and date format
2. **Parse** → Convert dates to datetime, validate data types
3. **Detect** → Auto-detect frequency (daily/monthly)
4. **Aggregate** → Group by selected dimensions
5. **Fill** → Auto-fill missing dates
6. **Features** → Add holiday features if enabled
7. **Format** → Convert to TimeGPT format (unique_id, ds, y)
8. **Forecast** → Call TimeGPT API or MA-6
9. **Merge** → Combine forecast with metadata
10. **Export** → Generate Excel/CSV files

### API Usage Optimization

- **Batch Forecasting**: All series processed in single API call
- **Smart Aggregation**: Reduces series count before forecasting
- **Automatic Fallback**: Switches to MA-6 if API quota exceeded
- **Request Tracking**: Counts API calls per session

---

## 🐛 Troubleshooting

### Issue: "Invalid API key"
**Solution**: 
- Check API key is correct
- Ensure no extra spaces
- Verify API key is active at dashboard.nixtla.io

### Issue: "Insufficient data"
**Solution**: 
- Ensure at least 30 days for daily data
- Ensure at least 12 months for monthly data
- Check for missing dates in critical series

### Issue: "API quota exceeded"
**Solution**: 
- App automatically falls back to MA-6
- Reduce number of series by aggregating
- Wait for quota reset (free tier limits)
- Consider upgrading API plan

### Issue: "Date parsing error"
**Solution**: 
- Ensure dates are in dd/mm/yyyy format
- Check for invalid dates (e.g., 32/01/2024)
- Remove any text in date column

### Issue: "Missing columns"
**Solution**: 
- Verify all required columns exist
- Check spelling matches exactly
- Case-sensitive: use lowercase column names

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review tooltips in the app (hover over ℹ️ icons)
3. Download sample data to see correct format
4. Check Nixtla documentation: [https://docs.nixtla.io](https://docs.nixtla.io)

---

## 📄 License

This application is developed by **Irsandi Habibie**.

---

## 🙏 Acknowledgments

- **TimeGPT** by Nixtla for the forecasting engine
- **Streamlit** for the web framework
- **Plotly** for interactive visualizations

---

## 📝 Version History

### Version 1.0.0 (Current)
- Initial release
- TimeGPT-1-long-horizon integration
- MA-6 fallback
- Indonesian holiday support
- Multi-level aggregation
- Excel/CSV export
- Interactive visualizations

---

**Powered by TimeGPT | Developed by Irsandi Habibie**

© 2025 Fleet Forecasting Engine. All rights reserved.
