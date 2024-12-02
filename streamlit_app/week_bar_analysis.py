import streamlit as st
import pandas as pd
import altair as alt


def create_week_bar_analysis(df):
    """Create bar chart for incidents by day of week using incident_day_of_week"""
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for Week Analysis",
        incident_options,
        key="week_bar_analysis_radio"
    )

    # Filter data based on selection
    if selected_incident != 'All Types':
        df = df[df['incident_category'] == selected_incident]

    # Create day counts using incident_day_of_week
    day_counts = pd.DataFrame(
        df['incident_day_of_week'].value_counts()).reset_index()
    day_counts.columns = ['day', 'count']

    # Sort days in correct order
    day_order = ['Sunday', 'Monday', 'Tuesday',
                 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_counts['day_num'] = day_counts['day'].map(
        {day: i for i, day in enumerate(day_order)})
    day_counts = day_counts.sort_values('day_num')

    # Create Altair chart with updated colors
    base = alt.Chart(day_counts).encode(
        x=alt.X('day:N',
                sort=day_order,
                title='Day of Week'),
        y=alt.Y('count:Q', title='Number of Incidents'),
        color=alt.condition(
            f"datum.count == {day_counts['count'].max()}",
            alt.value('#ff3333'),  # Brighter red for highest
            alt.value('#00b4d8')  # Matching blue from polar plot
        ),
        tooltip=[
            alt.Tooltip('day:N', title='Day'),
            alt.Tooltip('count:Q', title='Incidents', format=',d')
        ]
    )

    bars = base.mark_bar(opacity=0.7)  # Add opacity to bars

    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        color='white'
    ).encode(
        text=alt.Text('count:Q', format=',d')
    )

    avg_count = day_counts['count'].mean()
    avg_rule = alt.Chart(pd.DataFrame({'y': [avg_count]})).mark_rule(
        strokeDash=[5, 5],
        color='#ff3333',  # Matching red color
        strokeWidth=2
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='Daily Average', format=',d')]
    )

    chart = (bars + text + avg_rule).properties(
        title=f'Incidents by Day of Week - {selected_incident}',
        width='container',
        height=500
    )

    # Fix peak and lowest day calculation
    peak_day = day_counts.loc[day_counts['count'].idxmax(), 'day']
    lowest_day = day_counts.loc[day_counts['count'].idxmin(), 'day']

    return chart, day_counts['count'].sum(), avg_count, peak_day, lowest_day
