#!/usr/bin/env python3
"""
Test script to diagnose TkinterMapView issues
"""

import tkinter as tk
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import tkintermapview
    print(f"TkinterMapView imported successfully")
    print(f"Version: {tkintermapview.__version__}")
except ImportError as e:
    print(f"Failed to import TkinterMapView: {e}")
    sys.exit(1)

def test_map():
    """Test basic map functionality"""
    root = tk.Tk()
    root.title("Map Test")
    root.geometry("800x600")
    
    # Create status label
    status_label = tk.Label(root, text="Initializing map...", fg="blue")
    status_label.pack(pady=5)
    
    try:
        # Create map widget
        map_widget = tkintermapview.TkinterMapView(root, width=780, height=550)
        map_widget.pack(pady=10)
        
        # Set explicit tile server
        map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", max_zoom=22)
        
        # Set a test location (New York City)
        map_widget.set_position(40.7589, -73.9851)
        map_widget.set_zoom(12)
        
        # Add a test marker
        map_widget.set_marker(40.7589, -73.9851, text="Test Location")
        
        # Update status
        def update_status():
            status_label.config(text="Map should be visible now. If not, there may be network issues.", fg="green")
        
        root.after(3000, update_status)
        
        print("Map widget created successfully")
        status_label.config(text="Map widget created. Loading tiles...", fg="orange")
        
    except Exception as e:
        print(f"Error creating map widget: {e}")
        status_label.config(text=f"Error: {e}", fg="red")
    
    root.mainloop()

if __name__ == "__main__":
    print("Testing TkinterMapView...")
    test_map()
