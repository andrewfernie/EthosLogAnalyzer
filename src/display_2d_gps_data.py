"""
Module for displaying 2D GPS data from Ethos log files, preprocessed into DataFrames.

This module provides a function to plot GPS tracks on an interactive map using TkinterMapView.
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import tkintermapview


def display_2d_gps_data(df, filename):
    """
    Display a 2D map of GPS data using TkinterMapView.

    This function plots the GPS track from the DataFrame on an interactive map widget,
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

        if len(lat) == 0:
            messagebox.showerror("Error", "No valid GPS coordinates found.")
            return

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

        # Create the main window
        map_window = tk.Toplevel()
        map_window.title(f"GPS Track - {os.path.basename(filename)}")
        map_window.geometry("1000x700")

        # Create a frame for the map and info
        main_frame = ttk.Frame(map_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create info frame for statistics
        info_frame = ttk.LabelFrame(main_frame, text="Track Statistics")
        info_frame.pack(fill=tk.X, pady=(0, 5))

        # Display statistics
        stats_text = ""
        stats_text += f"Date: {df['Date'].iloc[0]} | T0: {df['Time'].iloc[0]} | Duration: {df['ElapsedTime'].iloc[-1] - df['ElapsedTime'].iloc[0]:.1f}s\n"
        stats_text += f"Points: {len(lat)} | Lat: {lat.min():.6f}° - {lat.max():.6f}° | Lon: {lon.min():.6f}° - {lon.max():.6f}°"
        stats_label = ttk.Label(info_frame, anchor=tk.CENTER, justify=tk.CENTER, text=stats_text)
        stats_label.pack(pady=5)
    
        # Create a control frame for map controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Add center on track button
        def center_on_track():
            map_widget.set_position(center_lat, center_lon)
            map_widget.set_zoom(zoom)
        
        ttk.Button(control_frame, text="Center on Track", 
                  command=center_on_track).pack(side=tk.LEFT, padx=2)

        # Add map type selector
        ttk.Label(control_frame, text="Map Type:").pack(side=tk.LEFT, padx=(20, 5))
        map_type_var = tk.StringVar(value="OpenStreetMap")
        map_type_combo = ttk.Combobox(control_frame, textvariable=map_type_var, 
                                    values=["OpenStreetMap", "Google Map", "Google Satellite"], 
                                    state="readonly", width=18)
        map_type_combo.pack(side=tk.LEFT, padx=2)
        
        def change_map_type(event=None):
            selected = map_type_var.get()
            try:
                if selected == "OpenStreetMap":
                    map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=22)
                elif selected == "OpenStreetMap DE":
                    map_widget.set_tile_server("https://tile.openstreetmap.de/{z}/{x}/{y}.png", max_zoom=22)
                elif selected == "CartoDB":
                    map_widget.set_tile_server("https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png", max_zoom=22)
                elif selected == "OpenTopoMap":
                    map_widget.set_tile_server("https://a.tile.opentopomap.org/{z}/{x}/{y}.png", max_zoom=17)
                elif selected == "Google Map":
                    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
                elif selected == "Google Satellite":
                    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
                
                # Force refresh after changing tile server
                current_zoom = map_widget.zoom
                map_widget.set_zoom(current_zoom + 1)
                map_widget.after(100, lambda: map_widget.set_zoom(current_zoom))
                
            except Exception as e:
                error_label = ttk.Label(main_frame, text=f"Error changing map type: {str(e)}", foreground="red")
                error_label.pack(pady=10)

        map_type_combo.bind("<<ComboboxSelected>>", change_map_type)

    # Create the map widget
        try:
            map_widget = tkintermapview.TkinterMapView(main_frame, width=990, height=600, corner_radius=0)
            map_widget.pack(fill=tk.BOTH, expand=True)
           
            # Set the first tile server
            change_map_type()
            
            # Set the position and zoom
            map_widget.set_position(center_lat, center_lon)
            map_widget.set_zoom(zoom)
            
        except Exception as e:
            # Fallback if there are issues with the map widget
            error_label = ttk.Label(main_frame, text=f"Error creating map widget: {str(e)}", foreground="red")
            error_label.pack(pady=10)

        # Create path coordinates list
        path_coordinates = list(zip(lat.tolist(), lon.tolist()))

        # Add the GPS track as a path
        if len(path_coordinates) > 1:
            map_widget.set_path(path_coordinates, color="blue", width=3)

        # Add start marker (red)
        start_marker = map_widget.set_marker(lat.iloc[0], lon.iloc[0], 
                                           text="Start", 
                                           marker_color_circle="red",
                                           marker_color_outside="darkred")

        # Add end marker (green)
        end_marker = map_widget.set_marker(lat.iloc[-1], lon.iloc[-1], 
                                         text="End", 
                                         marker_color_circle="green",
                                         marker_color_outside="darkgreen")

        
        main_frame.mainloop()

    else:
        messagebox.showerror(
            "Error", "GPS.Latitude and GPS.Longitude columns are required.")
