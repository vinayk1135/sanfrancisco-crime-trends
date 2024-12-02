import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np


def create_district_map_analysis(df):
    """Create an interactive district map visualization using Streamlit's map"""

    # District data with standardized names
    district_data = {
        'district_names': ['CENTRAL', 'NORTHERN', 'SOUTHERN', 'MISSION', 'RICHMOND', 'TARAVAL', 'INGLESIDE', 'BAYVIEW', 'TENDERLOIN', 'PARK'],
        'latitude': [37.751, 37.790, 37.778, 37.758, 37.78, 37.75, 37.72, 37.72, 37.79, 37.77],
        'longitude': [-122.45, -122.44, -122.40, -122.41, -122.48, -122.485, -122.46, -122.40, -122.413, -122.49]
    }

    # Convert to DataFrame
    districts_df = pd.DataFrame(district_data)

    # Clean the police_district column in the input DataFrame
    df['police_district'] = df['police_district'].str.upper()
    df = df.dropna(subset=['police_district'])

    # Add incident type selector in sidebar
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for District Map",
        incident_options,
        key="district_map_radio"
    )

    # Filter incidents based on selection
    if selected_incident != 'All Types':
        filtered_df = df[df['incident_category'] == selected_incident].copy()
    else:
        filtered_df = df.copy()

    # Count incidents per district
    district_counts = filtered_df['police_district'].value_counts()

    # Add incident counts and calculate normalized values for visualization
    districts_df['incident_count'] = districts_df['district_names'].map(
        lambda x: district_counts.get(x, 0))

    # Calculate normalized values for radius and color
    max_incidents = districts_df['incident_count'].max()
    districts_df['radius'] = districts_df['incident_count'].apply(
        lambda x: (x / max_incidents) * 1300 + 300)

    # Calculate opacity (between 40 and 200) and color intensity
    districts_df['opacity'] = districts_df['incident_count'].apply(
        lambda x: int((x / max_incidents) * 110 + 60))

    # Create a custom color for each point based on incident count
    districts_df['color'] = districts_df.apply(
        lambda row: [255,
                     # Less green for higher counts
                     max(0, int(
                         255 - (row['incident_count'] / max_incidents) * 255)),
                     0,
                     row['opacity']],
        axis=1)

    # Create the map layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        districts_df,
        get_position=["longitude", "latitude"],
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        opacity=0.8
    )

    # Set the viewport location
    view_state = pdk.ViewState(
        longitude=-122.44,
        latitude=37.76,
        zoom=12,
        min_zoom=11,
        max_zoom=15,
        pitch=0,
        bearing=0
    )

    # Combine everything and render with tooltip
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>District:</b> {district_names}<br/>"
            "<b>Incidents:</b> {incident_count}",
            "style": {
                "background": "white",
                "color": "black",
                "font-family": '"Helvetica Neue", Arial',
                "z-index": "10000"
            }
        }
    )

    st.pydeck_chart(r)

    # Update expander to show more details
    with st.expander("View District Details", expanded=False):
        details_df = districts_df[['district_names', 'incident_count']].copy()
        details_df.columns = ['District', 'Incidents']
        details_df = details_df.sort_values('Incidents', ascending=False)
        st.dataframe(details_df, use_container_width=True)

    # Calculate metrics
    total_incidents = int(districts_df['incident_count'].sum())
    num_districts = len(districts_df)
    busiest_district = details_df.iloc[0]['District'].title()

    return total_incidents, num_districts, busiest_district
