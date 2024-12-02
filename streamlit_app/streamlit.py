import streamlit as st
import pandas as pd
import altair as alt
import os
import plotly.graph_objects as go
from time_analysis import create_time_analysis
from parallel_time_analysis import create_parallel_time_analysis
from day_of_week_analysis import create_day_of_week_analysis, create_day_of_week_bar_analysis
from week_bar_analysis import create_week_bar_analysis
from larceny_time_analysis import create_larceny_analysis
from larceny_analysis import create_larceny_analysis
from larceny_pie_analysis import create_larceny_pie_analysis
from map_analysis import create_map_analysis
from district_map_analysis import create_district_map_analysis

# Must be the first Streamlit command
st.set_page_config(layout="wide")


def load_data():
    """Load the CSV file from the current directory."""
    try:
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if not csv_files:
            st.error("No CSV files found in the current directory!")
            return None
        df = pd.read_csv('clean_dataset.csv')  # Use specific file for now
        st.sidebar.success(f"Data loaded successfully")
        return df
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return None


def create_top_categories_chart(df):
    # Create DataFrame of top incident categories
    df_categories = pd.DataFrame(
        df.incident_category.value_counts().reset_index())
    df_categories.columns = ['incident_category', 'count']

    # Get top N categories based on user selection
    top_n = st.sidebar.slider("Number of categories to display", 5, 20, 10)
    top_categories = df_categories.head(top_n)

    # Calculate averages
    top_n_avg = top_categories['count'].mean()
    total_avg = df_categories['count'].mean()

    # Create Altair chart
    base = alt.Chart(top_categories).encode(
        x=alt.X('incident_category:N',
                sort='-y',
                axis=alt.Axis(
                    title='Incident Categories',
                    labelAngle=-45,
                    labelOverlap=False,  # Prevent label overlap handling
                    labelLimit=0  # Remove text truncation
                )),
        y=alt.Y('count:Q', title='Count'),
        color=alt.condition(
            # Fixed condition
            f"datum.count == {top_categories['count'].max()}",
            alt.value('red'),  # Color for highest bar
            alt.value('#ffcccb')  # Light red for other bars
        )
    )

    # Bars with custom opacity
    bars = base.mark_bar(opacity=0.8)

    # Add value labels on top of bars
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text=alt.Text('count:Q', format='.0f')
    )

    # Add average lines with enhanced visibility
    top_n_rule = alt.Chart(pd.DataFrame({'y': [top_n_avg]})).mark_rule(
        strokeDash=[5, 5],
        color='white',
        strokeWidth=2,
        opacity=0.8
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='Top N Average', format='.0f')]
    )

    total_rule = alt.Chart(pd.DataFrame({'y': [total_avg]})).mark_rule(
        strokeDash=[3, 3],
        color='red',
        strokeWidth=2,
        opacity=0.8
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='Total Average', format='.0f')]
    )

    # Combine all chart elements
    chart = (bars + text + top_n_rule + total_rule).properties(
        title=f'Top {top_n} Incident Categories (2018-Present)',
        width='container',
        height=500
    )

    return chart


def create_neighborhood_analysis(df):
    # Add incident type selector in sidebar
    incident_options = ['All Types', 'Larceny Theft', 'Motor Vehicle Theft',
                        'Assault', 'Burglary', 'Robbery']
    selected_incident = st.sidebar.radio(
        "Select Incident Type", incident_options)

    # Filter data based on selection
    if selected_incident != 'All Types':
        df = df[df['incident_category'] == selected_incident]

    # Create DataFrame of police districts
    df_districts = pd.DataFrame(
        df.police_district.value_counts().reset_index())
    df_districts.columns = ['police_district', 'count']

    # Calculate statistics
    district_avg = df_districts['count'].mean()
    max_district = df_districts.iloc[0]['police_district']
    min_district = df_districts.iloc[-1]['police_district']

    # Create Altair chart
    base = alt.Chart(df_districts).encode(
        x=alt.X('police_district:N',
                sort='-y',
                axis=alt.Axis(
                    title='Police Districts',
                    labelAngle=-45
                )),
        y=alt.Y('count:Q', title='Number of Incidents'),
        color=alt.condition(
            f"datum.count == {df_districts['count'].max()}",
            alt.value('#1f77b4'),  # Blue for highest
            alt.value('#aec7e8')  # Light blue for others
        )
    )

    # Bars
    bars = base.mark_bar()

    # Value labels
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text=alt.Text('count:Q', format='.0f')
    )

    # Average line
    avg_rule = alt.Chart(pd.DataFrame({'y': [district_avg]})).mark_rule(
        strokeDash=[5, 5],
        color='red',
        strokeWidth=2
    ).encode(
        y='y',
        tooltip=[alt.Tooltip('y', title='District Average', format='.0f')]
    )

    # Combine chart elements
    chart = (bars + text + avg_rule).properties(
        title=f'Incidents by Police District - {selected_incident}',
        width='container',
        height=500
    )

    return chart, max_district, min_district, district_avg, selected_incident


def create_time_based_analysis(df):
    """Time-based analysis of incidents"""
    chart, total, yearly_avg, peak_period, incident_type, peak_metric_title = create_time_analysis(
        df)
    st.altair_chart(chart, use_container_width=True)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", f"{int(total):,}")
    with col2:
        st.metric("Average per Period", f"{int(yearly_avg):,}")
    with col3:
        st.metric(peak_metric_title, peak_period)
    with col4:
        st.metric("Incident Type", incident_type)


