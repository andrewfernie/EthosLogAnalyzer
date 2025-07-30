"""
Module for creating and viewing KML files from Ethos log DataFrames.

This module provides functions to:
- Generate a KML file from a DataFrame containing GPS data.
- Create a temporary KML file and open it with the system's default application.
- Validate and structure GPS and optional altitude data for KML export.

Functions:
    create_kml_file(df, source_filename): Create and save a KML file from a DataFrame.
    view_kml_file(df, source_filename): Create and open a temporary KML file.
    create_kml_file_structure(df, source_filename, kml_filename): Build and write the KML structure.

Requires:
    - pandas
    - tkinter
    - xml.etree.ElementTree
"""

from tkinter import messagebox
import os

def create_kml_file(df, source_filename):
    """
    Create a KML file from the provided DataFrame and source filename.

    This function changes the extension of the source filename from .csv to .kml,
    generates the KML file using the DataFrame, and notifies the user upon success.

    Args:
        df (pd.DataFrame): The DataFrame containing the log data.
        source_filename (str): The original CSV filename.

    Returns:
        None
    """
    # Change extension from .csv to .kml
    base, _ = os.path.splitext(source_filename)
    kml_filename = base + ".kml"
    create_kml_file_structure(df, source_filename, kml_filename)
    messagebox.showinfo("Create KML File", f"KML file created: {kml_filename}")


def view_kml_file(df, source_filename):
    """
    Create a temporary KML file from the DataFrame and opens it with the default application.
    This will typically be Google Earth or similar program.

    This function generates a temporary KML file ("temp.kml") using the DataFrame,
    and attempts to open it using the operating system's default KML viewer.

    Args:
        df (pd.DataFrame): The DataFrame containing the log data.
        source_filename (str): The original CSV filename, used only as a reference in the KML file.

    Returns:
        None
    """
    # Create a temporary KML file
    temp_kml = "temp.kml"
    create_kml_file_structure(df, source_filename, temp_kml)
    # Open the KML file with the default application
    try:
        if os.name == 'nt':  # Windows
            os.startfile(temp_kml)
        elif os.name == 'posix':
            import subprocess
            subprocess.run(['xdg-open', temp_kml])
        else:
            messagebox.showinfo(
                "View KML File", f"Temporary KML file created: {temp_kml}")
    except Exception as e:
        messagebox.showerror("View KML File", f"Could not open KML file: {e}")


