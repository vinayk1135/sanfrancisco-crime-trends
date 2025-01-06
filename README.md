# San Francisco Property Crimes Data Visualization Tool

## Overview
The **San Francisco Property Crimes Data Visualization Tool** is an interactive platform designed to provide insights into property crimes in San Francisco. This tool focuses on various property crime types, such as theft, burglary, vandalism, and vehicle-related incidents, using comprehensive data visualization techniques. 

### Key Objectives:
- Improve public safety awareness.
- Assist city officials in addressing property crime through better resource allocation.
- Help law enforcement identify high-crime districts and deploy resources effectively.
- Enable citizens to stay informed and take precautions.

---

## Features
- **Crime Hotspot Mapping**: Identify neighborhoods with high levels of property crimes.
- **Trend Analysis**: Explore crime trends over time (monthly/yearly).
- **Time Analysis**: Detect specific times with higher crime activities.
- **Incident Reporting Gaps**: Analyze the average time gap between incidents and reporting.
- **User-Friendly Interface**: Intuitive visuals for all user groups.

---

## Target Users
1. **City Officials**: For resource allocation and crime prevention strategies.
2. **Law Enforcement**: To identify crime hotspots and deploy patrols.
3. **Citizens**: To stay informed about crime trends in their neighborhoods.

---

## Data Source
The project uses data provided by the San Francisco Police Department (SFPD) via the following dataset:
- [Police Department Incident Reports (2018 to Present)](https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783)

### Key Dataset Columns:
- **Incident Date**: Date and time of the incident.
- **Incident Category**: The type of property crime (e.g., theft, vandalism).
- **Police District**: District where the crime occurred.
- **Neighborhood**: Neighborhood location of the incident.
- **Resolution**: Status of the incident report (e.g., Open, Arrest, Unfounded).
- **Latitude & Longitude**: Geolocation of the incident.

For a full description of all columns, refer to the dataset's [metadata](https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783/about_data).

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/vinayk1135/sanfrancisco-crime-trends.git
   cd sanfrancisco-crime-trends
