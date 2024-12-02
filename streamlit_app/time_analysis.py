import streamlit as st
import pandas as pd
import altair as alt


def create_time_analysis(df):
    # Convert incident_date to datetime
    df['date'] = pd.to_datetime(df['incident_date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.strftime('%Y-%m')  # Format: YYYY-MM

    # Add time granularity selector
    time_granularity = st.sidebar.radio(
        "Select Time Granularity",
        ["Yearly", "Monthly"],
        key="time_granularity"
    )

    # Add year navigation for monthly view
    if time_granularity == "Monthly":
        col1, col2, col3 = st.columns([1, 3, 1])
        min_year, max_year = df['year'].min(), df['year'].max()

        with col1:
            if st.button("← Previous Year"):
                if 'selected_year' in st.session_state:
                    st.session_state.selected_year = max(
                        min_year, st.session_state.selected_year - 1)

        with col2:
            if 'selected_year' not in st.session_state:
                st.session_state.selected_year = max_year
            st.subheader(f"Showing data for {st.session_state.selected_year}")

        with col3:
            if st.button("Next Year →"):
                if 'selected_year' in st.session_state:
                    st.session_state.selected_year = min(
                        max_year, st.session_state.selected_year + 1)

    # Add incident type selector
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type for Time Analysis",
        incident_options,
        key="time_analysis_radio"
    )

    # Filter data based on selection
    if selected_incident != 'All Types':
        df = df[df['incident_category'] == selected_incident]

    # Create aggregation based on selected granularity
    if time_granularity == "Monthly":
        # Filter for selected year and format months
        df = df[df['year'] == st.session_state.selected_year]
        # Add month number for proper sorting
        df['month_num'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')

        # Create monthly data with all months (even if no incidents)
        all_months = pd.DataFrame({
            'month_num': range(1, 13),
            'month_name': ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']
        })

        # Count incidents by month
        monthly_counts = df.groupby(
            ['month_num', 'month_name']).size().reset_index(name='count')

        # Merge with all months to include zeros for months with no incidents
        time_data = all_months.merge(
            monthly_counts, on=['month_num', 'month_name'], how='left')
        time_data['count'] = time_data['count'].fillna(0)

        # Sort by month number
        time_data = time_data.sort_values('month_num')
        x_field = 'month_name'
        title_suffix = f'Month ({st.session_state.selected_year})'
    else:
        time_data = df.groupby('year').size().reset_index(name='count')
        x_field = 'year'
        title_suffix = 'Year'

    # Calculate metrics
    total_incidents = time_data['count'].sum()
    avg_incidents = time_data['count'].mean()

    # Update peak period calculation
    if time_granularity == "Monthly":
        peak_row = time_data.loc[time_data['count'].idxmax()]
        peak_period = f"{peak_row['month_name']} ({int(peak_row['count']):,})"
    else:
        peak_period = str(time_data.loc[time_data['count'].idxmax(), x_field])

    # Update metrics display title in streamlit
    peak_metric_title = "Peak Month" if time_granularity == "Monthly" else "Peak Year"

    # Create chart
    base = alt.Chart(time_data).encode(
        x=alt.X(f'{x_field}:O',
                title=title_suffix,
                axis=alt.Axis(labelAngle=-45),
                # Add sort field for proper month ordering
                sort=None if time_granularity == "Yearly" else alt.SortField(
                    'month_num', order='ascending')),
        y=alt.Y('count:Q',
                title='Number of Incidents',
                scale=alt.Scale(zero=True)),
        tooltip=[
            alt.Tooltip(f'{x_field}:O', title=title_suffix),
            alt.Tooltip('count:Q', title='Incidents', format=',d'),
            # Add month number to tooltip for debugging
            alt.Tooltip('month_num:Q', title='Month #') if time_granularity == "Monthly" else alt.Tooltip(
                f'{x_field}:O', title=title_suffix)
        ]
    )

    # Create bars
    bars = base.mark_bar(color='#2196F3', opacity=0.8)

    # Add value labels
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=12
    ).encode(
        text=alt.Text('count:Q', format=',.0f')
    )

    # Add average line
    avg_rule = alt.Chart(pd.DataFrame({'y': [avg_incidents]})).mark_rule(
        strokeDash=[5, 5],
        color='red',
        strokeWidth=2
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='Average', format=',.0f')]
    )

    # Combine chart elements
    chart = (bars + text + avg_rule).properties(
        title=f'Incidents by {title_suffix} - {selected_incident}',
        width='container',
        height=500
    )

    return chart, total_incidents, avg_incidents, peak_period, selected_incident, peak_metric_title
