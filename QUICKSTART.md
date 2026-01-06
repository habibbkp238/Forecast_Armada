# 🚀 Quick Start Guide

## Fleet Forecasting Engine
**Developed by Irsandi Habibie**

---

## Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Internet connection
- ✅ Nixtla API key (get free at https://dashboard.nixtla.io)

---

## Installation Methods

### Method 1: Using Startup Scripts (Recommended)

#### On Linux/Mac:
```bash
cd fleet_forecasting_app
chmod +x start.sh
./start.sh
```

#### On Windows:
```cmd
cd fleet_forecasting_app
start.bat
```

The script will:
1. Create a virtual environment
2. Install all dependencies
3. Launch the application

---

### Method 2: Manual Installation

#### Step 1: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# Activate on Linux/Mac:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Run the Application
```bash
streamlit run app.py
```

---

## First Time Setup

### 1. Get Your API Key
1. Visit https://dashboard.nixtla.io
2. Sign up for a free account
3. Copy your API key

### 2. Launch the App
- The app will automatically open in your browser at `http://localhost:8501`
- If not, manually open: http://localhost:8501

### 3. Configure API Key
1. Go to the "🏠 Home & Setup" page
2. Paste your API key
3. Click "Validate"

### 4. Download Sample Data (Optional)
1. Click "📥 Download Sample" on the Home page
2. Use this to test the app

---

## Quick Usage Flow

```
1. Home & Setup
   ↓ Enter API key
   ↓ Download sample data (optional)
   
2. Data Upload & Explorer
   ↓ Upload your CSV/Excel file
   ↓ Review data quality
   ↓ Explore visualizations
   
3. Forecasting Engine
   ↓ Select aggregation level
   ↓ Set forecast horizon
   ↓ Enable holidays (recommended)
   ↓ Choose model
   ↓ Run forecast
   
4. Results & Download
   ↓ View visualizations
   ↓ Export to Excel/CSV
   ✓ Done!
```

---

## Sample Data Format

Your CSV/Excel file should have these columns:

| date | company | origin | destination | province | region | fleet_type | qty |
|------|---------|--------|-------------|----------|--------|------------|-----|
| 01/01/2024 | PT ABC | Jakarta | Bandung | West Java | West | Truck | 5 |
| 01/01/2024 | PT ABC | Jakarta | Surabaya | East Java | East | Van | 3 |

**Important**: Date format must be dd/mm/yyyy (e.g., 31/12/2024)

---

## Troubleshooting

### App won't start?
```bash
# Check Python version (must be 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### API key validation fails?
- Check for typos or extra spaces
- Verify key is active at https://dashboard.nixtla.io
- Ensure internet connection is working

### Date parsing errors?
- Ensure dates are in dd/mm/yyyy format
- Check for invalid dates (e.g., 32/01/2024)
- Remove any text in the date column

### Import errors?
```bash
# Reinstall specific packages
pip install streamlit --upgrade
pip install nixtla --upgrade
```

---

## System Requirements

### Minimum:
- Python 3.8+
- 2GB RAM
- 500MB free disk space
- Internet connection

### Recommended:
- Python 3.10+
- 4GB RAM
- 1GB free disk space
- Stable internet connection

---

## Getting Help

1. **Read the README.md** for detailed documentation
2. **Check tooltips** in the app (hover over ℹ️ icons)
3. **Download sample data** to see correct format
4. **Visit Nixtla docs**: https://docs.nixtla.io

---

## Next Steps

After installation:
1. ✅ Configure your API key
2. ✅ Upload or use sample data
3. ✅ Run your first forecast
4. ✅ Explore the visualizations
5. ✅ Export your results

---

## Support

For issues or questions, review:
- README.md (comprehensive guide)
- In-app tooltips (context-specific help)
- Nixtla documentation (API-specific questions)

---

**Powered by TimeGPT | Developed by Irsandi Habibie**

© 2025 Fleet Forecasting Engine
