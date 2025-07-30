"""
Module for displaying 2D GPS data from Ethos log files, preprocessed into DataFrames.

This module provides a function to plot GPS tracks on an interactive map using Plotly.
"""

import os
from tkinter import messagebox
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def display_2d_gps_data(df, filename):
    """
    Display a 2D map of GPS data using Plotly.

    This function plots the GPS track from the DataFrame on an interactive mapbox map,
    showing the path, start, and end points. It also displays basic statistics about the track.

    Args:
        df (pd.DataFrame): The DataFrame containing the log data, with 'GPS.Latitude' and 
        'GPS.Longitude' columns.

        filename (str): The name of the source file (for display purposes).

    Returns:
        None
    """
    if 'GPS.Latitude' in df.columns and 'GPS.Longitude' in df.columns:
        # Convert to numeric in case they are not
        lat = pd.to_numeric(df['GPS.Latitude'], errors='coerce')
        lon = pd.to_numeric(df['GPS.Longitude'], errors='coerce')

        # Remove any rows where lat or lon is NaN
        valid = ~(lat.isna() | lon.isna())
        lat = lat[valid]
        lon = lon[valid]

        # Calculate center point for map
        center_lat = lat.mean()
        center_lon = lon.mean()

        # Calculate zoom level based on GPS data spread
        lat_range = lat.max() - lat.min()
        lon_range = lon.max() - lon.min()
        max_range = max(lat_range, lon_range)

        # Estimate zoom level (rough approximation)
        if max_range > 1.0:
            zoom = 8
        elif max_range > 0.1:
            zoom = 12
        elif max_range > 0.01:
            zoom = 15
        else:
            zoom = 17

        # Create scatter points
        fig = px.scatter_mapbox(
            lat=lat,
            lon=lon,
            zoom=zoom,
            height=600,
            width=800,
            mapbox_style="open-street-map",
            title="2D GPS Data Overlay"
        )

        # Add line trace
        fig.add_trace(
            go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='lines',
                line=dict(width=2, color='blue'),
                name='Path'
            )
        )

        # Add marker for the first point (red)
        fig.add_trace(
            go.Scattermapbox(
                lat=[lat.iloc[0]],
                lon=[lon.iloc[0]],
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Start'
            )
        )

        # Add marker for the last point (green)
        fig.add_trace(
            go.Scattermapbox(
                lat=[lat.iloc[-1]],
                lon=[lon.iloc[-1]],
                mode='markers',
                marker=dict(size=12, color='green'),
                name='End'
            )
        )

       # Update map style and layout
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom
            ),
            title={
                'text': f"GPS Track - {os.path.basename(filename)}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255,255,255,0.8)"
            )
        )

        # Add annotations with statistics
        stats_text = f"""Points: {len(lat)} \n
        Lat : {lat.min():.6f}° - {lat.max():.6f}°
        Lon : {lon.min():.6f}° - {lon.max():.6f}°"""

        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.02, y=0.02,
            xanchor='left', yanchor='bottom',
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
            font=dict(size=10)
        )

        fig.show()
    else:
        messagebox.showerror(
            "Error", "GPS.Latitude and GPS.Longitude columns are required.")
