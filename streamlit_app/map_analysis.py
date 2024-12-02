import streamlit as st
import pandas as pd


def create_map_analysis(df):
    """Create an interactive map visualization for incidents"""

    # Add incident type selector in sidebar
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for Map",
        incident_options,
        key="map_analysis_radio"
    )

    # Filter data based on selection and cache the result
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_filtered_data(df, incident_type):
        if (incident_type != 'All Types'):
            filtered_df = df[df['incident_category'] == incident_type].copy()
        else:
            filtered_df = df.copy()
        return filtered_df.dropna(subset=['latitude', 'longitude'])

    map_df = get_filtered_data(df, selected_incident)

    # Create container for map with custom styling
    st.markdown("""
        <style>
        .big-map {
            margin: 1rem 0;
            padding: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="big-map">', unsafe_allow_html=True)
        # Create the map showing all incidents
        st.map(
            data=map_df,
            latitude='latitude',
            longitude='longitude',
            size=st.sidebar.slider("Point Size", 1, 30, 5),
            color=[255, 50, 50, 3],
            zoom=None,
            use_container_width=True,
            height=500
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Add incident details in an expander with simpler view
    with st.expander("View Incident Details", expanded=False):
        st.info(f"Showing all {len(map_df):,} incidents")
        st.dataframe(
            map_df[['incident_category', 'incident_date', 'incident_time']],
            use_container_width=True,
            height=400
        )

    # Calculate metrics - now total_incidents shows all incidents
    total_incidents = len(map_df)
    unique_locations = len(map_df.groupby(['latitude', 'longitude']).size())

    return total_incidents, unique_locations, selected_incident
