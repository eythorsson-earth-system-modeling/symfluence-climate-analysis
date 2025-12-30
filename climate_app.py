import streamlit as st
import ee
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Climate Analysis", layout="wide")

@st.cache_resource
def init_ee():
    try:
        ee.Initialize()
        return True
    except:
        return False

@st.cache_data(ttl=3600)
def get_climate_data(lat, lon, start_year, end_year):
    """Cached climate data retrieval"""
    point = ee.Geometry.Point([lon, lat])
    
    # Use ERA5 monthly data
    era5 = ee.ImageCollection("ECMWF/ERA5/MONTHLY") \
        .filterDate(f'{start_year}-01-01', f'{end_year}-12-31')
    
    # Calculate annual means efficiently
    years = list(range(start_year, end_year + 1))
    results = []
    
    for year in years:
        year_data = era5.filterDate(f'{year}-01-01', f'{year}-12-31')
        
        # Temperature (K to C)
        temp = year_data.select('mean_2m_air_temperature').mean().subtract(273.15)
        # Precipitation (m to mm)
        precip = year_data.select('total_precipitation').sum().multiply(1000)
        
        # Single reduceRegion call
        combined = ee.Image.cat([temp, precip])
        stats = combined.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=25000,
            maxPixels=1e6
        ).getInfo()
        
        results.append({
            'year': year,
            'temp': stats.get('mean_2m_air_temperature', 0),
            'precip': stats.get('total_precipitation', 0)
        })
    
    return results

def classify_climate(temp, precip):
    """Fast climate classification"""
    if temp < -3:
        return "ET" if precip < 400 else "Df"
    elif temp < 18:
        return "BS" if precip < 500 else "Cf"
    else:
        return "BW" if precip < 600 else "Af"

def plot_climate_data(data, location):
    """Fast dual-axis climate plot"""
    years = [d['year'] for d in data]
    temps = [d['temp'] for d in data]
    precips = [d['precip'] for d in data]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years, y=temps,
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='red', width=2),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=precips,
        mode='lines+markers',
        name='Precipitation (mm)',
        line=dict(color='blue', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f'Climate Data - {location}',
        xaxis_title='Year',
        yaxis=dict(title='Temperature (°C)', side='left', color='red'),
        yaxis2=dict(title='Precipitation (mm)', side='right', overlaying='y', color='blue'),
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def main():
    st.title("Climate Classification Analysis")
    
    if not init_ee():
        st.error("Earth Engine authentication required")
        st.stop()
    
    # Streamlined interface
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        lat = st.number_input("Latitude", value=40.0, format="%.3f")
    with col2:
        lon = st.number_input("Longitude", value=-100.0, format="%.3f")
    with col3:
        start_year = st.selectbox("Start Year", [2010, 2015, 2020], index=0)
    with col4:
        end_year = st.selectbox("End Year", [2020, 2022], index=1)
    
    # Auto-run analysis
    if st.button("Analyze", type="primary") or True:  # Auto-run
        with st.spinner("Processing..."):
            try:
                data = get_climate_data(lat, lon, start_year, end_year)
                
                if data:
                    # Plot time series
                    fig = plot_climate_data(data, f"({lat:.2f}, {lon:.2f})")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Quick stats and classification
                    recent = data[-1]
                    climate_type = classify_climate(recent['temp'], recent['precip'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Recent Temp", f"{recent['temp']:.1f}°C")
                    with col2:
                        st.metric("Recent Precip", f"{recent['precip']:.0f} mm")
                    with col3:
                        st.metric("Climate Type", climate_type)
                    with col4:
                        temp_trend = (data[-1]['temp'] - data[0]['temp']) / len(data)
                        st.metric("Temp Trend", f"{temp_trend:.2f}°C/yr")
                    
                    # Data table (optional)
                    if st.checkbox("Show data"):
                        df = pd.DataFrame(data)
                        df['climate_type'] = df.apply(lambda x: classify_climate(x['temp'], x['precip']), axis=1)
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button("Download CSV", csv, f"climate_{lat}_{lon}.csv")
                else:
                    st.warning("No climate data found")
                    
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    main()