def create_parallel_view(df):
    """Parallel coordinates view of time-based analysis"""
    chart, total, avg, peak_year, incident_type = create_parallel_time_analysis(
        df)
    st.altair_chart(chart, use_container_width=True)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", f"{int(total):,}")
    with col2:
        st.metric("Average per Year", f"{int(avg):,}")
    with col3:
        st.metric("Peak Year", str(peak_year))
    with col4:
        st.metric("Incident Type", incident_type)


def main():
    st.title("Analyzing Property Crime Trends Across San Francisco Neighborhoods")

    # Load data
    df = load_data()

    if df is not None:
        # Sidebar visualization selector
        st.sidebar.header("Visualization Options")
        viz_option = st.sidebar.selectbox(
            "Select Visualization Type",
            ["Top Categories Analysis",
             "Neighborhood Analysis",
             "Time-based Analysis",
             "Parallel Time View",
             "Day of Week Analysis",
             "Week Bar Analysis",
             "Time of the Day Analysis",
             "Larceny Day/Night Analysis",
             "Incident Map",
             "District Map Analysis"]  # Add new option
        )

        # Display selected visualization
        if viz_option == "Top Categories Analysis":
            chart = create_top_categories_chart(df)
            st.altair_chart(chart, use_container_width=True)

            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Top Categories Average",
                          f"{int(df.incident_category.value_counts().head(10).mean())}")
            with col2:
                st.metric("Overall Average",
                          f"{int(df.incident_category.value_counts().mean())}")

        elif viz_option == "Neighborhood Analysis":
            chart, max_district, min_district, district_avg, incident_type = create_neighborhood_analysis(
                df)
            st.altair_chart(chart, use_container_width=True)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Most Active District", max_district)
            with col2:
                st.metric("Least Active District", min_district)
            with col3:
                st.metric("Average Incidents", f"{int(district_avg)}")
            with col4:
                st.metric("Incident Type", incident_type)

        elif viz_option == "Time-based Analysis":
            create_time_based_analysis(df)

        elif viz_option == "Parallel Time View":
            create_parallel_view(df)

        elif viz_option == "Day of Week Analysis":
            fig, total, avg, peak_day, lowest_day, counts = create_day_of_week_analysis(
                df)
            st.plotly_chart(fig, use_container_width=True)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Incidents", f"{int(total):,}")
            with col2:
                st.metric("Daily Average", f"{int(avg):,}")
            with col3:
                st.metric("Peak Day", peak_day)
            with col4:
                st.metric("Lowest Day", lowest_day)

        elif viz_option == "Day of Week Bar Chart":
            chart, total, avg, peak_day, lowest_day = create_day_of_week_bar_analysis(
                df)
            st.altair_chart(chart, use_container_width=True)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Incidents", f"{int(total):,}")
            with col2:
                st.metric("Daily Average", f"{int(avg):,}")
            with col3:
                st.metric("Peak Day", peak_day)
            with col4:
                st.metric("Lowest Day", lowest_day)

        elif viz_option == "Week Bar Analysis":
            chart, total, avg, peak_day, lowest_day = create_week_bar_analysis(
                df)
            st.altair_chart(chart, use_container_width=True)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Incidents", f"{int(total):,}")
            with col2:
                st.metric("Daily Average", f"{int(avg):,}")
            with col3:
                st.metric("Peak Day", peak_day)
            with col4:
                st.metric("Lowest Day", lowest_day)

        elif viz_option == "Time of the Day Analysis":
            # Add visualization type selector
            viz_type = st.sidebar.radio(
                "Select Visualization Type",
                ["Line Chart", "Grid Chart"]
            )

            # Create visualization based on selection
            result = create_larceny_analysis(
                df,
                "line" if viz_type == "Line Chart" else "grid"
            )

            chart, total, avg, peak_time, lowest_time, chart_type = result

            # Display chart based on its type
            if chart_type == "plotly":
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.altair_chart(chart, use_container_width=True)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Incidents", f"{int(total):,}")
            with col2:
                st.metric("Hourly Average", f"{int(avg):,}")
            with col3:
                st.metric("Peak Time", peak_time)
            with col4:
                st.metric("Lowest Time", lowest_time)

        elif viz_option == "Larceny Day/Night Analysis":
            fig, morning_count, afternoon_count, night_count = create_larceny_pie_analysis(
                df)
            st.plotly_chart(fig, use_container_width=True)

            # Display metrics
            total = morning_count + afternoon_count + night_count
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Morning (6am-12pm)", f"{int(morning_count):,}")
            with col2:
                st.metric("Afternoon (12pm-6pm)", f"{int(afternoon_count):,}")
            with col3:
                st.metric("Night (6pm-6am)", f"{int(night_count):,}")
            with col4:
                st.metric("Total Incidents", f"{int(total):,}")

        elif viz_option == "Incident Map":
            total_incidents, unique_locations, incident_type = create_map_analysis(
                df)

            # Display metrics below map
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Incidents", f"{total_incidents:,}")
            with col2:
                st.metric("Unique Locations", f"{unique_locations:,}")
            with col3:
                st.metric("Incident Type", incident_type)

        elif viz_option == "District Map Analysis":
            total_incidents, num_districts, busiest_district = create_district_map_analysis(
                df)

            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Incidents", f"{total_incidents:,}")
            with col2:
                st.metric("Number of Districts", num_districts)
            with col3:
                st.metric("Busiest District", busiest_district)


if __name__ == '__main__':
    main()