def create_kml_file_structure(df, source_filename, kml_filename):
    """
    Generate the KML file structure and write it to disk.

    This function validates the presence of required GPS columns, removes rows with missing 
    GPS data, and creates a KML file with placemarks for the start and end points, as well as 
    the flight path.

    Args:
        df (pd.DataFrame): The DataFrame containing the log data.
        source_filename (str): The original CSV filename.
        kml_filename (str): The output KML filename.

    Returns:
        bool: True if the file was created successfully, False otherwise.
    """
    try:
        import xml.etree.ElementTree as ET

        create_file_success = False

        if not {'GPS.Latitude', 'GPS.Longitude'}.issubset(df.columns):
            raise ValueError(
                "DataFrame must contain 'GPS.Latitude' and 'GPS.Longitude' columns.")

        # Check for altitude data
        alt_col_name = None
        for col in ['GPS alt (m)', 'GPS alt(m)', 'GPS.Altitude', 'Altitude']:
            if col in df:
                alt_col_name = col
                break

        # Remove rows with NaN in GPS columns
        gps_cols = ['GPS.Latitude', 'GPS.Longitude']
        if alt_col_name in df.columns:
            gps_cols.append(alt_col_name)

        df_valid = df.dropna(subset=gps_cols)

        # Check for DateTime data
        datetime_col_name = None
        if 'DateTime' in df_valid:
            datetime_col_name = 'DateTime'

        if len(df['GPS.Latitude']) == 0:
            messagebox.showerror(
                "Error", "No valid GPS data found for KML creation!")
            return

        # Create KML structure
        kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        document = ET.SubElement(kml, 'Document')

        # Add document name and description
        name = ET.SubElement(document, 'name')
        name.text = "Flight Track"

        description = ET.SubElement(document, 'description')
        description.text = f"GPS track exported from log file {os.path.basename(source_filename)}"\
            f" by EthosLogAnalyzer"

        # Add style for the track line
        style = ET.SubElement(document, 'Style', id="trackStyle")
        linestyle = ET.SubElement(style, 'LineStyle')
        color = ET.SubElement(linestyle, 'color')
        color.text = "ff0000ff"  # Red line in KML format (AABBGGRR)
        width = ET.SubElement(linestyle, 'width')
        width.text = "3"

        # Add style for start point
        start_style = ET.SubElement(document, 'Style', id="startStyle")
        iconstyle = ET.SubElement(start_style, 'IconStyle')
        icon = ET.SubElement(iconstyle, 'Icon')
        href = ET.SubElement(icon, 'href')
        href.text = "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png"

        # Add style for end point
        end_style = ET.SubElement(document, 'Style', id="endStyle")
        iconstyle = ET.SubElement(end_style, 'IconStyle')
        icon = ET.SubElement(iconstyle, 'Icon')
        href = ET.SubElement(icon, 'href')
        href.text = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"

        # Create placemark for start point
        start_placemark = ET.SubElement(document, 'Placemark')
        start_name = ET.SubElement(start_placemark, 'name')
        start_name.text = "Start"
        start_desc = ET.SubElement(start_placemark, 'description')

        start_desc.text = f"Flight start point\\nLat: {df_valid['GPS.Latitude'].iloc[0]}\\nLon:"\
            f" {df_valid['GPS.Longitude'].iloc[0]}"
        if alt_col_name is not None:
            start_desc.text += f"\\nAlt: {df_valid[alt_col_name].iloc[0]}m"

        start_styleurl = ET.SubElement(start_placemark, 'styleUrl')
        start_styleurl.text = "#startStyle"

        start_point = ET.SubElement(start_placemark, 'Point')
        start_coords = ET.SubElement(start_point, 'coordinates')
        if alt_col_name is not None:
            start_coords.text = f"{df_valid['GPS.Longitude'].iloc[0]},"\
                f"{df_valid['GPS.Latitude'].iloc[0]},{df_valid[alt_col_name].iloc[0]}"
        else:
            start_coords.text = f"{df_valid['GPS.Longitude'].iloc[0]},"\
                f"{df_valid['GPS.Latitude'].iloc[0]},0"

        # Create placemark for end point
        end_placemark = ET.SubElement(document, 'Placemark')
        end_name = ET.SubElement(end_placemark, 'name')
        end_name.text = "End"
        end_desc = ET.SubElement(end_placemark, 'description')
        end_desc.text = f"Flight end point\\nLat: {df_valid['GPS.Latitude'].iloc[-1]}\\n"\
            f"Lon: {df_valid['GPS.Longitude'].iloc[-1]}"
        if alt_col_name is not None:
            end_desc.text += f"\\nAlt: {df_valid[alt_col_name].iloc[-1]}m"

        end_styleurl = ET.SubElement(end_placemark, 'styleUrl')
        end_styleurl.text = "#endStyle"

        end_point = ET.SubElement(end_placemark, 'Point')
        end_coords = ET.SubElement(end_point, 'coordinates')
        if alt_col_name is not None:
            end_coords.text = f"{df_valid['GPS.Longitude'].iloc[-1]},"\
                f"{df_valid['GPS.Latitude'].iloc[-1]},{df_valid[alt_col_name].iloc[-1]}"
        else:
            end_coords.text = f"{df_valid['GPS.Longitude'].iloc[-1]},"\
                "{df_valid['GPS.Latitude'].iloc[-1]},0"

        # Create placemark for the track
        track_placemark = ET.SubElement(document, 'Placemark')
        track_name = ET.SubElement(track_placemark, 'name')
        track_name.text = "Flight Path"

        track_desc = ET.SubElement(track_placemark, 'description')
        track_desc.text = f"""Flight track with {len(df_valid['GPS.Latitude'])} GPS points
Altitude data: {'Yes' if alt_col_name is not None else 'No'}
Timestamp data: {'Yes' if datetime_col_name is not None else 'No'}"""

        track_styleurl = ET.SubElement(track_placemark, 'styleUrl')
        track_styleurl.text = "#trackStyle"

        # Create LineString for the track
        linestring = ET.SubElement(track_placemark, 'LineString')

        # Set altitude mode
        altmode = ET.SubElement(linestring, 'altitudeMode')
        altmode.text = "absolute" if alt_col_name is not None else "clampToGround"

        # Create coordinates string
        coords_list = []
        for i in range(len(df_valid['GPS.Latitude'])):
            if alt_col_name is not None:
                coords_list.append(
                    f"{df_valid['GPS.Longitude'].iloc[i]},{df_valid['GPS.Latitude'].iloc[i]},"\
                        f"{df_valid[alt_col_name].iloc[i]}")
            else:
                coords_list.append(
                    f"{df_valid['GPS.Longitude'].iloc[i]},{df_valid['GPS.Latitude'].iloc[i]},0")

        coordinates = ET.SubElement(linestring, 'coordinates')
        coordinates.text = ' '.join(coords_list)

        # Create the tree and write to file
        tree = ET.ElementTree(kml)
        ET.indent(tree, space="  ", level=0)  # Pretty print formatting

        # Write KML file with XML declaration
        with open(kml_filename, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)

        create_file_success = True
        print(f"KML file saved: {kml_filename}")

    except Exception as e:
        messagebox.showerror("Error", f"Error creating KML file:\n{e}")
        print(f"KML creation error: {e}")
        create_file_success = False

    return create_file_success
