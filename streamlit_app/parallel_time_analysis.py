import streamlit as st
import pandas as pd
import altair as alt


def create_parallel_time_analysis(df):
    # Add incident type selector
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for Parallel Analysis",
        incident_options,
        key="parallel_analysis_radio"
    )

    # Filter data based on selection
    if selected_incident != 'All Types':
        df = df[df['incident_category'] == selected_incident]

    # Create yearly aggregation
    yearly_data = df.groupby('incident_year').size().reset_index(name='count')
    avg_count = yearly_data['count'].mean()

    # Create vertical rules for each year
    year_rules = alt.Chart(yearly_data).mark_rule(
        strokeDash=[2, 2],
        color='gray',
        opacity=0.5
    ).encode(
        x='incident_year:O'
    )

    # Create a single chart instead of multiple segments
    base = alt.Chart(yearly_data).encode(
        x=alt.X('incident_year:O',
                axis=alt.Axis(title='Year', labelAngle=0)),
        y=alt.Y('count:Q',
                axis=alt.Axis(title='Number of Incidents'),
                scale=alt.Scale(domain=[0, yearly_data['count'].max() * 1.1]))
    )

    # Create connected line
    line = base.mark_line(
        color='green',
        strokeWidth=2,
        point=True  # Add points at each year
    ).encode(
        tooltip=[
            alt.Tooltip('incident_year:O', title='Year'),
            alt.Tooltip('count:Q', title='Incidents', format=',d')
        ]
    )

    # Add points for emphasis
    points = base.mark_circle(
        color='green',
        size=100
    )

    # Update text color to white
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        fontSize=12,
        color='white'
    ).encode(
        text=alt.Text('count:Q', format=',d')
    )

    # Add average line
    avg_line = alt.Chart(pd.DataFrame({
        'y': [avg_count]
    })).mark_rule(
        color='red',
        strokeDash=[5, 5],
        strokeWidth=2
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='Average', format=',d')]
    )

    # Combine all elements
    parallel_chart = (year_rules + line + points + text + avg_line).properties(
        title=f'Time Series View - {selected_incident}',
        width='container',
        height=500
    )

    return (parallel_chart,
            yearly_data['count'].sum(),
            avg_count,
            yearly_data.loc[yearly_data['count'].idxmax(), 'incident_year'],
            selected_incident)
