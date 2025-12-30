import streamlit as st
import ee
import geemap.foliumap as geemap
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
from streamlit_folium import st_folium

st.set_page_config(page_title="Climate Classification", layout="wide")

@st.cache_resource
def initialize_ee():
    try:
        ee.Initialize()
        return True
    except:
        try:
            ee.Authenticate()
            ee.Initialize()
            return True
        except:
            return False

def get_climate_data(geometry, start_year, end_year):
    """Get climate data from ERA5"""
    era5 = ee.ImageCollection("ECMWF/ERA5/MONTHLY")
    
    # Filter by date range
    start_date = f'{start_year}-01-01'
    end_date = f'{end_year}-12-31'
    
    collection = era5.filterDate(start_date, end_date)
    
    # Calculate annual means
    years = list(range(start_year, end_year + 1))
    annual_data = []
    
    for year in years:
        year_data = collection.filterDate(f'{year}-01-01', f'{year}-12-31')
        
        # Temperature (convert K to C)
        temp_mean = year_data.select('mean_2m_air_temperature').mean().subtract(273.15)
        
        # Precipitation (convert m to mm)
        precip_sum = year_data.select('total_precipitation').sum().multiply(1000)
        
        # Reduce over geometry
        temp_stats = temp_mean.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=25000,
            maxPixels=1e9
        )
        
        precip_stats = precip_sum.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=25000,
            maxPixels=1e9
        )
        
        annual_data.append({
            'year': year,
            'temperature': temp_stats,
            'precipitation': precip_stats
        })
    
    return annual_data

def classify_koppen(temp_annual, precip_annual):
    """Simplified Köppen-Geiger classification"""
    if temp_annual < -3:
        return "ET" if precip_annual < 400 else "Df"
    elif temp_annual < 18:
        return "BS" if precip_annual < 500 else "Cf"
    else:
        return "BW" if precip_annual < 600 else "Af"

def create_climate_map():
    """Create interactive climate map"""
    Map = geemap.Map(center=[40, -100], zoom=3)
    
    # Add temperature layer
    era5_temp = ee.ImageCollection("ECMWF/ERA5/MONTHLY") \
        .filterDate('2020-01-01', '2020-12-31') \
        .select('mean_2m_air_temperature') \
        .mean() \
        .subtract(273.15)
    
    temp_vis = {
        'min': -30,
        'max': 30,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
    }
    
    Map.addLayer(era5_temp, temp_vis, 'Mean Temperature 2020 (°C)')
    
    # Add precipitation layer
    era5_precip = ee.ImageCollection("ECMWF/ERA5/MONTHLY") \
        .filterDate('2020-01-01', '2020-12-31') \
        .select('total_precipitation') \
        .sum() \
        .multiply(1000)
    
    precip_vis = {
        'min': 0,
        'max': 2000,
        'palette': ['white', 'blue', 'darkblue']
    }
    
    Map.addLayer(era5_precip, precip_vis, 'Annual Precipitation 2020 (mm)')
    
    return Map

