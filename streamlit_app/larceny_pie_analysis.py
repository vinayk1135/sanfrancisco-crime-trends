import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def create_larceny_pie_analysis(df):
    # Filter for larceny thefts
    larceny_df = df[df['incident_category'] == 'Larceny Theft']

    # Convert time to hour
    larceny_df['hour'] = pd.to_datetime(larceny_df['incident_time']).dt.hour

    # Count incidents by hour
    hourly_counts = larceny_df.groupby('hour').size()

    # Add color selector in sidebar
    st.sidebar.subheader("Customize Pie Chart")
    color_schemes = {
        # Night: dark blue, Morning: yellow, Afternoon: orange
        'Time of Day': ['#2C3E50', '#F1C40F', '#E67E22'],
        'Ocean': ['#034694', '#3498DB', '#1ABC9C'],  # Deep to light blues
        'Sunset': ['#6C3483', '#E74C3C', '#F39C12'],  # Purple to orange
        'Forest': ['#145A32', '#27AE60', '#58D68D']   # Dark to light green
    }

    # Add description of color meanings
    st.sidebar.markdown("""
    **Color Meanings:**
    - First color: Night (6pm-6am)
    - Second color: Morning (6am-12pm)
    - Third color: Afternoon (12pm-6pm)
    """)

    selected_scheme = st.sidebar.selectbox(
        "Color Scheme",
        options=list(color_schemes.keys())
    )

    # Calculate counts for three periods
    night_count = hourly_counts[(hourly_counts.index >= 18) | (
        hourly_counts.index < 6)].sum()
    morning_count = hourly_counts[(hourly_counts.index >= 6) & (
        hourly_counts.index < 12)].sum()
    afternoon_count = hourly_counts[(hourly_counts.index >= 12) & (
        hourly_counts.index < 18)].sum()

    # Create list of values and labels
    values = [night_count, morning_count, afternoon_count]
    labels = ['Night (6pm-6am)', 'Morning (6am-12pm)', 'Afternoon (12pm-6pm)']

    # Create pie chart using plotly
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0,
        marker_colors=color_schemes[selected_scheme],
        hovertemplate="<b>%{label}</b><br>" +
                      "Count: %{value:,.0f}<br>" +
                      "Percentage: %{percent}<br>" +
                      "<extra></extra>",  # Removes trace name from hover
        textposition='auto',
        textinfo='percent+label',
        texttemplate="%{label}<br>%{percent:.1%}",
        textfont=dict(size=14)
    )])

    # Update layout with new styling
    fig.update_layout(
        title={
            'text': "Larceny Theft Distribution by Time of Day",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        width=800,
        height=600,
        annotations=[{
            'text': f"Total Incidents: {sum(values):,}",
            'x': 0.5,
            'y': -0.3,
            'showarrow': False,
            'font': {'size': 16}
        }]
    )

    return fig, morning_count, afternoon_count, night_count
