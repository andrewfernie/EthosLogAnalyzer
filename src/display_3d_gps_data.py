"""
Module for displaying 3D GPS data from Ethos log DataFrames.

This module provides a function to plot 3D GPS tracks using matplotlib.
"""
import os
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt

def display_3d_gps_data(df, filename):
    """
    Display a 3D plot of GPS data using matplotlib.

    This function plots the GPS track from the DataFrame in 3D (longitude, latitude, altitude),
    showing the path and coloring points by altitude.

    Args:
        df (pd.DataFrame): The DataFrame containing the log data, with 'GPS.Latitude', 
            'GPS.Longitude', and 'GPS alt(m)' columns.
        filename (str): The name of the source file (for display purposes).

    Returns:
        None
    """
    if all(col in df.columns for col in ['GPS.Latitude', 'GPS.Longitude', 'GPS alt(m)']):
        lat = pd.to_numeric(df['GPS.Latitude'], errors='coerce')
        lon = pd.to_numeric(df['GPS.Longitude'], errors='coerce')
        alt = pd.to_numeric(df['GPS alt(m)'], errors='coerce')

        # Remove any rows where lat, lon, or alt is NaN
        valid = ~(lat.isna() | lon.isna() | alt.isna())
        lat = lat[valid]
        lon = lon[valid]
        alt = alt[valid]

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(lon, lat, alt, color='blue', label='Path')
        ax.scatter(lon, lat, alt, c=alt, cmap='viridis', s=20)

        ax.set_title(f"3D GPS Data - {os.path.basename(filename)}")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Altitude (m)')
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showerror("Error", "Required columns: GPS.Latitude, GPS.Longitude,"\
                             " and GPS alt (m) are missing.")
        