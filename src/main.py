"""
Main entry point for the Ethos Log Analyzer application. 

This application can be used to view and analyze log files recorded by FrSky radio control 
transmitters using the Ethos operating system. The log files are in CSV format and contain 
telemetry data such as GPS coordinates, battery voltage, current, and other flight parameters.
The specific data columns vary depending on the model setup and the sensors used.


MIT License

Copyright (c) 2025 Andrew Fernie

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import os
from tkinter import Label, Tk, Button
from load_log_file import load_log_file
from display_log_data import display_log_data
from display_2d_gps_data import display_2d_gps_data
from display_3d_gps_data import display_3d_gps_data
from create_kml_file import create_kml_file
from create_kml_file import view_kml_file
from export_processed_log_file import export_processed_log_file


def main():
    """
    Launches the Ethos Log Analyzer GUI application.

    This function loads a CSV log file then preprocesses the data (cleans up and calculates a few 
    derived data series). It then initializes the main Tkinter window, and provides buttons for 
    the user to:
      - Plot log data against time
      - Display GPS data as a 2D overlay on Open Street Map data (available if GPS columns are 
        present)
      - Display GPS data in a 3D plot (available if GPS and altitude columns are present)
      - Create a KML file for mapping (available if GPS columns are present)
      - View the generated KML file (available if GPS columns are present)
      - Export the processed (cleaned up) log file
      - Exit the application

    Button availability is determined by the presence of required columns in the loaded DataFrame.
    """

    df, filename, import_status = load_log_file()

    root = Tk()
    root.title("Ethos Log Analyzer")
    # Set minimum window size. It automatically resizes to fit the content, but doesn't look good
    # when too narrow, which happens with short filenames, and this prevents that from happening.
    root.minsize(275, 425)

    # Center the window
    root.eval('tk::PlaceWindow . center')

    # Main label
    Label(root, text=f'"{os.path.basename(filename)}" imported.\n' + import_status,
          font=("Arial", 12, "bold")).pack(pady=10)

    has_gps = {'GPS.Latitude', 'GPS.Longitude'}.issubset(df.columns)
    has_gps_with_altitude = {'GPS.Latitude',
                             'GPS.Longitude', 'GPS alt(m)'} .issubset(df.columns)

    Button(root, text="Display Log Data", width=20, height=2,
           command=lambda: display_log_data(df, filename)).pack(pady=5)

    btn_2d = Button(root, text="Display 2D GPS Data", width=20, height=2,
                    command=lambda: display_2d_gps_data(df, filename),
                    state="normal" if has_gps else "disabled")
    btn_2d.pack(pady=5)

    btn_3d = Button(root, text="Display 3D GPS Data", width=20, height=2,
                    command=lambda: display_3d_gps_data(df, filename),
                    state="normal" if has_gps_with_altitude else "disabled")
    btn_3d.pack(pady=5)

    btn_kml = Button(root, text="Create KML File", width=20, height=2,
                     command=lambda: create_kml_file(df, filename),
                     state="normal" if has_gps else "disabled")
    btn_kml.pack(pady=5)

    btn_view_kml = Button(root, text="View KML File", width=20, height=2,
                          command=lambda: view_kml_file(df, filename),
                          state="normal" if has_gps else "disabled")
    btn_view_kml.pack(pady=5)

    btn_export = Button(root, text="Export Processed Log File", width=20, height=2,
                        command=lambda: export_processed_log_file(df, filename))
    btn_export.pack(pady=5)

    Button(root, text="Exit", width=20, height=2, bg='lightcoral',
           command=root.quit).pack(pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
