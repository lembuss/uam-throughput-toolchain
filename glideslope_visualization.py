import matplotlib.pyplot as plt
import numpy as np
from parameters import Traffic, eVTOL
import functions
import math

def get_distance_from_rwythreshold(altitude, altitude_along_glideslope_ft, distance_to_runway_ft):
    distance_from_rwythreshold =  np.interp(altitude, altitude_along_glideslope_ft[::-1], distance_to_runway_ft[::-1])
    return distance_from_rwythreshold

end_distance_ft = 0 # Distance of the end point from rwy threshold

# Convert glide slope angle to radians
#glideslope_angle_rad = math.atan(Traffic.final_approach_fix_altitude_ft-Traffic.runway_elevation_ft)/(functions.convert_nm_to_ft(Traffic.final_approach_segment_nm))
glideslope_angle_rad = np.deg2rad(Traffic.glideslope_angle_deg)
# Create a range of distances from the starting point to the runway threshold
distance_to_runway_ft = np.linspace(functions.convert_nm_to_ft(Traffic.final_approach_segment_nm), end_distance_ft, 100)  # Change the range as needed

# Calculate the altitude along the glide slope using the formula: 
# Altitude = final_approach_fix_altitude_ft + (slope * distance)
slope = np.tan(glideslope_angle_rad)
altitude_along_glideslope_ft = Traffic.final_approach_fix_altitude_ft + (slope * (distance_to_runway_ft - functions.convert_nm_to_ft(Traffic.final_approach_segment_nm)))

# get distances from runway threshold
x_at_1000ft_separation = get_distance_from_rwythreshold(Traffic.start_separation_minima_altitude_ft, altitude_along_glideslope_ft, distance_to_runway_ft)
x_at_evtol_cruising_altitude = get_distance_from_rwythreshold(eVTOL.cruise_altitude_ft, altitude_along_glideslope_ft, distance_to_runway_ft)

start_separation_nm = functions.convert_ft_to_nm(x_at_1000ft_separation)
end_separation_nm = functions.convert_ft_to_nm(x_at_evtol_cruising_altitude)

print('Start of Separatio is at', start_separation_nm, ' nm from the Runway Threshold')
print('End of Separation is at', end_separation_nm, ' nm from the Runway Threshold')
# Create the graph
plt.figure(figsize=(8, 6))
plt.plot(distance_to_runway_ft, altitude_along_glideslope_ft, linestyle='-', color='b')

# Customize the plot
plt.title("Aircraft Glideslope During Instrument Approach on Runway 26L at Munich Airport")
plt.xlabel("Distance to Runway Threshold (ft)")
plt.ylabel("Altitude (ft)")
plt.grid(True)

# Add key control lines
plt.axhline(y=Traffic.runway_elevation_ft, color='r', linestyle='--', label='Runway Altitude')
plt.axhline(y=eVTOL.cruise_altitude_ft, color='r', linestyle='-.', label='eVTOL Cruising Altitude')
plt.axhline(y=Traffic.start_separation_minima_altitude_ft, color='r', linestyle=':', label='1000ft separation limit')

# plot vertical lines as well
plt.axvline(x=np.interp(Traffic.start_separation_minima_altitude_ft, altitude_along_glideslope_ft[::-1], distance_to_runway_ft[::-1]), 
            color='m', linestyle='--', label=f'Distance to RWY threshold at start of 1000ft separation limit')

plt.axvline(x=np.interp(eVTOL.cruise_altitude_ft, altitude_along_glideslope_ft[::-1], distance_to_runway_ft[::-1]), 
            color='m', linestyle='-.', label=f'Distance to RWY threshold at end of 1000ft separation limit')

# Show the graph
plt.legend()
plt.show()
