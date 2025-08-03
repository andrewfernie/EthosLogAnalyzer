#!/usr/bin/env python3
"""
Test script for the new TkinterMapView implementation
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from display_2d_gps_data import display_2d_gps_data

def create_test_data():
    """Create some sample GPS data for testing"""
    # Create a simple rectangular path
    lats = [40.7589, 40.7589, 40.7489, 40.7489, 40.7589]  # NYC area
    lons = [-73.9851, -73.9751, -73.9751, -73.9851, -73.9851]
    
    # Create some additional points along the path
    all_lats = []
    all_lons = []
    
    for i in range(len(lats)-1):
        lat_start, lat_end = lats[i], lats[i+1]
        lon_start, lon_end = lons[i], lons[i+1]
        
        # Interpolate points between start and end
        for j in range(10):
            t = j / 9.0
            lat = lat_start + t * (lat_end - lat_start)
            lon = lon_start + t * (lon_end - lon_start)
            all_lats.append(lat)
            all_lons.append(lon)
    
    # Create DataFrame
    df = pd.DataFrame({
        'GPS.Latitude': all_lats,
        'GPS.Longitude': all_lons,
        'Time': range(len(all_lats))
    })
    
    return df

if __name__ == "__main__":
    print("Creating test GPS data...")
    test_df = create_test_data()
    print(f"Created {len(test_df)} GPS points")
    
    print("Launching 2D GPS display...")
    display_2d_gps_data(test_df, "test_data.csv")
    
    print("Test completed!")
