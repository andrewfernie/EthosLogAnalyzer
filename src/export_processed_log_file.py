"""
Module for exporting processed Ethos log DataFrames to CSV files.

Functions:
    export_processed_log_file(df, original_filename): Prompts the user to select a location and filename for saving the processed log data.
"""

import os
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
import pandas as pd

def export_processed_log_file(df, original_filename):
    """
    Export the processed DataFrame to a new CSV file.

    Prompts the user to select a location and filename for saving the processed log data.

    Args:
        df (pd.DataFrame): The processed DataFrame to export.
        original_filename (str): The original filename, used to suggest a default name.

    Returns:
        None
    """
    save_filename = asksaveasfilename(defaultextension=".csv",
                                      initialfile=f"processed_{os.path.basename(original_filename)}",
                                      filetypes=[("CSV files", "*.csv")])
    if save_filename:
        df.to_csv(save_filename, index=False)
        messagebox.showinfo("Export Complete", f"Processed log file saved to:\n{save_filename}")