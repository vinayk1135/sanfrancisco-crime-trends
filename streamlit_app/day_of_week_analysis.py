import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt


def create_day_of_week_analysis(df):
    """Create star plot for incidents by day of week"""
    # Add incident type selector
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for Day Analysis",
        incident_options,
        key="day_analysis_radio"
    )

    # Filter data based on selection
    if selected_incident != 'All Types':
        df = df[df['incident_category'] == selected_incident]

    # Create day of week stats using incident_day_of_week
    days = ['Sunday', 'Monday', 'Tuesday',
            'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_counts = []

    for day in days:
        count = len(df[df['incident_day_of_week'] == day])
        day_counts.append(count)

    # Create the figure with updated styling
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=day_counts,
        theta=days,
        fill='toself',
        name=selected_incident,
        line=dict(color='#00b4d8', width=2),
    ))

    # Update layout with dark template
    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(
                visible=True,
                color='white',
                showline=True,
                showticklabels=True,
                gridcolor="rgba(255, 255, 255, 0.2)"
            ),
            angularaxis=dict(
                color='white',
                gridcolor="rgba(255, 255, 255, 0.2)"
            )
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text=f"Incidents by Day of Week - {
                selected_incident}<br><sup>(Star Plot / Glyph)</sup>",
            font=dict(color="white", size=20)
        ),
        showlegend=True
    )

    # Calculate statistics
    total_incidents = sum(day_counts)
    avg_per_day = total_incidents / 7
    peak_day = days[day_counts.index(max(day_counts))]
    lowest_day = days[day_counts.index(min(day_counts))]

    return fig, total_incidents, avg_per_day, peak_day, lowest_day, day_counts


def create_day_of_week_bar_analysis(df):
    """Create bar chart for incidents by day of week"""
    # Add incident type selector
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for Bar Analysis",
        incident_options,
        key="day_bar_analysis_radio"
    )

    # Filter data based on selection
    if selected_incident != 'All Types':
        df = df[df['incident_category'] == selected_incident]

    # Create day of week stats
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    df['incident_date'] = pd.to_datetime(df['incident_date'])
    df['day_of_week'] = df['incident_date'].dt.dayofweek

    # Create DataFrame for the chart
    day_counts = pd.DataFrame([
        {'day': days[day], 'count': len(
            df[df['day_of_week'] == day]), 'day_num': day}
        for day in range(7)
    ])

    # Create Altair chart
    base = alt.Chart(day_counts).encode(
        x=alt.X('day:N',
                sort=day_counts['day'].tolist(),  # Sort by actual day order
                title='Day of Week'),
        y=alt.Y('count:Q', title='Number of Incidents'),
        color=alt.condition(
            f"datum.count == {day_counts['count'].max()}",
            alt.value('red'),  # Highest bar in red
            alt.value('#1f77b4')  # Other bars in blue
        ),
        tooltip=[
            alt.Tooltip('day:N', title='Day'),
            alt.Tooltip('count:Q', title='Incidents', format=',d')
        ]
    )

    # Create bars
    bars = base.mark_bar()

    # Add text labels on top of bars
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        color='white'
    ).encode(
        text=alt.Text('count:Q', format=',d')
    )

    # Add average line
    avg_count = day_counts['count'].mean()
    avg_rule = alt.Chart(pd.DataFrame({'y': [avg_count]})).mark_rule(
        strokeDash=[5, 5],
        color='white',
        strokeWidth=2
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='Daily Average', format=',d')]
    )

    # Combine chart elements
    chart = (bars + text + avg_rule).properties(
        title=f'Incidents by Day of Week - {selected_incident}',
        width='container',
        height=500
    )

    return chart, day_counts['count'].sum(), avg_count, days[day_counts['count'].idxmax()], days[day_counts['count'].idxmin()]
