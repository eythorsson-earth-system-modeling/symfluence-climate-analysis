# SYMFLUENCE Köppen-Geiger Climate Classification Tool

🌍 **Advanced climate analysis using NASA NEX-GDDP downscaled climate data**

Built by **Darri Eythorsson**, University of Calgary  
Contact: darri@symfluence.org

## 🚀 Features

- **📍 Point Climate Analysis**: Detailed location-specific climate data
- **🌡️ Köppen-Geiger Classification**: Automatic climate type identification  
- **📈 Time Series Analysis**: Multi-decade climate trends (1950-2100)
- **🌧️ Temperature & Precipitation**: Dual-axis visualizations
- **🔄 Climate Evolution**: Track climate type changes over time
- **📊 Statistical Analysis**: Trends, means, and climate metrics

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/eythorsson-earth-system-modeling/symfluence-climate-analysis.git
cd symfluence-climate-analysis

# Install dependencies
pip install -r climate_requirements.txt

# Set up Google Earth Engine authentication
earthengine authenticate
```

## 🎯 Usage

```bash
# Run the Streamlit app
streamlit run climate_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 Data Sources

- **NASA NEX-GDDP**: Downscaled Global Daily Downscaled Projections
- **Time Range**: 1950-2100 (historical and projections)
- **Resolution**: 25km global coverage
- **Variables**: Temperature (max/min), Precipitation
- **Scenarios**: Historical, RCP4.5, RCP8.5

## 🌟 Analysis Modes

### Point Climate Analysis
- Location-specific climate time series
- Automatic Köppen-Geiger classification
- Temperature and precipitation trends
- Climate type evolution over time
- Statistical summaries and metrics

### Regional Classification (Coming Soon)
- Interactive regional climate maps
- Climate zone boundaries
- Comparative analysis between regions
- Climate change projections

### Climate Trends (Coming Soon)
- Long-term temperature trends
- Precipitation pattern changes
- Climate shift detection
- Future scenario analysis

## 🌍 Köppen-Geiger Classification

The app implements simplified Köppen-Geiger climate classification:

- **ET - Tundra**: Mean temp < -3°C, low precipitation
- **Df - Continental**: Mean temp < -3°C, high precipitation  
- **BS - Semi-arid**: Cool temps, moderate precipitation
- **Cf - Temperate**: Moderate temps, adequate precipitation
- **BW - Arid**: Hot temps, low precipitation
- **Af - Tropical**: Hot temps, high precipitation

## 📈 Outputs

- **Interactive Time Series**: Temperature and precipitation trends
- **Climate Metrics**: Mean values, trends, classification
- **Climate Evolution**: Type changes over time
- **Export Options**: CSV download with full analysis data

## 🔬 Technical Details

- **Platform**: Google Earth Engine + Streamlit
- **Language**: Python 3.8+
- **Visualization**: Plotly interactive charts
- **Data Processing**: Earth Engine API with NASA NEX-GDDP
- **UI Framework**: Streamlit with custom gradient CSS

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📧 Contact

**Darri Eythorsson**  
University of Calgary  
Email: darri@symfluence.org  
Website: https://eythorsson-earth-system-modeling.github.io

## 🔗 Related Projects

- [SYMFLUENCE Snow Analysis](https://github.com/eythorsson-earth-system-modeling/symfluence-snow-analysis)
- [SYMFLUENCE Documentation](https://github.com/SYMFLUENCE/docs)
