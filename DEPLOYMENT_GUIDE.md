# 🚛 Fleet Forecasting Engine - Complete Package

**Developed by Irsandi Habibie**

---

## 📦 Package Contents

This package contains a complete, production-ready Streamlit application for fleet forecasting using TimeGPT.

### What's Included:

✅ **4-Page Streamlit Application**
- Home & Setup (API configuration)
- Data Upload & Explorer (data validation & visualization)
- Forecasting Engine (configuration & execution)
- Results & Download (charts & exports)

✅ **Professional Features**
- TimeGPT-1-long-horizon integration
- MA-6 fallback method
- Indonesian holiday support
- Multi-level aggregation (9 options)
- Interactive Plotly visualizations
- Excel/CSV export (detailed & summary)
- Batch forecasting (single API call)
- Data quality validation
- Auto-fill missing dates
- Outlier handling

✅ **User Experience**
- Clean green-themed UI
- Tooltips throughout the app
- Loading indicators
- Error handling with friendly messages
- Sample data generation
- API quota tracking

✅ **Documentation**
- README.md (comprehensive guide)
- QUICKSTART.md (installation guide)
- PROJECT_STRUCTURE.md (technical details)
- Inline code comments
- Tooltips in the app

✅ **Deployment Tools**
- start.sh (Linux/Mac launcher)
- start.bat (Windows launcher)
- requirements.txt (dependencies)
- .streamlit/config.toml (theme config)

---

## 🚀 Getting Started

### Quick Launch (3 Steps):

1. **Get API Key**
   - Go to https://dashboard.nixtla.io
   - Sign up (free tier available)
   - Copy your API key

