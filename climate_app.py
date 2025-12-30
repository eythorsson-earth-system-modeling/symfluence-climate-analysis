#!/usr/bin/env python3
"""
SYMFLUENCE Köppen-Geiger Climate Classification Tool
Advanced climate analysis using Google Earth Engine
Built by Darri Eythorsson - University of Calgary
"""

import streamlit as st
import ee
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
import json

# Page config
st.set_page_config(
    page_title="SYMFLUENCE Climate Analysis",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #28a745 0%, #17a2b8 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .climate-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_ee():
    """Initialize Earth Engine"""
    try:
        ee.Initialize()
        return True, "✅ Earth Engine connected successfully"
    except Exception as e:
        try:
            ee.Authenticate()
            ee.Initialize()
            return True, "✅ Earth Engine authenticated and connected"
        except Exception as e2:
            return False, f"❌ Earth Engine initialization failed: {str(e2)}"

def analyze_point_climate(lat, lon, start_year, end_year):
    """Analyze climate at a specific point using ECMWF ERA5 data"""
    
    try:
        point = ee.Geometry.Point([lon, lat])
        
        # Use ERA5 monthly data instead of NASA NEX-GDDP
        era5_monthly = ee.ImageCollection("ECMWF/ERA5/MONTHLY")
        
        climate_data = []
        
        for year in range(start_year, end_year + 1):
            yearly_data = era5_monthly.filterDate(f'{year}-01-01', f'{year}-12-31')
            
            # Temperature (convert from Kelvin to Celsius)
            temp_2m = yearly_data.select('mean_2m_air_temperature').mean().subtract(273.15)
            
            # Precipitation (convert from m to mm)
            precip = yearly_data.select('total_precipitation').sum().multiply(1000)
            
            # Extract values at point
            temp_value = temp_2m.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=25000,
                maxPixels=1e6
            ).getInfo()
            
            precip_value = precip.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=25000,
                maxPixels=1e6
            ).getInfo()
            
            climate_data.append({
                'year': year,
                'tmean_annual': temp_value.get('mean_2m_air_temperature', 0),
                'prec_annual': precip_value.get('total_precipitation', 0)
            })
        
        return pd.DataFrame(climate_data)
        
    except Exception as e:
        st.error(f"Climate analysis failed: {str(e)}")
        return None

def classify_climate_type(tmean, prec):
    """Simplified Köppen-Geiger classification"""
    
    if tmean < -3:
        if prec < 400:
            return "ET - Tundra"
        else:
            return "Df - Continental"
    elif tmean < 18:
        if prec < 500:
            return "BS - Semi-arid"
        else:
            return "Cf - Temperate"
    else:
        if prec < 600:
            return "BW - Arid"
        else:
            return "Af - Tropical"

