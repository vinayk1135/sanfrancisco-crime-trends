import pandas as pd
import altair as alt
import streamlit as st


def create_larceny_grid_analysis(df):
    """Create grid bar chart analysis for larceny theft incidents by time"""
    # Filter for larceny theft
    larceny_df = df[df['incident_category'] == 'Larceny Theft'].copy()

    # Extract hour from incident_time
    larceny_df['hour'] = pd.to_datetime(
        larceny_df['incident_time'], format='%H:%M').dt.hour

    # Create time periods (morning, afternoon, evening, night)
    def get_period(hour):
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'

    larceny_df['period'] = larceny_df['hour'].apply(get_period)

    # Group by hour and period
    hourly_counts = larceny_df.groupby(['period', 'hour'])[
        'incident_category'].count().reset_index()
    hourly_counts.columns = ['period', 'hour', 'count']

    # Create grid bar chart
    chart = alt.Chart(hourly_counts).mark_bar().encode(
        x=alt.X('hour:O',
                title='Hour of Day',
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y('count:Q',
                title='Number of Incidents'),
        color=alt.Color('period:N',
                        scale=alt.Scale(
                            domain=['Morning', 'Afternoon',
                                    'Evening', 'Night'],
                            range=['#90EE90', '#FFD700', '#FF6B6B', '#4682B4']
                        )),
        tooltip=['period', 'hour', 'count']
    ).properties(
        title='Larceny Thefts by Hour and Time Period',
        width='container',
        height=400
    )

    # Create vertical rules for time period separators
    period_rules = alt.Chart(pd.DataFrame({
        'hour': [5, 12, 17, 21],  # Hours where periods change
        'label': ['Morning', 'Afternoon', 'Evening', 'Night']
    })).mark_rule(
        strokeDash=[5, 5],
        stroke='white',
        strokeWidth=1,
        opacity=0.5
    ).encode(
        x='hour:O'
    )

    # Add text labels above the rules
    period_labels = alt.Chart(pd.DataFrame({
        'hour': [2, 8, 14, 19],  # Centered positions for labels
        'label': ['Night', 'Morning', 'Afternoon', 'Evening'],
        'y': [max(hourly_counts['count']) * 1.1] * 4  # Position above the bars
    })).mark_text(
        color='white',
        fontSize=12
    ).encode(
        x='hour:O',
        y='y:Q',
        text='label'
    )

    # Combine base chart with rules and labels
    chart = alt.layer(
        chart,
        period_rules,
        period_labels
    ).properties(
        title='Larceny Thefts by Hour and Time Period',
        width='container',
        height=400
    )

    # Calculate metrics
    total = hourly_counts['count'].sum()
    avg = total / 24
    peak_hour = hourly_counts.loc[hourly_counts['count'].idxmax()]
    lowest_hour = hourly_counts.loc[hourly_counts['count'].idxmin()]

    return chart, total, avg, f"{int(peak_hour['hour']):02d}:00 ({peak_hour['period']})", f"{int(lowest_hour['hour']):02d}:00 ({lowest_hour['period']})"