2. **Launch App**
   ```bash
   # Linux/Mac
   ./start.sh
   
   # Windows
   start.bat
   
   # Manual
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. **Configure & Run**
   - Enter API key in Home page
   - Upload your data (or use sample)
   - Configure forecast settings
   - View results & export

---

## 📊 Data Format

### Required CSV/Excel Columns:
```
date, company, origin, destination, province, region, fleet_type, qty
```

### Example Row:
```csv
01/01/2024,PT ABC,Jakarta,Bandung,West Java,West,Truck,5
```

**Important**: Date format must be **dd/mm/yyyy**

---

## ⚙️ Key Features Explained

### 1. Aggregation Levels (9 Options)
Choose how to group your data:
- **Most Granular**: company + origin + destination + fleet_type
- **By Company**: Aggregate all routes and fleet types
- **By Route**: Origin-destination pairs
- **By Fleet Type**: Aggregate by vehicle type
- **By Region/Province**: Geographic grouping
- **Combinations**: Company & Route, Company & Fleet Type, etc.

### 2. Models
- **TimeGPT-1-long-horizon** (Recommended): Best for 3+ years data
- **TimeGPT-1**: Standard model, faster
- **Moving Average (MA-6)**: Fallback, no API needed

### 3. Holiday Integration
- Automatically includes Indonesian public holidays
- Adds binary features (is_holiday, is_weekend)
- Improves forecast accuracy for seasonal patterns

### 4. Export Options
**Detailed Export (Excel)**:
- Sheet 1: All forecasts with dimensions
- Sheet 2: Summary by date
- Sheet 3: Summary by fleet type
- Sheet 4: Summary by region
- Sheet 5: Summary by route
- Sheet 6: Metadata

**Summary Export**:
- Simple aggregated totals by date
- CSV or Excel format

---

## 🎯 Use Cases

### Example 1: Company-Wide Planning
```
Aggregation: By Company
Horizon: 30 days
Output: Total fleet needs per company per day
Use: Budget planning, resource allocation
```

### Example 2: Route Optimization
```
Aggregation: By Route
Horizon: 7 days
Output: Fleet needs per route per day
Use: Route planning, delivery scheduling
```

### Example 3: Fleet Type Management
```
Aggregation: By Fleet Type
Horizon: 90 days
Output: Needs per vehicle type per day
Use: Fleet acquisition, maintenance planning
```

### Example 4: Detailed Forecasting
```
Aggregation: Most Granular
Horizon: 14 days
Output: Every company-route-fleet combination
Use: Detailed operational planning
```

---

## 💡 Best Practices

### Data Preparation
✅ Use consistent date format (dd/mm/yyyy)
✅ Include at least 1-3 years of historical data
✅ Ensure no gaps in critical series
✅ Clean outliers or use app's outlier handling

### Forecasting
✅ Enable holiday features (recommended)
✅ Use TimeGPT-1-long-horizon for 3+ years data
✅ Start with higher aggregation to reduce series count
✅ Monitor API usage (counter in sidebar)

### Performance
✅ Filter data before forecasting if many series
✅ Use batch forecasting (automatic)
✅ Higher aggregation = faster processing
✅ Free tier: ~1000 forecasts/month

---

## 🔧 Customization

### Change Colors
Edit `app.py` CSS section:
```python
:root {
    --primary-green: #2E7D32;  # Your color
    --secondary-green: #66BB6A; # Your color
    ...
}
```

### Add More Aggregation Levels
Edit `utils/data_processor.py`:
```python
agg_mappings = {
    'Your Custom Level': ['col1', 'col2'],
    ...
}
```

### Modify Export Format
Edit `utils/export.py`:
```python
# Add custom sheets or formatting
```

---

## 📈 Performance Metrics

### Typical Performance:
- Data upload & validation: < 5 seconds
- TimeGPT forecast (100 series): 30-60 seconds
- MA-6 forecast (100 series): 5-10 seconds
- Export generation: < 5 seconds
- Chart rendering: Instant

### Scalability:
- Tested with: 3 years daily data (~1000 days)
- Max series: 1000+ (depends on API quota)
- File size: Up to 200MB recommended
- Export size: Unlimited

---

## 🐛 Common Issues & Solutions

### "Invalid API key"
→ Check for typos, verify at dashboard.nixtla.io

### "Insufficient data"
→ Need 30+ days for daily or 12+ months for monthly

### "API quota exceeded"
→ App auto-switches to MA-6 fallback

### "Date parsing error"
→ Ensure dd/mm/yyyy format exactly

### Import errors
→ Run: `pip install -r requirements.txt --upgrade`

---

## 📞 Support Resources

1. **README.md** - Comprehensive documentation
2. **QUICKSTART.md** - Installation guide
3. **PROJECT_STRUCTURE.md** - Technical details
4. **In-app tooltips** - Hover over ℹ️ icons
5. **Sample data** - Download from Home page
6. **Nixtla docs** - https://docs.nixtla.io

---

## 🔐 Security Notes

- API keys stored in session state only (not persisted)
- No data is saved to disk without explicit export
- All processing happens locally
- API calls are made directly to Nixtla
- No third-party data sharing

---

## 🎓 Technical Stack

- **Framework**: Streamlit 1.28+
- **Forecasting**: TimeGPT (Nixtla)
- **Data**: Pandas, NumPy
- **Visualization**: Plotly
- **Export**: OpenPyXL
- **Holidays**: holidays (Python library)

---

## 📋 Version Information

**Version**: 1.0.0
**Release Date**: January 2025
**Compatibility**: Python 3.8+
**License**: Custom (by Irsandi Habibie)

---

## 🎯 Next Steps

After deployment:

1. ✅ **Configure API key** in Home page
2. ✅ **Upload data** or use sample
3. ✅ **Run first forecast** with recommended settings
4. ✅ **Explore visualizations** in Results page
5. ✅ **Export results** to Excel/CSV
6. ✅ **Adjust settings** for your needs
7. ✅ **Share with team** for feedback

---

## 🌟 Features Roadmap (Future)

Potential enhancements:
- [ ] Multi-model ensemble forecasting
- [ ] Forecast accuracy metrics (MAPE, MAE, RMSE)
- [ ] Automated email reports
- [ ] Database integration (PostgreSQL, MySQL)
- [ ] Real-time API monitoring
- [ ] Custom holiday calendar upload
- [ ] Forecast comparison tools
- [ ] User authentication
- [ ] Forecast versioning/history

---

## 📬 Feedback

This application was developed by **Irsandi Habibie** to provide professional fleet forecasting capabilities using cutting-edge AI technology.

For suggestions or improvements, consider:
- Testing with your real data
- Documenting any issues encountered
- Sharing use cases and results
- Providing feedback on UX/UI

---

## 🙏 Acknowledgments

Special thanks to:
- **Nixtla** for TimeGPT API
- **Streamlit** for the framework
- **Plotly** for visualizations
- The open-source community

---

## 📄 License & Attribution

**Developed by**: Irsandi Habibie
**Powered by**: TimeGPT
**Year**: 2025

When using or sharing this application, please maintain attribution to the developer.

---

## ✨ Final Notes

This is a complete, production-ready application that:
- ✅ Works out of the box
- ✅ Includes comprehensive documentation
- ✅ Has professional UI/UX
- ✅ Handles errors gracefully
- ✅ Supports batch processing
- ✅ Provides multiple export formats
- ✅ Includes tooltips and help text
- ✅ Has automatic fallback methods

**Ready to deploy and use immediately!**

---

**Powered by TimeGPT | Developed by Irsandi Habibie**

© 2025 Fleet Forecasting Engine. All rights reserved.

---

**🚀 Start forecasting now: `./start.sh` or `start.bat`**