def create_climate_time_series(df, lat, lon):
    """Create climate time series chart"""
    
    fig = go.Figure()
    
    # Temperature
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['tmean_annual'],
        mode='lines+markers',
        name='Mean Temperature (°C)',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=6),
        yaxis='y'
    ))
    
    # Precipitation
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['prec_annual'],
        mode='lines+markers',
        name='Annual Precipitation (mm)',
        line=dict(color='#007bff', width=3),
        marker=dict(size=6),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f'Climate Time Series - Point ({lat:.3f}, {lon:.3f})',
        xaxis_title='Year',
        yaxis=dict(
            title='Temperature (°C)',
            side='left',
            titlefont=dict(color='#dc3545'),
            tickfont=dict(color='#dc3545')
        ),
        yaxis2=dict(
            title='Precipitation (mm)',
            side='right',
            overlaying='y',
            titlefont=dict(color='#007bff'),
            tickfont=dict(color='#007bff')
        ),
        height=500,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_climate_dashboard(df):
    """Create climate statistics dashboard"""
    
    if df.empty:
        return
    
    # Calculate climate statistics
    temp_trend = np.polyfit(df['year'], df['tmean_annual'], 1)[0]  # Slope
    prec_trend = np.polyfit(df['year'], df['prec_annual'], 1)[0]
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌡️ Mean Temp", f"{df['tmean_annual'].mean():.1f}°C")
    
    with col2:
        st.metric("🌧️ Mean Precip", f"{df['prec_annual'].mean():.0f} mm")
    
    with col3:
        st.metric("📈 Temp Trend", f"{temp_trend:.3f}°C/year", 
                 delta=f"{temp_trend:.3f}" if temp_trend != 0 else None)
    
    with col4:
        st.metric("📊 Precip Trend", f"{prec_trend:.1f} mm/year",
                 delta=f"{prec_trend:.1f}" if prec_trend != 0 else None)
    
    with col5:
        # Classify current climate
        recent_climate = classify_climate_type(
            df['tmean_annual'].iloc[-1],
            df['prec_annual'].iloc[-1]
        )
        st.metric("🌍 Climate Type", recent_climate)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 SYMFLUENCE Climate Classification</h1>
        <p>Köppen-Geiger climate analysis using ECMWF ERA5 data</p>
        <p><em>Built by Darri Eythorsson, University of Calgary</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize Earth Engine
    ee_status, ee_message = initialize_ee()
    
    if ee_status:
        st.success(ee_message)
    else:
        st.error(ee_message)
        st.info("Please authenticate with Google Earth Engine to use this application.")
        st.stop()
    
    # Sidebar controls
    st.sidebar.markdown("## 🌡️ Climate Analysis Controls")
    
    st.markdown("## 📍 Point Climate Analysis")
    
    # Coordinate input
    col1, col2 = st.columns(2)
    with col1:
        input_lat = st.number_input("Latitude", value=51.1784, min_value=-90.0, max_value=90.0, step=0.01, format="%.4f")
    with col2:
        input_lon = st.number_input("Longitude", value=-115.5708, min_value=-180.0, max_value=180.0, step=0.01, format="%.4f")
    
    # Year range
    col1, col2 = st.columns(2)
    with col1:
        start_year = st.number_input("Start Year", value=2010, min_value=1979, max_value=2022, step=1)
    with col2:
        end_year = st.number_input("End Year", value=2022, min_value=1979, max_value=2022, step=1)
    
    if st.button("🚀 Analyze Climate", type="primary"):
        if start_year >= end_year:
            st.error("❌ Start year must be before end year")
            st.stop()
        
        with st.spinner(f"🔄 Analyzing climate at ({input_lat:.4f}, {input_lon:.4f})..."):
            climate_df = analyze_point_climate(input_lat, input_lon, start_year, end_year)
        
        if climate_df is not None and not climate_df.empty:
            # Display results
            st.markdown("### 📊 Climate Analysis Results")
            
            # Climate dashboard
            create_climate_dashboard(climate_df)
            
            # Time series chart
            climate_chart = create_climate_time_series(climate_df, input_lat, input_lon)
            st.plotly_chart(climate_chart, use_container_width=True)
            
            # Climate classification over time
            st.markdown("### 🌍 Climate Classification Over Time")
            
            climate_df['climate_type'] = climate_df.apply(
                lambda row: classify_climate_type(row['tmean_annual'], row['prec_annual']), 
                axis=1
            )
            
            # Show climate evolution
            climate_evolution = climate_df[['year', 'climate_type']].copy()
            st.dataframe(climate_evolution, use_container_width=True)
            
            # Download data
            st.markdown("### 💾 Download Climate Data")
            csv_data = climate_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Climate Analysis CSV",
                data=csv_data,
                file_name=f"climate_analysis_{input_lat:.4f}_{input_lon:.4f}_{start_year}_{end_year}.csv",
                mime="text/csv"
            )
        else:
            st.warning("❌ No climate data found for the specified location and period")
    
    # Welcome info
    st.markdown("## 🌟 About This Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Features
        - **Point Climate Analysis**: Detailed location-specific climate data
        - **Köppen-Geiger Classification**: Automatic climate type identification
        - **Time Series Analysis**: Multi-decade climate trends
        - **Temperature & Precipitation**: Dual-axis visualizations
        - **Climate Evolution**: Track climate type changes over time
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Data Sources
        - **ECMWF ERA5**: High-quality reanalysis data
        - **Time Range**: 1979-2022 (monthly resolution)
        - **Resolution**: 25km global coverage
        - **Variables**: Temperature, Precipitation
        - **Quality**: Research-grade climate data
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <strong>SYMFLUENCE Köppen-Geiger Climate Classification Tool</strong><br>
        Advanced climate analysis using ECMWF ERA5 reanalysis data<br>
        Built by <strong>Darri Eythorsson</strong>, University of Calgary<br>
        Contact: <a href='mailto:darri@symfluence.org'>darri@symfluence.org</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
