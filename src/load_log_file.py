"""
Module for loading and preprocessing Ethos log CSV files.

This module provides a function to prompt the user to select a CSV file, import it as a pandas 
DataFrame, and perform preprocessing steps on the data.

Functions:
    load_log_file(): Prompts the user to select a CSV file, loads and preprocesses it, and 
    returns the DataFrame and filename.
"""

from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime
import re
import pandas as pd
from pyproj import Proj


def load_log_file():
    """
    Prompts the user to select a CSV log file, loads it into a pandas DataFrame, and preprocesses 
    the data.

    Preprocessing steps include:
    - Removing empty columns
    - Handling potentially missing 'Date' and 'Time' columns by generating them if necessary
    - Combining 'Date' and 'Time' into a 'DateTime' column
    - Calculating 'ElapsedTime' from 'DateTime' as an offset from the first timestamp
    - Splitting 'GPS' column into 'GPS.Latitude' and 'GPS.Longitude' if present
    - Computing 'GPS.X(m)' and 'GPS.Y(m)' as excursions in meters from the center GPS point using 
        pyproj (WGS84)
    - Computing 'Power (W)' if 'VFAS(V)' and 'Current(A)' columns are present
    - Summing all 'LiPoN (V)' columns into 'LiPo Total (V)' if present
    - Sorting columns alphabetically

    Returns:
        tuple: (df, filename)
            df (pd.DataFrame): The preprocessed DataFrame.
            filename (str): The path to the loaded CSV file.

    Raises:
        FileNotFoundError: If no file is selected.
    """
    Tk().withdraw()  # Prevents the root window from appearing
    filename = askopenfilename(filetypes=[("CSV files", "*.csv")])

    import_status=""

    if filename:
        df = pd.read_csv(filename)

        # Remove empty columns
        df = df.dropna(axis=1, how='all')

        # Split GPS column if present
        if 'GPS' in df.columns:
            gps_split = df['GPS'].str.split(' ', expand=True)
            df['GPS.Latitude'] = gps_split[0]
            df['GPS.Longitude'] = gps_split[1]
            df = df.drop(columns=['GPS'])

        # Compute X/Y excursions in meters from center GPS point if GPS columns exist
        if 'GPS.Longitude' in df.columns and 'GPS.Latitude' in df.columns:
            # Convert to float in case they are strings
            df['GPS.LongitudeFloat'] = df['GPS.Longitude'].astype(float)
            df['GPS.LatitudeFloat'] = df['GPS.Latitude'].astype(float)
            lon0 = df['GPS.LongitudeFloat'].mean()
            lat0 = df['GPS.LatitudeFloat'].mean()
            # Use pyproj for accurate projection (WGS84)
            proj = Proj(proj='aeqd', lat_0=lat0, lon_0=lon0, datum='WGS84')
            x, y = proj(df['GPS.LongitudeFloat'].values,
                        df['GPS.LatitudeFloat'].values)
            df['GPS.X(m)'] = x
            df['GPS.Y(m)'] = y
            df = df.drop(columns=['GPS.LatitudeFloat', 'GPS.LongitudeFloat'])
            import_status += "Contains GPS data.\n"
        else:
            import_status += "No GPS data found.\n"

        # The files from the radio should have Date and Time columns, and this application will
        # combine them into a DateTime column for more convenient processing. However, if the file
        # being opened is one that was previously processed and exported from this application
        # then the DateTime column will already exist, and there is no need to regenerate it.
        if not 'DateTime' in df.columns:
            # There was no DateTime column, so we need to create one. If either Date or Time is missing,
            # we will generate one. The generated data won't be accurate, but at least it allows the various
            # data series to be plotted.
            if 'Time' in df.columns:
                # Ensure 'Time' is in HH:MM:SS.f format (with one or more "f" digits). The typical problem
                # is that if the file has gone through Excel and HH should have been '12' it may have
                # been dropped and we only have MM:SS.f format with an implied '12:' at the front. If so,
                # we prepend '12:' to the time.
                if not re.match(r'^\d{1,2}:\d{2}:\d{2}\.\d+$', df['Time'].iloc[0]):
                    print(
                        "Warning: 'Time' column format is not HH:MM:SS.f. Prepending '12:' to the time values.")
                    df['Time'] = '12:' + df['Time'].astype(str)
            else:
                # If no Time column, generate one assuming start at 12:00:00 and 1 second between each sample
                start_time = datetime.strptime("12:00:00.0", "%H:%M:%S.%f")
                df['Time'] = [(start_time + pd.Timedelta(seconds=i)
                               ).strftime("%H:%M:%S.%f")[:-3] for i in range(len(df))]
                print(f"Warning: 'Time' column not found. Using generated time values starting at 12:00:00.0"
                      " with 1 second intervals.")
                import_status += "No time data found.\n"

            if not 'Date' in df.columns:
                # If only Time is present, use current date
                current_date = datetime.now().strftime('%Y-%m-%d')
                print(
                    f"Warning: 'Date' column not found. Using current date: {current_date}")
                df['Date'] = current_date
                import_status += "No date data found.\n"


            # At this point we should have both Date and Time columns, either from the file or generated.
            df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' +
                                            df['Time'].astype(str),
                                            errors='coerce')

            # Calculate ElapsedTime as an offset from the first DateTime
            if not df['DateTime'].isnull().all():
                first_time = df['DateTime'].iloc[0]
                df['ElapsedTime'] = (
                    df['DateTime'] - first_time).dt.total_seconds()
            else:
                df['ElapsedTime'] = None

        # Compute Power (W) if VFAS(V) and Current(A) are present
        if 'VFAS(V)' in df.columns and 'Current(A)' in df.columns:
            df['Power (W)'] = df['VFAS(V)'] * df['Current(A)']
            import_status += "Generated 'Power (W)' data.\n"

        # Compute LiPo Total (V) if any LiPo? (V) columns exist
        lipo_cols = [col for col in df.columns if re.match(
            r"LiPo\d+\(V\)", col)]
        if lipo_cols:
            df['LiPo Total (V)'] = df[lipo_cols].sum(axis=1)
            import_status += "Generated 'LiPo Total (V)' data.\n"

        # Sort columns alphabetically
        df = df[sorted(df.columns)]

        print(f"File '{filename}' imported successfully.")
        return df, filename, import_status
    else:
        raise FileNotFoundError("No file selected.")
