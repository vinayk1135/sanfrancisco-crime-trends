import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def create_larceny_analysis(df):
    """Create time vs count analysis for larceny theft incidents"""
    # Filter for larceny theft
    larceny_df = df[df['incident_category'] == 'Larceny Theft'].copy()

    # Convert incident_time to datetime
    larceny_df['incident_time'] = pd.to_datetime(
        larceny_df['incident_time'], format='%H:%M').dt.time

    # Group by hour and count incidents
    hourly_counts = larceny_df.groupby(larceny_df['incident_time'].apply(
        lambda x: x.hour))['incident_category'].count().reset_index()
    hourly_counts.columns = ['hour', 'count']

    # Create line plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hourly_counts['hour'],
        y=hourly_counts['count'],
        mode='lines+markers',
        name='Larceny Theft',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="Larceny Thefts by Time of Day",
        xaxis_title="Hour of Day (24-hour format)",
        yaxis_title="Number of Incidents",
        template='plotly_dark',
        showlegend=True,
        width=800,
        height=600
    )

    # Calculate metrics
    total = hourly_counts['count'].sum()
    avg = total / 24
    peak_hour = hourly_counts.loc[hourly_counts['count'].idxmax(), 'hour']
    lowest_hour = hourly_counts.loc[hourly_counts['count'].idxmin(), 'hour']

    return fig, total, avg, f"{peak_hour:02d}:00", f"{lowest_hour:02d}:00"
