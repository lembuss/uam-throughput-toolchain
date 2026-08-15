import requests
import pandas as pd

# Constants
OPENSKY_API_URL = 'https://opensky-network.org/api/states/all'

def fetch_live_flight_data():
    try:
        # Make the request to the OpenSky API
        response = requests.get(OPENSKY_API_URL)
        response.raise_for_status()  # Raise an error if the request failed

        # Parse the response JSON
        data = response.json()

        # Convert the response to a DataFrame
        columns = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact',
                   'longitude', 'latitude', 'baro_altitude', 'on_ground', 'velocity',
                   'true_track', 'vertical_rate', 'sensors', 'geo_altitude', 'squawk',
                   'spi', 'position_source', 'aircraft_type']

        # The 'aircraft_type' is not provided directly; placeholder for potential lookup

        flights = pd.DataFrame(data['states'], columns=columns[:-1])
        flights['aircraft_type'] = None  # Placeholder for the actual aircraft type

        return flights

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def main():
    flights_df = fetch_live_flight_data()
    if flights_df is not None:
        # Saving to an Excel file
        flights_df.to_excel('live_flight_data.xlsx', index=False)
        print("Flight data written to live_flight_data.xlsx")

if __name__ == "__main__":
    main()