def plot_climate_time_series(data, location_name):
    """Plot climate time series"""
    years = []
    temps = []
    precips = []
    
    for item in data:
        temp_val = item['temperature'].getInfo().get('mean_2m_air_temperature')
        precip_val = item['precipitation'].getInfo().get('total_precipitation')
        
        if temp_val is not None and precip_val is not None:
            years.append(item['year'])
            temps.append(temp_val)
            precips.append(precip_val)
    
    if not years:
        return None
    
    fig = go.Figure()
    
    # Temperature trace
    fig.add_trace(go.Scatter(
        x=years,
        y=temps,
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='red', width=2),
        yaxis='y'
    ))
    
    # Precipitation trace
    fig.add_trace(go.Scatter(
        x=years,
        y=precips,
        mode='lines+markers',
        name='Precipitation (mm)',
        line=dict(color='blue', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f'Climate Data - {location_name}',
        xaxis_title='Year',
        yaxis=dict(
            title='Temperature (°C)',
            side='left',
            titlefont=dict(color='red'),
            tickfont=dict(color='red')
        ),
        yaxis2=dict(
            title='Precipitation (mm)',
            side='right',
            overlaying='y',
            titlefont=dict(color='blue'),
            tickfont=dict(color='blue')
        ),
        height=500
    )
    
    return fig

def main():
    st.title("Climate Classification Analysis")
    st.write("Interactive Köppen-Geiger climate analysis using ERA5 data")
    
    if not initialize_ee():
        st.error("Earth Engine authentication required")
        st.stop()
    
    # Sidebar controls
    with st.sidebar:
        st.header("Analysis Parameters")
        
        start_year = st.number_input(
            "Start Year",
            value=2010,
            min_value=1979,
            max_value=2022
        )
        
        end_year = st.number_input(
            "End Year",
            value=2022,
            min_value=1979,
            max_value=2022
        )
        
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["Interactive Map", "Point Analysis", "Regional Analysis"]
        )
    
    if analysis_mode == "Interactive Map":
        st.subheader("Interactive Climate Map")
        st.write("Explore global temperature and precipitation patterns")
        
        # Layer selection
        layer_type = st.radio(
            "Display Layer",
            ["Temperature", "Precipitation", "Both"]
        )
        
        # Create and display map
        Map = create_climate_map()
        
        # Modify layers based on selection
        if layer_type == "Temperature":
            # Remove precipitation layer logic would go here
            pass
        elif layer_type == "Precipitation":
            # Remove temperature layer logic would go here
            pass
        
        map_data = st_folium(Map, width=700, height=500)
        
        # Process map clicks
        if map_data['last_object_clicked_popup']:
            coords = map_data['last_object_clicked_popup']
            st.write(f"Clicked coordinates: {coords}")
    
    elif analysis_mode == "Point Analysis":
        st.subheader("Point Climate Analysis")
        
        # Coordinate input
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=40.0, format="%.4f")
        with col2:
            lon = st.number_input("Longitude", value=-100.0, format="%.4f")
        
        if st.button("Analyze Climate"):
            point = ee.Geometry.Point([lon, lat])
            
            with st.spinner("Processing climate data..."):
                climate_data = get_climate_data(point, start_year, end_year)
            
            if climate_data:
                # Plot time series
                fig = plot_climate_time_series(
                    climate_data, 
                    f"Point ({lat:.3f}, {lon:.3f})"
                )
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Calculate climate classification
                recent_data = climate_data[-1]
                temp_val = recent_data['temperature'].getInfo().get('mean_2m_air_temperature', 0)
                precip_val = recent_data['precipitation'].getInfo().get('total_precipitation', 0)
                
                climate_type = classify_koppen(temp_val, precip_val)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Recent Temperature", f"{temp_val:.1f}°C")
                with col2:
                    st.metric("Recent Precipitation", f"{precip_val:.0f} mm")
                with col3:
                    st.metric("Climate Type", climate_type)
                
                # Data export
                if st.checkbox("Show raw data"):
                    df_data = []
                    for item in climate_data:
                        temp_val = item['temperature'].getInfo().get('mean_2m_air_temperature')
                        precip_val = item['precipitation'].getInfo().get('total_precipitation')
                        
                        if temp_val is not None and precip_val is not None:
                            df_data.append({
                                'Year': item['year'],
                                'Temperature (°C)': temp_val,
                                'Precipitation (mm)': precip_val,
                                'Climate Type': classify_koppen(temp_val, precip_val)
                            })
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        st.dataframe(df)
                        
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            f"climate_analysis_{lat}_{lon}.csv",
                            "text/csv"
                        )
    
    elif analysis_mode == "Regional Analysis":
        st.subheader("Regional Climate Analysis")
        
        # Predefined regions
        regions = {
            "North America": ee.Geometry.Rectangle([-140, 25, -60, 70]),
            "Europe": ee.Geometry.Rectangle([-10, 35, 40, 70]),
            "Amazon Basin": ee.Geometry.Rectangle([-75, -15, -45, 5])
        }
        
        selected_region = st.selectbox("Select Region", list(regions.keys()))
        
        if st.button("Analyze Region"):
            geometry = regions[selected_region]
            
            with st.spinner(f"Analyzing {selected_region}..."):
                climate_data = get_climate_data(geometry, start_year, end_year)
            
            if climate_data:
                fig = plot_climate_time_series(climate_data, selected_region)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
