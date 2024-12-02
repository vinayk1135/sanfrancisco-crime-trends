import pandas as pd
import plotly.graph_objects as go
import altair as alt
import streamlit as st


def create_larceny_analysis(df, analysis_type="line"):
    """Create larceny theft analysis with multiple visualization options"""
    # Filter for larceny theft
    larceny_df = df[df['incident_category'] == 'Larceny Theft'].copy()

    if analysis_type == "line":
        # Time vs Count line analysis
        larceny_df['hour'] = pd.to_datetime(
            larceny_df['incident_time'], format='%H:%M').dt.hour

        hourly_counts = larceny_df.groupby(
            'hour')['incident_category'].count().reset_index()
        hourly_counts.columns = ['hour', 'count']

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

        total = hourly_counts['count'].sum()
        avg = total / 24
        peak_time = f"{
            hourly_counts.loc[hourly_counts['count'].idxmax(), 'hour']:02d}:00"
        lowest_time = f"{
            hourly_counts.loc[hourly_counts['count'].idxmin(), 'hour']:02d}:00"

        return fig, total, avg, peak_time, lowest_time, "plotly"

    else:  # Grid analysis
        # Create time periods
        def get_period(hour):
            if 5 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 21:
                return 'Evening'
            else:
                return 'Night'

        # Extract hour and add period
        larceny_df['hour'] = pd.to_datetime(
            larceny_df['incident_time'], format='%H:%M').dt.hour
        larceny_df['period'] = larceny_df['hour'].apply(get_period)

        # Group by hour and period
        hourly_counts = larceny_df.groupby(['period', 'hour'])[
            'incident_category'].count().reset_index()
        hourly_counts.columns = ['period', 'hour', 'count']

        # Create base chart
        base_chart = alt.Chart(hourly_counts).mark_bar().encode(
            x=alt.X('hour:O', title='Hour of Day',
                    axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count:Q', title='Number of Incidents'),
            color=alt.Color('period:N',
                            scale=alt.Scale(
                                domain=['Morning', 'Afternoon',
                                        'Evening', 'Night'],
                                range=['#90EE90', '#FFD700',
                                       '#FF6B6B', '#4682B4']
                            )),
            tooltip=['period', 'hour', 'count']
        ).properties(
            title='Larceny Thefts by Hour and Time Period',
            width='container',
            height=400
        )

        # Create hour grid
        hour_grid = alt.Chart(pd.DataFrame({
            'hour': range(24)
        })).mark_rule(
            strokeDash=[2, 2],
            stroke='gray',
            strokeWidth=0.5,
            opacity=0.3
        ).encode(
            x='hour:O'
        )

        # Create period separators
        period_rules = alt.Chart(pd.DataFrame({
            'hour': [5, 12, 17, 21],
            'label': ['Morning', 'Afternoon', 'Evening', 'Night']
        })).mark_rule(
            strokeDash=[5, 5],
            stroke='white',
            strokeWidth=1,
            opacity=0.5
        ).encode(
            x='hour:O'
        )

        # Create period labels
        period_labels = alt.Chart(pd.DataFrame({
            'hour': [2, 8, 14, 19],
            'label': ['Night', 'Morning', 'Afternoon', 'Evening'],
            'y': [max(hourly_counts['count']) * 1.1] * 4
        })).mark_text(
            color='white',
            fontSize=12
        ).encode(
            x='hour:O',
            y='y:Q',
            text='label'
        )

        # Combine all layers
        final_chart = alt.layer(
            hour_grid,
            base_chart,
            period_rules,
            period_labels
        )

        # Calculate metrics
        total = hourly_counts['count'].sum()
        avg = total / 24
        peak_hour = hourly_counts.loc[hourly_counts['count'].idxmax()]
        lowest_hour = hourly_counts.loc[hourly_counts['count'].idxmin()]
        peak_time = f"{int(peak_hour['hour']):02d}:00 ({peak_hour['period']})"
        lowest_time = f"{int(lowest_hour['hour']):02d}:00 ({
            lowest_hour['period']})"

        return final_chart, total, avg, peak_time, lowest_time, "altair"
